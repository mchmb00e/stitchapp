# ==============================================================================
# Módulo de Rutas para Categorías (routes/categorias.py)
# ------------------------------------------------------------------------------
# Este archivo define el Blueprint para todas las operaciones CRUD (Crear, Leer,
# Actualizar, Eliminar) relacionadas con las categorías de bordados.
# ==============================================================================

from flask import Blueprint, jsonify, request
from db import db
from models import Categoria
from routes.tools import schema
from routes.bordados import count
import datetime

# --- Creación del Blueprint ---
bp_categorias = Blueprint("bp_categorias", __name__)


@bp_categorias.route("/lista", methods=["GET"])
def lista():
    """
    Obtiene una lista de todas las categorías existentes.

    Para cada categoría, también calcula y añade la cantidad de bordados
    que pertenecen a ella.

    Returns:
        JSON: Una lista de objetos, donde cada objeto representa una categoría
              con su id, nombre, descripción y la cantidad de bordados asociados.
    """
    # Define la consulta para seleccionar los campos básicos de la categoría.
    query = db.select(Categoria.id, Categoria.nombre, Categoria.descripcion)
    
    # Ejecuta la consulta y obtiene todos los resultados.
    exec = db.session.execute(query).all()
    
    res = []

    # Itera sobre cada fila de resultado para construir la respuesta final.
    for r in exec:
        res.append({
            'id': r.id,
            'nombre': r.nombre,
            'descripcion': r.descripcion,
            # Llama a la función 'count' para obtener el número de bordados.
            'cantidad': count(r.id)
        })

    return schema(200, "", res)


@bp_categorias.route("/", methods=["POST"])
def crear_categoria():
    """
    Crea una nueva categoría en la base de datos.

    Recibe el nombre y la descripción desde un formulario multipart/form-data.
    Valida que el nombre de la categoría no esté ya en uso.

    Args (Body):
        nombre (str): El nombre para la nueva categoría.
        descripcion (str, optional): Una descripción para la categoría.

    Returns:
        JSON: Un objeto con el ID de la categoría recién creada.
    """
    # Obtiene datos de request.form, adecuado para multipart/form-data.
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')  # Será None si no se envía.

    # Valida que el campo 'nombre' no esté vacío.
    if not nombre:
        return schema(400, "El campo 'nombre' es requerido.", {})

    # Comprueba que no exista otra categoría con el mismo nombre.
    categoria_existente = db.session.query(Categoria).filter_by(nombre=nombre).first()
    if categoria_existente:
        return schema(404, f"La categoría con el nombre '{nombre}' ya existe.", {})

    # Crea la nueva instancia del modelo Categoria.
    nueva_categoria = Categoria(
        nombre=nombre,
        descripcion=descripcion
    )

    # Intenta guardar la nueva categoría en la base de datos.
    try:
        db.session.add(nueva_categoria)
        db.session.commit()
        
        # Devuelve el ID como confirmación (código 201: Created).
        return schema(201, "Categoría creada con éxito", {
            "id": nueva_categoria.id
        })
    except Exception as e:
        # Si algo falla, revierte la transacción para mantener la consistencia.
        db.session.rollback()
        print(f"Error al crear categoría: {e}")
        return schema(500, "Error interno del servidor al guardar la categoría.", {})


@bp_categorias.route("/<int:id>", methods=["PUT", "DELETE"])
def gestionar_categoria_individual(id):
    """
    Gestiona una categoría específica por su ID.

    - PUT: Actualiza el nombre y/o la descripción de la categoría.
    - DELETE: Elimina la categoría de la base de datos.

    Args (URL):
        id (int): El ID de la categoría a gestionar.
    Args (Body for PUT):
        nombre (str, optional): El nuevo nombre para la categoría.
        descripcion (str, optional): La nueva descripción.

    Returns:
        JSON: Un timestamp de confirmación de la operación.
    """
    # Obtiene la categoría de la base de datos; común para PUT y DELETE.
    categoria = db.session.get(Categoria, id)
    if not categoria:
        return schema(404, "ID de categoría no válido.", {})

    # --- Lógica para PUT (Actualizar) ---
    if request.method == "PUT":
        data = request.form
        try:
            # Actualiza el nombre si se proporciona, validando que no se duplique.
            if 'nombre' in data:
                nuevo_nombre = data.get('nombre')
                if not nuevo_nombre:
                    return schema(400, "El nombre no puede estar vacío.", {})
                if nuevo_nombre != categoria.nombre:
                    nombre_existente = db.session.query(Categoria).filter(
                        Categoria.id != id, Categoria.nombre == nuevo_nombre
                    ).first()
                    if nombre_existente:
                        return schema(404, f"El nombre '{nuevo_nombre}' ya está en uso.", {})
                    categoria.nombre = nuevo_nombre

            # Actualiza la descripción si se proporciona.
            if 'descripcion' in data:
                categoria.descripcion = data.get('descripcion')

            db.session.commit()
            timestamp = datetime.datetime.now().isoformat()
            return schema(200, "Categoría actualizada.", {"current_timestamp": timestamp})

        except Exception as e:
            db.session.rollback()
            return schema(500, f"Error al actualizar la categoría: {str(e)}", {})

    # --- Lógica para DELETE (Eliminar) ---
    elif request.method == "DELETE":
        try:
            # Elimina el objeto de la sesión y confirma.
            # La relación en el modelo Bordado con "ondelete=SET NULL" asegura que
            # los bordados asociados no se borren, solo se desvinculen.
            db.session.delete(categoria)
            db.session.commit()
            
            timestamp = datetime.datetime.now().isoformat()
            return schema(200, "Categoría eliminada.", {"current_timestamp": timestamp})
            
        except Exception as e:
            db.session.rollback()
            return schema(500, f"Error al eliminar la categoría: {str(e)}", {})