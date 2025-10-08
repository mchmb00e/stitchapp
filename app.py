from flask import Flask, jsonify
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
Base = db.Model
class Categoria(Base):
    __tablename__ = "CATEGORIAS"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(100))

    # Relación con bordados
    bordados = db.relationship("Bordado", back_populates="categoria")


class Medio(Base):
    __tablename__ = "MEDIOS"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(100))
    token = db.Column(db.String(255), nullable=False)

    # Relación con exportados
    exportados = db.relationship("Exportado", back_populates="medio")


class Bordado(Base):
    __tablename__ = "BORDADOS"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    categoria_id = db.Column("categoria", db.Integer, db.ForeignKey("CATEGORIAS.id", ondelete="SET NULL"))
    favorito = db.Column(db.Boolean, default=False)
    archivo = db.Column(db.String(50), nullable=False)
    imagen = db.Column(db.String(50), nullable=False)
    modificado = db.Column(db.TIMESTAMP, server_default=db.text("CURRENT_TIMESTAMP"), onupdate=db.text("CURRENT_TIMESTAMP"))

    # Relaciones
    categoria = db.relationship("Categoria", back_populates="bordados")
    exportados = db.relationship("Exportado", back_populates="bordado")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria_id,
            "favorito": self.favorito,
            "archivo": self.archivo,
            "imagen": self.imagen,
            "modificado": str(self.modificado)
        }


class Exportado(Base):
    __tablename__ = "EXPORTADOS"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bordado_id = db.Column("bordado", db.Integer, db.ForeignKey("BORDADOS.id"), nullable=False)
    medio_id = db.Column("medio", db.Integer, db.ForeignKey("MEDIOS.id"), nullable=False)
    fecha = db.Column(db.TIMESTAMP, server_default=db.text("CURRENT_TIMESTAMP"), nullable=False)

    # Relaciones
    bordado = db.relationship("Bordado", back_populates="exportados")
    medio = db.relationship("Medio", back_populates="exportados")


# ROUTES

## Endpoint GET

@app.route("/api/pattern/<int:id>", methods=["GET"])
def get_pattern_by_id(id: int):
    if id > 0:
        res = Bordado.query.get(id)
    else:
        res = { 'error': 404 }
    return jsonify(res.to_dict())


if __name__ == '__main__':
    app.run(debug = True, port = 5001)