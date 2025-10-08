#####################
#
# Script para poblar la base de datos PROY_STITCHAPP
#
# Miguel Chamorro | miguelchamorro912@gmail.com
#
#####################

from threading import Thread, Lock
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from model import Bordado
import os
import pyembroidery as pe

# ----------------------
# Configuración SQLAlchemy
# ----------------------
engine = create_engine("ADD URL DATABASE")
Session = sessionmaker(bind=engine)

# ----------------------
# Funciones auxiliares
# ----------------------
def wext(file: str) -> str:
    return file[:file.rfind('.')]

def proccess_file(file: str):
    """Procesa un archivo creando su propia sesión."""
    session = Session()
    try:
        full_path = os.path.join(os.getcwd(), 'patterns', file)
        nombre0 = wext(file)

        pattern = pe.read_pes(full_path)
        pe.write_png(pattern, os.path.join(os.getcwd(), 'images', nombre0 + '.png'))

        bordado = Bordado(
            nombre=nombre0,
            categoria_id=None,
            archivo=file,
            imagen=nombre0 + '.png'
        )
        session.add(bordado)
        session.commit()
    except Exception as e:
        print(f"Error procesando {file}: {e}")
        session.rollback()
    finally:
        session.close()

# ----------------------
# Ejecutar en hilos con progreso
# ----------------------
def run_in_threads(route, k):
    threads = []
    lock = Lock()
    progreso_total = len(route)
    progreso_actual = [0]  # lista mutable para compartir entre hilos

    def worker(files, thread_id):
        for f in files:
            proccess_file(f)
            with lock:
                progreso_actual[0] += 1
                porcentaje = (progreso_actual[0] / progreso_total) * 100
                print(f"[Hilo {thread_id}] Procesados {progreso_actual[0]}/{progreso_total} "
                      f"archivos ({porcentaje:.1f}%)", end='\r')

    for i in range(k):
        files_for_thread = route[i::k]
        if not files_for_thread:
            continue
        t = Thread(target=worker, args=(files_for_thread, i+1))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\nTodos los archivos procesados.")

route = os.listdir('patterns')
k = 16  # número de hilos
run_in_threads(route, k)
