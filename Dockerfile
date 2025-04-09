FROM python:3.12-alpine

# Definir variables de entorno
ENV TZ=Europe/Madrid \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    GUNICORN_WORKERS=4 \
    GUNICORN_BIND=0.0.0.0:5088 \
    GUNICORN_LOG_LEVEL=info

# Instalar solo tzdata y eliminar archivos innecesarios
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

WORKDIR /app

# Crear un usuario sin privilegios para mayor seguridad
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copiar solo requirements primero para optimizar caché
COPY ./app/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Luego copiar el resto de la aplicación
COPY ./app /app

EXPOSE 5088

# Ejecutar Gunicorn con Uvicorn
ENV PYTHONPATH=/app

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:5088", "app:app", "--log-level", "info"]
