set -e

mkdir -p "$(dirname "$DEDUP_DB")"
mkdir -p "$PROCESSED_DIR"

echo "Starting UTS Aggregator..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8080
