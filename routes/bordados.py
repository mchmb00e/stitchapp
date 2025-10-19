# ==============================================================================
# Módulo de Rutas para Bordados (routes/bordados.py)
# ------------------------------------------------------------------------------
# Este archivo define el Blueprint para todas las operaciones CRUD y otras
# utilidades relacionadas con los bordados, como filtrado, previsualización,
# y gestión de información.
# ==============================================================================

from flask import Blueprint, request, send_file
from db import db
from models import Bordado
from sqlalchemy import desc, asc
from routes.tools import schema
import os
import pyembroidery
from werkzeug.utils import secure_filename
import datetime

def count(category_id: int) -> int:
    """
    Cuenta cuántos bordados pertenecen a una categoría específica.

    Args:
        category_id (int): El ID de la categoría a consultar.

    Returns:
        int: El número total de bordados en esa categoría.
    """
    # Construye y ejecuta una consulta para contar los bordados.
    query = db.select(Bordado).filter_by(categoria_id=category_id)
    bordados = db.session.execute(query).scalars().all()
    return len(bordados)

# --- Creación del Blueprint ---
bp_bordados = Blueprint("bp_bordados", __name__)


@bp_bordados.route("/filtrar", methods=["GET"])
def filtrar():
    """
    Filtra y ordena la lista de bordados según varios criterios.

    Permite buscar por nombre, filtrar por favoritos, por categoría y
    especificar el orden de los resultados.

    Args (Query Params):
        contiene (str, optional): Texto para buscar en el nombre del bordado.
        favorito (str, optional): 'true' o '1' para filtrar solo favoritos.
        categoria (int, optional): ID de la categoría para filtrar.
        order (int, optional): Criterio de ordenación (1-4).

    Returns:
        JSON: Una lista de objetos de bordado que coinciden con el filtro.
    """
    args = request.args

    # Obtiene los parámetros de la URL.
    contiene = args.get('contiene')
    favorito_str = args.get('favorito')
    categoria_id = args.get('categoria', type=int)
    order = args.get('order', type=int)
    
    # Inicia la consulta base de SQLAlchemy.
    query = db.select(Bordado.id, Bordado.nombre, Bordado.favorito, Bordado.modificado)
    
    # Aplica los filtros de forma dinámica a la consulta.
    if contiene:
        query = query.filter(Bordado.nombre.ilike(f'%{contiene}%'))
    if favorito_str is not None:
        es_favorito = favorito_str.lower() in ('true', '1', 't')
        query = query.filter(Bordado.favorito == es_favorito)
    if categoria_id is not None:
        query = query.filter(Bordado.categoria_id == categoria_id)

    # Aplica la ordenación según el parámetro 'order'.
    if order == 1:
        query = query.order_by(asc(Bordado.nombre))
    elif order == 2:
        query = query.order_by(desc(Bordado.nombre))
    elif order == 3:
        query = query.order_by(asc(Bordado.modificado))
    elif order == 4:
        query = query.order_by(desc(Bordado.modificado))
    else:
        # Orden por defecto: los más nuevos primero.
        query = query.order_by(desc(Bordado.id))
    
    # Ejecuta la consulta final.
    resultados = db.session.execute(query).all()

    # Formatea los resultados para la respuesta JSON.
    res = [{'id': r.id, 'nombre': r.nombre, 'favorito': r.favorito} for r in resultados]

    return schema(200, "", res)


@bp_bordados.route("/previsualizacion", methods=["GET", "POST"])
def previsualizacion():
    """
    Gestiona la previsualización de archivos de bordado.

    - GET: Retorna la imagen de previsualización (.png) guardada de un bordado existente.
    - POST: Genera una previsualización temporal de un archivo .pes sin guardarlo.

    Args (GET Query Params):
        id (int): El ID del bordado del que se quiere la imagen.
    Args (POST Body):
        pattern (File): El archivo .pes a previsualizar.

    Returns:
        FileResponse: La imagen .png de la previsualización.
    """
    if request.method == "GET":
        id = request.args.get('id', type=int)
        if not id:
            return schema(404, "No se ha dado una ID", None)

        bordado = db.session.get(Bordado, id)
        if bordado:
            full_path = os.path.join(os.getcwd(), "images", bordado.imagen)
            return send_file(full_path, mimetype="image/png")
        else:
            return schema(404, "ID no válida.", None)
        
    elif request.method == "POST":
        # Limpia el directorio temporal antes de procesar.
        tmp_dir = os.path.join(os.getcwd(), 'tmp')
        if os.path.isdir(tmp_dir):
            for f in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, f))

        # Valida el archivo enviado.
        if 'pattern' not in request.files or not request.files['pattern'].filename:
            return schema(404, "No se seleccionó ningún archivo .PES.", None)
        
        pattern = request.files['pattern']
        if not pattern.filename.lower().endswith(".pes"):
            return schema(400, "El archivo debe ser .PES", None)

        # Guarda temporalmente el .pes, lo convierte a .png y lo envía.
        tmp_save_pes = os.path.join(tmp_dir, 'tmp.pes')
        pattern.save(tmp_save_pes)
        
        p = pyembroidery.read_pes(tmp_save_pes)
        tmp_save_png = os.path.join(tmp_dir, 'tmp.png')
        pyembroidery.write_png(p, tmp_save_png)

        return send_file(tmp_save_png, mimetype="image/png")


