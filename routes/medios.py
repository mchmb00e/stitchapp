from flask import Blueprint, jsonify, request
from db import db
from models import *
from routes.tools import schema

bp_medios = Blueprint("bp_medios", __name__)

@bp_medios.route("/", methods=["GET"])
def hello_world():
    return jsonify("Hello World from bp_medios")

# Medios externos conectados
@bp_medios.route("/info", methods=["GET"])
def medios_conectados():
    from os import getlogin, listdir
    from os.path import isdir, join, isfile

    username = getlogin()
    route = join("/media", username)
    res_medios = []

    if isdir(route):
        medios = listdir(route)

        for m in medios:
            route_medio = join(route, m)
            if isdir(route_medio):
                route_token = join(route_medio, '.token')
                if isfile(route_token):
                    with open(route_token, "r", encoding="utf-8") as f:
                        token = f.read()
                        print(token[:255])
                    query = db.session.query(Medio).filter(Medio.token == token[:255]).first()
                    print(query)
                    if query is not None:
                        res_medios.append({
                            'id': query.id,
                            'nombre': query.nombre,
                            'descripcion': query.descripcion,
                            'registrado': True
                        })
                else:
                    res_medios.append({
                        'id': -1,
                        'nombre': m,
                        'descripcion': "No se dió descripción.",
                        'registrado': False
                    })
        
        res = schema(200, "", res_medios)




    else:
        res = schema(404, f"No existe {route}", [])
    
    return jsonify(res)