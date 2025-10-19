################################################################################
#
# Script para Poblar la Base de Datos PROY_STITCHAPP
# ------------------------------------------------------------------------------
# Este script lee todos los archivos de bordado (.pes) de una carpeta 'patterns',
# genera una previsualización en formato .png para cada uno en la carpeta 'images',
# y guarda la información de cada bordado en la base de datos utilizando
# múltiples hilos para acelerar el proceso.
#
# Autor: Miguel Chamorro | miguelchamorro912@gmail.com
#
################################################################################

from threading import Thread, Lock
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Bordado  # Asume que 'models.py' está en la misma ruta
import os
import pyembroidery as pe

# ----------------------
# 1. Configuración de SQLAlchemy
# ----------------------
# Se crea el motor de la base de datos.
# IMPORTANTE: Reemplazar "ADD URL DATABASE" con la URL de conexión real.
engine = create_engine("ADD URL DATABASE")

# Se crea una fábrica de sesiones que estará vinculada al motor.
# Cada hilo utilizará esta fábrica para crear su propia sesión aislada.
Session = sessionmaker(bind=engine)

# ----------------------
# 2. Funciones Auxiliares
# ----------------------

def wext(file: str) -> str:
    """
    Elimina la extensión de un nombre de archivo.
    
    Args:
        file (str): El nombre del archivo con extensión.
        
    Returns:
        str: El nombre del archivo sin la extensión.
    """
    # Encuentra la posición del último punto y devuelve la subcadena anterior.
    return file[:file.rfind('.')]

def proccess_file(file: str):
    """
    Procesa un único archivo de bordado.
    
    Esta función es ejecutada por cada hilo. Crea su propia sesión de base de
    datos para garantizar que las operaciones sean seguras para los hilos (thread-safe).
    Lee un archivo .pes, genera un .png y guarda un registro en la tabla Bordado.
    
    Args:
        file (str): El nombre del archivo a procesar de la carpeta 'patterns'.
    """
    # Crea una nueva sesión de base de datos para este hilo específico.
    session = Session()
    try:
        # Construye la ruta completa al archivo .pes de origen.
        full_path = os.path.join(os.getcwd(), 'patterns', file)
        nombre_sin_extension = wext(file)

        # Lee el archivo de bordado y genera su previsualización en .png.
        pattern = pe.read_pes(full_path)
        pe.write_png(pattern, os.path.join(os.getcwd(), 'images', nombre_sin_extension + '.png'))

        # Crea un nuevo objeto Bordado con la información extraída.
        bordado = Bordado(
            nombre=nombre_sin_extension,
            categoria_id=None,  # La categoría se puede asignar después.
            archivo=file,
            imagen=nombre_sin_extension + '.png'
        )
        # Añade y confirma el nuevo registro en la base de datos.
        session.add(bordado)
        session.commit()
    except Exception as e:
        # Si ocurre un error, se imprime y se revierte la transacción.
        print(f"Error procesando {file}: {e}")
        session.rollback()
    finally:
        # Se asegura de que la sesión se cierre siempre, liberando la conexión.
        session.close()

# ----------------------
# 3. Ejecución Multihilo
# ----------------------

def run_in_threads(files_to_process: list, num_threads: int):
    """
    Distribuye la lista de archivos para ser procesados en múltiples hilos.
    
    Args:
        files_to_process (list): La lista de nombres de archivo a procesar.
        num_threads (int): El número de hilos que se utilizarán.
    """
    threads = []
    lock = Lock()  # Lock para sincronizar el acceso a la variable de progreso.
    total_files = len(files_to_process)
    processed_count = [0]  # Se usa una lista para que sea mutable y compartida.

    def worker(files, thread_id):
        """Función que cada hilo ejecutará."""
        for f in files:
            proccess_file(f)
            # Usa un Lock para actualizar el contador de progreso de forma segura.
            with lock:
                processed_count[0] += 1
                porcentaje = (processed_count[0] / total_files) * 100
                # Imprime el progreso en la misma línea.
                print(f"[Hilo {thread_id}] Procesados {processed_count[0]}/{total_files} "
                      f"archivos ({porcentaje:.1f}%)", end='\r')

    # Distribuye los archivos entre los hilos.
    for i in range(num_threads):
        # La sintaxis de slicing [i::num_threads] asigna archivos de forma equitativa.
        files_for_thread = files_to_process[i::num_threads]
        if not files_for_thread:
            continue
        
        # Crea e inicia cada hilo.
        t = Thread(target=worker, args=(files_for_thread, i + 1))
        threads.append(t)
        t.start()

    # Espera a que todos los hilos terminen su ejecución.
    for t in threads:
        t.join()

    print("\nTodos los archivos han sido procesados.")

# ----------------------
# 4. Punto de Entrada del Script
# ----------------------
if __name__ == "__main__":
    # Obtiene la lista de archivos de la carpeta 'patterns'.
    route = os.listdir('patterns')
    # Define el número de hilos a utilizar.
    k = 16
    # Inicia el procesamiento multihilo.
    run_in_threads(route, k)
