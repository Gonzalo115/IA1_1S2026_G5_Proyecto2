# Python 3.11 requerido por mediapipe 0.10.9
FROM python:3.11-slim

# Librerias del sistema necesarias para OpenCV y MediaPipe en Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias primero para aprovechar cache de capas
COPY requirements.txt .
RUN pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el codigo de la aplicacion
COPY . .

# Crear carpeta de modelos si no existe (el modelo entrenado se monta como volumen)
RUN mkdir -p models

EXPOSE 8000

# Gunicorn: 1 worker (MediaPipe no es thread-safe), timeout 300s para entrenamientos largos
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "300", "app:app"]