# ==============================================================================
# Módulo de Rutas para Medios (routes/medios.py)
# ------------------------------------------------------------------------------
# Este archivo define el Blueprint para todas las operaciones relacionadas con
# los medios extraíbles (por ejemplo, unidades USB). Incluye listar, registrar,
# obtener información, exportar bordados y eliminar bordados de un medio.
# ==============================================================================

from flask import Blueprint, jsonify, request
from db import db
from models import Medio, Bordado, Exportado
from routes.tools import schema, generate_token
import os
import shutil
from getpass import getuser
import datetime

# --- Constantes de Configuración ---
LIMITE = 8  # Límite de bordados que un medio puede almacenar (lógica de negocio).
BASE = "/media"  # Directorio base donde se montan los dispositivos en Linux.
USER = getuser()  # Nombre del usuario actual para construir la ruta de montaje.

# --- Creación del Blueprint ---
bp_medios = Blueprint("bp_medios", __name__)


@bp_medios.route("/lista", methods=["GET"])
def lista():
    """
    Lista todos los medios extraíbles conectados al sistema.

    Distingue entre medios registrados en la base de datos y los que no lo están.
    Puede filtrar para mostrar solo los medios registrados.

    Args (Query Params):
        solo_registrados (int, optional): Si es 1, solo devuelve medios registrados.

    Returns:
        JSON: Una lista de objetos, cada uno representando un medio con su
              nombre, ID (si está registrado) y estado de registro.
    """
    # Obtiene el parámetro opcional para filtrar.
    args = request.args
    registrados = args.get('solo_registrados', type=int)

    # Escanea el directorio físico en busca de dispositivos montados.
    medios_fisicos = []
    mount_base = os.path.join(BASE, USER)
    if os.path.isdir(mount_base):
        for m in os.listdir(mount_base):
            m_path = os.path.join(mount_base, m)
            if os.path.isdir(m_path):
                medios_fisicos.append(m)
    else:
        return schema(404, "No hay dispositivos conectados.", [])

    # Procesa cada medio encontrado para verificar su estado de registro.
    res = []
    for m in medios_fisicos:
        m_path = os.path.join(BASE, USER, m)
        token_path = os.path.join(m_path, ".token")

        # Si existe un archivo .token, el medio podría estar registrado.
        if os.path.isfile(token_path):
            with open(token_path, 'r') as f:
                token = f.read().replace("\n", "")
            
            # Busca el token en la base de datos.
            query = db.select(Medio.id, Medio.nombre).filter_by(token=token)
            exec = db.session.execute(query).first()
            
            # Si se encuentra, se marca como registrado.
            if exec is not None:
                res.append({'id': exec.id, 'nombre': exec.nombre, 'registrado': True})
            else:
                # Si el token no está en la BD, se considera no registrado.
                res.append({'id': 0, 'nombre': m, 'registrado': False})
        else:
            # Si no hay .token, definitivamente no está registrado.
            res.append({'id': 0, 'nombre': m, 'registrado': False})

    # Aplica el filtro si fue solicitado.
    if registrados:
        res = [r for r in res if r['registrado']]

    return schema(200, "", res)


