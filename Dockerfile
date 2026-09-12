# Multi-stage Dockerfile for FLOODTWIN RESPONDER
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim AS backend
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY geospatial/ ./geospatial/
COPY risk-engine/ ./risk-engine/
COPY rag/ ./rag/
COPY agent/ ./agent/
COPY mcp-server/ ./mcp-server/
COPY sample-data/ ./sample-data/
COPY risk_engine.py ./
COPY mcp_server.py ./
COPY scripts/ ./scripts/

# Copy built frontend assets
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
