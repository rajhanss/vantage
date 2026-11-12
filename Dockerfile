# Multi-stage Dockerfile for Vantage Platform

# Stage 1: Build Frontend Assets
FROM node:20-slim AS frontend-builder
WORKDIR /app/web
COPY web/package*.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    VANTAGE_DB_PATH=/data/vantage.db

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend
COPY backend/pyproject.toml ./backend/
RUN pip install --no-cache-dir ./backend

COPY backend/ ./backend/
RUN pip install --no-cache-dir -e ./backend

# Copy compiled frontend into backend static mount
COPY --from=frontend-builder /app/web/dist ./backend/vantage/static

# Create persistent data volume mount point
RUN mkdir -p /data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["sh", "-c", "uvicorn vantage.main:app --host 0.0.0.0 --port ${PORT}"]