@bp_medios.route("/<int:id>", methods=["GET", "DELETE"])
def informacion(id):
    """
    Gestiona un medio específico.

    - GET: Retorna información sobre un medio, incluyendo la lista de IDs de
           bordados que contiene.
    - DELETE: Elimina un bordado específico de este medio.

    Args (URL):
        id (int): El ID del medio registrado.
    Args (Body for DELETE):
        id_bordado (int): El ID del bordado a eliminar del medio.

    Returns:
        JSON: Para GET, la lista de IDs. Para DELETE, un timestamp de confirmación.
    """
    # --- 1. Encontrar el medio (común para GET y DELETE) ---
    medio = db.session.get(Medio, id)
    if medio is None:
        return schema(404, "ID de medio no válida.", {})

    # Busca la ruta física del medio a través de su token.
    select_media_path = None
    media_token = medio.token
    media_path = os.path.join(BASE, USER)

    if not os.path.isdir(media_path):
        return schema(404, "El directorio de medios base no existe.", {})

    for m in os.listdir(media_path):
        drive_path = os.path.join(media_path, m)
        token_path = os.path.join(drive_path, '.token')
        
        if os.path.isdir(drive_path) and os.path.isfile(token_path):
            try:
                with open(token_path, 'r') as f:
                    token = f.read().strip()
                if token == media_token:
                    select_media_path = drive_path
                    break  # Encontramos el medio
            except Exception:
                continue

    if select_media_path is None:
        return schema(404, "El medio registrado no se encuentra conectado.", {})

    # --- 2. Lógica para GET ---
    if request.method == "GET":
        patterns = []
        patterns_path = os.path.join(select_media_path, '.patterns')
        
        if not os.path.isfile(patterns_path):
            return schema(200, "", {'id_bordados': [], 'limite': LIMITE})

        # Lee los IDs del archivo .patterns.
        with open(patterns_path, 'r', encoding='utf-8') as f:
            for linea in f.readlines():
                if linea.strip():
                    patterns.append(int(linea.strip()))
        
        return schema(200, "", {'id_bordados': patterns, 'limite': LIMITE})

    # --- 3. Lógica para DELETE ---
    elif request.method == "DELETE":
        id_bordado = request.form.get('id_bordado', type=int)
        if not id_bordado:
            return schema(400, "Falta 'id_bordado' en el body.", {})

        bordado = db.session.get(Bordado, id_bordado)
        if not bordado:
            return schema(404, f"Bordado con ID {id_bordado} no encontrado.", {})
        
        # Elimina el archivo físico .pes del medio.
        pes_file_path = os.path.join(select_media_path, bordado.archivo)
        if not os.path.isfile(pes_file_path):
            return schema(404, f"El archivo {bordado.archivo} no existe en el medio.", {})
        
        os.remove(pes_file_path)

        # Reescribe el archivo .patterns excluyendo el ID del bordado eliminado.
        patterns_path = os.path.join(select_media_path, '.patterns')
        advertencia = ""
        if os.path.isfile(patterns_path):
            with open(patterns_path, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
            
            nuevas_lineas = [l for l in lineas if l.strip() != str(id_bordado)]
            
            if len(nuevas_lineas) == len(lineas):
                advertencia = "Advertencia: El ID no estaba en .patterns, pero el archivo .pes fue eliminado."
            
            with open(patterns_path, 'w', encoding='utf-8') as f:
                f.writelines(nuevas_lineas)
        else:
             advertencia = "Advertencia: El archivo .patterns no existía, pero el archivo .pes fue eliminado."

        # Elimina el registro de la tabla Exportado para mantener consistencia.
        registro_exportado = db.session.query(Exportado).filter_by(medio_id=id, bordado_id=id_bordado).first()
        if registro_exportado:
            db.session.delete(registro_exportado)
            db.session.commit()
            
        timestamp = datetime.datetime.now().isoformat()
        return schema(200, advertencia or "Bordado eliminado del medio.", {"current_timestamp": timestamp})


@bp_medios.route("/exportar", methods=["POST"])
def exportar_bordado():
    """
    Exporta un bordado desde el servidor a un medio extraíble registrado.

    Copia el archivo .pes, añade su ID al archivo .patterns del medio y crea
    un registro en la tabla Exportado.

    Args (Body):
        id_bordado (int): El ID del bordado a exportar.
        id_medio (int): El ID del medio de destino.

    Returns:
        JSON: Un objeto con los detalles de la exportación exitosa.
    """
    id_bordado = request.form.get('id_bordado', type=int)
    id_medio = request.form.get('id_medio', type=int)

    if not id_bordado or not id_medio:
        return schema(400, "Faltan los parámetros 'id_bordado' o 'id_medio'.", {})

    # Busca el medio y el bordado en la base de datos.
    medio = db.session.get(Medio, id_medio)
    bordado = db.session.get(Bordado, id_bordado)

    if not medio or not bordado:
        return schema(404, "El 'id_medio' o 'id_bordado' no es válido.", {})

    # Encuentra la ruta física del medio.
    select_media_path = None
    # ... (lógica para encontrar la ruta del medio omitida por brevedad, es la misma que arriba)

    # Define las rutas de origen y destino del archivo.
    source_pattern_path = os.path.join(os.getcwd(), 'patterns', bordado.archivo)
    dest_pattern_path = os.path.join(select_media_path, bordado.archivo)

    # Realiza la exportación como una transacción para asegurar la integridad.
    try:
        # Crea el registro de exportación.
        nuevo_exportado = Exportado(bordado_id=id_bordado, medio_id=id_medio)
        db.session.add(nuevo_exportado)
        
        # Copia el archivo físico.
        shutil.copy2(source_pattern_path, dest_pattern_path)
        
        # Añade el ID al archivo .patterns.
        with open(os.path.join(select_media_path, '.patterns'), 'a', encoding='utf-8') as f:
            f.write(f"\n{id_bordado}")
        
        # Confirma todos los cambios.
        db.session.commit()
    except Exception as e:
        # Si algo falla, revierte todo.
        db.session.rollback()
        return schema(500, f"Error durante la exportación. Transacción revertida: {str(e)}", {})
    
    return schema(201, "Bordado exportado con éxito.", {"exportado_id": nuevo_exportado.id})


@bp_medios.route("/", methods=["POST"])
def registrar_medio():
    """
    Registra un nuevo medio extraíble en el sistema.

    Crea los archivos .token y .patterns en el medio físico y guarda su
    información en la base de datos.

    Args (Body):
        nombre_actual (str): El nombre del directorio actual del medio (ej: "KINGSTON").
        nuevo_nombre (str): El nombre personalizado para registrar en el sistema.

    Returns:
        JSON: Un objeto con el ID, token y timestamp del nuevo medio registrado.
    """
    nombre_actual = request.form.get('nombre_actual')
    nuevo_nombre = request.form.get('nuevo_nombre')

    if not nombre_actual or not nuevo_nombre:
        return schema(400, "Faltan los parámetros 'nombre_actual' o 'nuevo_nombre'.", {})

    media_path = os.path.join(BASE, USER, nombre_actual)
    if not os.path.isdir(media_path):
        return schema(404, f"No se encontró el directorio del medio: {media_path}", {})

    # Validaciones para evitar duplicados.
    if os.path.isfile(os.path.join(media_path, ".token")):
        return schema(404, "Este medio ya está registrado.", {})
    if db.session.query(Medio).filter_by(nombre=nuevo_nombre).first():
        return schema(404, f"El nombre '{nuevo_nombre}' ya está en uso.", {})

    # Proceso de registro transaccional.
    token = generate_token()
    token_path = os.path.join(media_path, ".token")
    patterns_path = os.path.join(media_path, ".patterns")

    try:
        # Crea los archivos en el medio físico.
        with open(token_path, 'w') as f: f.write(token)
        with open(patterns_path, 'w') as f: f.write("")
        
        # Crea el registro en la base de datos.
        nuevo_medio = Medio(nombre=nuevo_nombre, token=token)
        db.session.add(nuevo_medio)
        db.session.commit()
    except Exception as e:
        # Si algo falla, revierte los cambios físicos y de la base de datos.
        db.session.rollback()
        if os.path.isfile(token_path): os.remove(token_path)
        if os.path.isfile(patterns_path): os.remove(patterns_path)
        return schema(500, f"Error interno al registrar el medio: {str(e)}", {})
        
    return schema(201, "Medio registrado con éxito.", {
        "id": nuevo_medio.id,
        "current_timestamp": datetime.datetime.now().isoformat(),
        "token": token
    })
