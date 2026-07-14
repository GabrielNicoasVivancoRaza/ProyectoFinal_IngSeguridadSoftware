# Imagen del backend FastAPI.
# Se usa una base slim y un usuario sin privilegios (buena practica DevSecOps).
FROM python:3.11-slim

# No escribir .pyc y salida sin buffer (logs inmediatos en contenedor)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias primero, para aprovechar la cache de capas de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Codigo de la aplicacion
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./

# Usuario sin privilegios y directorios de datos con permisos correctos.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/storage /app/ca_data \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
