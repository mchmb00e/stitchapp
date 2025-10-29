# Usa una imagen base oficial de Python (Python 3.11 Slim para ser ligero)
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copia el archivo de requisitos e instala las dependencias
# Esto se hace primero para aprovechar el caché de Docker
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo
COPY api/ .

# Expone el puerto por defecto de Flask
EXPOSE 5000

# Define la variable de entorno para que Flask sepa dónde está la aplicación
ENV FLASK_APP=app.py

# Comando para ejecutar la aplicación (usando un servidor Gunicorn/Waitress para producción)
# Para desarrollo simple con el servidor integrado de Flask, usa:
CMD [ "python3", "app.py" ]