from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ----------------------
# Modelos
# ----------------------

class Categoria(Base):
    __tablename__ = "CATEGORIAS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(20), nullable=False)
    descripcion = Column(String(100))

    # Relación con bordados
    bordados = relationship("Bordado", back_populates="categoria")


class Medio(Base):
    __tablename__ = "MEDIOS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(20), nullable=False)
    descripcion = Column(String(100))
    token = Column(String(255), nullable=False)

    # Relación con exportados
    exportados = relationship("Exportado", back_populates="medio")


class Bordado(Base):
    __tablename__ = "BORDADOS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    categoria_id = Column("categoria", Integer, ForeignKey("CATEGORIAS.id", ondelete="SET NULL"))
    favorito = Column(Boolean, default=False)
    archivo = Column(String(50), nullable=False)
    imagen = Column(String(50), nullable=False)
    modificado = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    # Relaciones
    categoria = relationship("Categoria", back_populates="bordados")
    exportados = relationship("Exportado", back_populates="bordado")


class Exportado(Base):
    __tablename__ = "EXPORTADOS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bordado_id = Column("bordado", Integer, ForeignKey("BORDADOS.id"), nullable=False)
    medio_id = Column("medio", Integer, ForeignKey("MEDIOS.id"), nullable=False)
    fecha = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relaciones
    bordado = relationship("Bordado", back_populates="exportados")
    medio = relationship("Medio", back_populates="exportados")
