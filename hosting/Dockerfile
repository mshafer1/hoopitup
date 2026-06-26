# Multi-stage build: Build frontend
FROM node:lts-alpine3.23@sha256:595398b0081eacda8e1c4c5b97b76cd1020e4d58a8ebcb4843b9bca1e79e7436 AS frontend-builder
WORKDIR /app/frontend
COPY app/frontend/package*.json ./
RUN npm install
COPY app/frontend/ ./
RUN npm run build

# Poetry compile stage: Export dependencies
FROM python:3.11-slim AS poetry-export
WORKDIR /app
RUN pip install --no-cache-dir poetry==2.4.1 poetry-plugin-export
COPY app/backend/pyproject.toml app/backend/poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final stage: Python and app
FROM python:3.11-slim

# Set working directory
WORKDIR /app


# Copy exported requirements from poetry stage
COPY --from=poetry-export /app/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY app/backend/ /app/backend/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy entrypoint script
COPY hosting/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

# Run entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
