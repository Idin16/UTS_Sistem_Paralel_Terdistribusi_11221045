# Dockerfile untuk Pub-Sub Log Aggregator
FROM python:3.11-slim

# Metadata
LABEL maintainer="112210245"
LABEL description="Pub-Sub Log Aggregator dengan Idempotent Consumer"

# Set working directory
WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

# Copy dependencies terlebih dahulu untuk caching
COPY requirements.txt ./

# Install dependencies + uvicorn standard
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn[standard]==0.24.0

# Copy source code
COPY src/ ./src/

# Create data directory untuk SQLite database
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Switch ke non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check bawaan Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/stats')" || exit 1

# Jalankan aplikasi (lebih aman lewat python -m)
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
