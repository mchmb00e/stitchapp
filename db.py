# ==============================================================================
# Módulo de Base de Datos (db.py)
# ------------------------------------------------------------------------------
# Este script centraliza la creación de la instancia de SQLAlchemy.
# Al importarla desde otros módulos (como app.py o los modelos), se asegura
# que toda la aplicación utilice la misma instancia de base de datos, evitando
# problemas de referencias circulares e inconsistencias.
# ==============================================================================

from flask_sqlalchemy import SQLAlchemy

# Creación de la instancia global de SQLAlchemy.
# Esta instancia 'db' se importará en otros archivos para definir los modelos
# y para ser inicializada con la aplicación Flask en app.py.
db = SQLAlchemy()