@bp_bordados.route("/<int:id>", methods=["GET", "PUT"])
def bordado_informacion(id):
    """
    Gestiona un bordado específico por su ID.

    - GET: Retorna la información detallada de un bordado.
    - PUT: Actualiza el nombre, categoría o estado de favorito de un bordado.

    Args (URL):
        id (int): El ID del bordado a gestionar.
    Args (Body for PUT):
        nombre (str, optional): El nuevo nombre.
        categoria (int, optional): El nuevo ID de categoría.
        favorito (str, optional): 'true' o 'false'.

    Returns:
        JSON: Para GET, los detalles del bordado. Para PUT, un timestamp.
    """
    bordado = db.session.get(Bordado, id)
    if bordado is None:
        return schema(404, "ID no válido.", {})

    if request.method == "GET":
        res = bordado.to_dict() # Usa el método del modelo para serializar.
        return schema(200, "", res)

    elif request.method == "PUT":
        data = request.form
        try:
            # Actualiza el nombre si se provee, validando que no esté en uso.
            if 'nombre' in data and data['nombre'] != bordado.nombre:
                nombre_existente = db.session.query(Bordado).filter(Bordado.id != id, Bordado.nombre == data['nombre']).first()
                if nombre_existente:
                    return schema(404, f"El nombre '{data['nombre']}' ya está en uso.", {})
                bordado.nombre = data['nombre']

            # Actualiza la categoría.
            if 'categoria' in data:
                bordado.categoria_id = int(data['categoria']) if data['categoria'] else None

            # Actualiza el estado de favorito.
            if 'favorito' in data:
                bordado.favorito = data.get('favorito', '').lower() in ('true', '1', 't')

            db.session.commit()
            return schema(200, "Bordado actualizado.", {"current_timestamp": datetime.datetime.now().isoformat()})
        except Exception as e:
            db.session.rollback()
            return schema(500, f"Error al actualizar: {str(e)}", {})


@bp_bordados.route("/", methods=["POST"])
def crear_bordado():
    """
    Crea un nuevo bordado en el sistema.

    Recibe un archivo .pes y datos asociados. Guarda el archivo .pes, genera
    y guarda una previsualización .png, y crea el registro en la base de datos.

    Args (Body):
        pattern (File): El archivo .pes del bordado.
        nombre (str): El nombre para el nuevo bordado.
        categoria (int, optional): El ID de la categoría.
        favorito (str, optional): 'true' o 'false'.

    Returns:
        JSON: El objeto del bordado recién creado.
    """
    # Validaciones iniciales del request.
    if "pattern" not in request.files:
        return schema(404, "Debe ingresar bordado (.PES).", {})
    file = request.files['pattern']
    nombre = request.form.get('nombre')
    if not nombre or not file or not file.filename:
        return schema(400, "Faltan 'nombre' o 'pattern' en la petición.", {})

    # Validaciones de negocio (nombre y archivo no duplicados).
    if db.session.query(Bordado).filter_by(nombre=nombre).first():
        return schema(404, f"El nombre '{nombre}' ya está en uso.", {})
    
    pattern_filename = secure_filename(file.filename)
    pattern_save_path = os.path.join(os.getcwd(), 'patterns', pattern_filename)
    if os.path.exists(pattern_save_path):
        return schema(404, f"Ya existe un archivo con el nombre {pattern_filename}", {})

    # Proceso de guardado y creación como una transacción.
    try:
        # Guarda el archivo .pes original.
        file.save(pattern_save_path)

        # Genera y guarda la previsualización .png.
        image_filename = os.path.splitext(pattern_filename)[0] + '.png'
        image_save_path = os.path.join(os.getcwd(), 'images', image_filename)
        p = pyembroidery.read_pes(pattern_save_path)
        pyembroidery.write_png(p, image_save_path)

        # Crea y guarda el nuevo registro en la base de datos.
        nuevo_bordado = Bordado(
            nombre=nombre,
            categoria_id=request.form.get('categoria', type=int),
            favorito=request.form.get('favorito', 'false').lower() in ('true', '1', 't'),
            archivo=pattern_filename,
            imagen=image_filename
        )
        db.session.add(nuevo_bordado)
        db.session.commit()
        
        return schema(201, "Bordado creado con éxito.", nuevo_bordado.to_dict())
    except Exception as e:
        # Si algo falla, revierte la transacción y limpia los archivos creados.
        db.session.rollback()
        if os.path.exists(pattern_save_path): os.remove(pattern_save_path)
        if 'image_save_path' in locals() and os.path.exists(image_save_path): os.remove(image_save_path)
        return schema(500, f"Error interno al procesar el archivo: {str(e)}", {})
