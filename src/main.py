import os
import time
import asyncio
import json
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException
import aiofiles
from .models import Event, Stats
from .dedup_store import DedupStore
from .consumer import consumer_worker, process_pending

DB_PATH = os.getenv("DEDUP_DB", "/app/data/dedup.db")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "/app/data/processed")
WORKERS = int(os.getenv("WORKERS", "2"))

app = FastAPI(title="UTS Aggregator System")

queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
dedup_store = DedupStore(DB_PATH)

stats = {
    "received": 0,
    "unique_processed": 0,
    "duplicate_dropped": 0,
    "topics": set(),
    "start_time": time.time(),
}

@app.get("/")
async def root():
    return {
        "service": "UTS Aggregator System",
        "status": "running",
        "docs": "/docs",
        "available_endpoints": ["/publish", "/events", "/stats", "/health"]
    }

@app.on_event("startup")
async def startup():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    await dedup_store.init()

    app.state.workers = [
        asyncio.create_task(consumer_worker(queue, dedup_store, PROCESSED_DIR, stats))
        for _ in range(WORKERS)
    ]
    print(f"Started {WORKERS} consumer workers")

    if os.path.exists(PROCESSED_DIR):
        topics = [
            f.replace(".ndjson", "")
            for f in os.listdir(PROCESSED_DIR)
            if f.endswith(".ndjson")
        ]
        stats["topics"].update(topics)
        print(f"[RECOVERED] Loaded topics from disk: {topics}")
    else:
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        print("[INIT] Created new processed directory.")

@app.on_event("shutdown")
async def shutdown():
    for w in app.state.workers:
        w.cancel()
    if hasattr(dedup_store, "close"):
        await dedup_store.close()

@app.post("/publish")
async def publish(request: Request):
    """Receive single or batch event JSON payload."""
    body = await request.json()
    events = body if isinstance(body, list) else [body]
    accepted = 0
    for e in events:
        try:
            event = Event(**e).dict()
            await queue.put(event)
            stats["received"] += 1
            stats["topics"].add(event["topic"])  # add immediately
            accepted += 1
        except Exception as ex:
            raise HTTPException(status_code=400, detail=str(ex))
    return {"accepted": accepted, "received_total": stats["received"]}

@app.get("/events")
async def get_events(topic: Optional[str] = None):
    """Return processed events (deduplicated)."""
    result: List[dict] = []
    topics = [topic] if topic else [
        f[:-7] for f in os.listdir(PROCESSED_DIR) if f.endswith(".ndjson")
    ]
    for t in topics:
        file_path = os.path.join(PROCESSED_DIR, f"{t}.ndjson")
        if not os.path.exists(file_path):
            continue
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            async for line in f:
                try:
                    result.append(json.loads(line))
                except Exception:
                    continue
    return result

@app.get("/stats", response_model=Stats)
async def get_stats():
    """Expose runtime metrics for observability."""
    return {
        "received": stats["received"],
        "unique_processed": stats["unique_processed"],
        "duplicate_dropped": stats["duplicate_dropped"],
        "topics": sorted(stats["topics"]),
        "uptime_seconds": time.time() - stats["start_time"],
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Aggregator is running"}

# For testing
app.state.process_pending = process_pending
