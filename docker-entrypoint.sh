#!/bin/sh
# Entry point untuk menjalankan FastAPI server

echo "Starting UTS Aggregator Service..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8080
