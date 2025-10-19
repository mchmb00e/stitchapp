# ==============================================================================
# Módulo de Modelos de Datos (models.py)
# ------------------------------------------------------------------------------
# Este archivo define las clases que mapean a las tablas de la base de datos
# utilizando SQLAlchemy ORM. Cada clase representa una tabla y sus atributos
# representan las columnas.
# ==============================================================================

from db import db

# --- Definición de Modelos ---

class Categoria(db.Model):
    """
    Representa una categoría para organizar los bordados.
    """
    __tablename__ = "CATEGORIAS"

    # --- Columnas ---
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(20), nullable=False, unique=True) # El nombre debe ser único
    descripcion = db.Column(db.String(100)) # Descripción opcional

    # --- Relaciones ---
    # Define la relación "uno a muchos" con la tabla Bordado.
    # Un objeto Categoria puede tener muchos objetos Bordado.
    bordados = db.relationship("Bordado", back_populates="categoria")

class Medio(db.Model):
    """
    Representa un medio extraíble (USB, etc.) registrado en el sistema.
    """
    __tablename__ = "MEDIOS"

    # --- Columnas ---
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(20), nullable=False, unique=True) # Nombre personalizado dado por el usuario
    token = db.Column(db.String(255), nullable=False, unique=True) # Token único para identificar el medio físico

    # --- Relaciones ---
    # Define la relación "uno a muchos" con la tabla Exportado.
    exportados = db.relationship("Exportado", back_populates="medio")

class Bordado(db.Model):
    """
    Representa un archivo de bordado con sus metadatos.
    """
    __tablename__ = "BORDADOS"

    # --- Columnas ---
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True) # Nombre personalizado del bordado
    categoria_id = db.Column("categoria", db.Integer, db.ForeignKey("CATEGORIAS.id", ondelete="SET NULL")) # Clave foránea a Categoria
    favorito = db.Column(db.Boolean, default=False) # Marcador de favorito
    archivo = db.Column(db.String(50), nullable=False) # Nombre del archivo .pes en el servidor
    imagen = db.Column(db.String(50), nullable=False) # Nombre del archivo de previsualización .png
    modificado = db.Column(db.TIMESTAMP, server_default=db.text("CURRENT_TIMESTAMP"), onupdate=db.text("CURRENT_TIMESTAMP")) # Fecha de última modificación

    # --- Relaciones ---
    # Relación "muchos a uno" con Categoria.
    categoria = db.relationship("Categoria", back_populates="bordados")
    # Relación "uno a muchos" con Exportado.
    exportados = db.relationship("Exportado", back_populates="bordado")

    def to_dict(self):
        """
        Convierte el objeto Bordado en un diccionario para serialización.
        
        Returns:
            dict: Una representación del bordado en formato de diccionario.
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria_id,
            "favorito": self.favorito,
            "archivo": self.archivo,
            "imagen": self.imagen,
            "modificado": str(self.modificado)
        }

class Exportado(db.Model):
    """
    Representa un registro de exportación. Actúa como una tabla intermedia
    (pivote) entre Bordado y Medio, registrando cuándo un bordado fue
    exportado a un medio específico.
    """
    __tablename__ = "EXPORTADOS"

    # --- Columnas ---
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bordado_id = db.Column("bordado", db.Integer, db.ForeignKey("BORDADOS.id"), nullable=False) # Clave foránea a Bordado
    medio_id = db.Column("medio", db.Integer, db.ForeignKey("MEDIOS.id"), nullable=False) # Clave foránea a Medio
    fecha = db.Column(db.TIMESTAMP, server_default=db.text("CURRENT_TIMESTAMP"), nullable=False) # Fecha de la exportación

    # --- Relaciones ---
    # Relación "muchos a uno" con Bordado.
    bordado = db.relationship("Bordado", back_populates="exportados")
    # Relación "muchos a uno" con Medio.
    medio = db.relationship("Medio", back_populates="exportados")
