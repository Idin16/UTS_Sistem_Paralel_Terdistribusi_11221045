FROM python:3.11-slim
WORKDIR /app

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/

COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh

USER appuser
EXPOSE 8080

CMD ["./docker-entrypoint.sh"]