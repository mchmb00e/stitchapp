# ==============================================================================
# Archivo Principal de la Aplicación Flask (app.py)
# ------------------------------------------------------------------------------
# Este script inicializa y configura la aplicación Flask, conecta la base de
# datos con SQLAlchemy y registra los blueprints que definen las rutas de la API.
# ==============================================================================

from flask import Flask
from flask_cors import CORS
from db import db



# --- 1. Inicialización y Configuración de la Aplicación ---

app = Flask(__name__) # Creación de la instancia principal de la aplicación Flask

CORS(app)

# Configuraciones de la aplicación
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Stitchapp123#$@db:3306/PROY_STITCHAPP" # URL de conexión a la base de datos
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # Desactiva el seguimiento de modificaciones para mejorar el rendimiento

# Inicializa la extensión SQLAlchemy con la aplicación Flask
db.init_app(app)


# --- 2. Registro de Blueprints (Módulos de la API) ---

# Importa los blueprints que contienen las rutas de cada módulo
from routes.medios import bp_medios
from routes.bordados import bp_bordados
from routes.categorias import bp_categorias

# Registra cada blueprint con un prefijo de URL específico.
# Esto organiza las rutas de la API, por ejemplo, todas las rutas de medios
# comenzarán con /api/medios.
app.register_blueprint(bp_medios, url_prefix="/api/medios")
app.register_blueprint(bp_bordados, url_prefix="/api/bordados")
app.register_blueprint(bp_categorias, url_prefix="/api/categorias")


# --- 3. Punto de Entrada para Ejecutar el Servidor ---

if __name__ == '__main__':
    """
    Punto de entrada principal para la aplicación.
    
    Este bloque se ejecuta solo cuando el script es llamado directamente
    (por ejemplo, `python app.py`). Inicia el servidor de desarrollo de Flask.
    """
    # Ejecuta la aplicación en modo debug en el puerto 5001
    app.run(debug = True, host = '0.0.0.0')
