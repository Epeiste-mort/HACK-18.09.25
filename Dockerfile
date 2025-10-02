# Stage 1: Build SPA
FROM node:18-bullseye AS web
WORKDIR /web
COPY web/package*.json ./
RUN npm i --silent --no-progress || npm i --silent --no-progress
COPY web/ ./
RUN npm run build

# Stage 2: Service (GPU-capable base works on CPU too)
FROM tensorflow/tensorflow:2.20.0-gpu

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender1 unar \
  && rm -rf /var/lib/apt/lists/*

COPY requirements-svc.txt ./
RUN pip install --upgrade pip && pip install -r requirements-svc.txt

COPY app/ ./app/
COPY scripts/ ./scripts/
COPY meanCT_model.keras meanCT_model.h5* ./
COPY --from=web /web/dist ./web/dist

ENV MODEL_PATH=/app/meanCT_model.keras

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]


