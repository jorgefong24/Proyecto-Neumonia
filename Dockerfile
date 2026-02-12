FROM python:3.10-slim

# Evita prompts interactivos al instalar paquetes
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependencias del sistema (Tkinter, OpenCV y X11 para GUI)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    tk \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir .

# Por defecto corre en modo CLI (útil en contenedor).
# Para la GUI (Tkinter) en contenedor se requiere servidor X/WSLg.
CMD ["python", "cli.py", "--help"]
