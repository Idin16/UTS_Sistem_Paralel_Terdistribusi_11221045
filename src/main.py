import asyncio
import time
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .models import Event
from .dedup_store import DedupStore
from .consumer import Consumer
import uvicorn
from typing import List, Union
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="UTS Aggregator")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_PATH = "data/dedup.db"
store = DedupStore(DB_PATH)
queue: asyncio.Queue = asyncio.Queue()

stats = {
    'received': 0,
    'unique_processed': 0,
    'duplicate_dropped': 0,
    'topics': set(),
    'start_time': time.time()
}
consumer = Consumer(queue, store, stats)

@app.on_event("startup")
async def startup_event():
    # ensure data dir exists
    import os
    os.makedirs("data", exist_ok=True)
    await consumer.start()

@app.on_event("shutdown")
async def shutdown_event():
    await consumer.stop()

@app.post("/publish")
async def publish(request: Request, payload: Union[dict, list] = Body(...)):
    events = []
    # accept single object or list
    if isinstance(payload, list):
        events = payload
    elif isinstance(payload, dict):
        events = [payload]
    else:
        raise HTTPException(status_code=400, detail="Invalid payload")

    accepted = 0
    for ev in events:
        try:
            e = Event.parse_obj(ev)
        except Exception as ex:
            raise HTTPException(status_code=400, detail=f"Invalid event schema: {ex}")
        stats['received'] += 1
        stats['topics'].add(e.topic)
        await queue.put(e.dict())
        accepted += 1
    return JSONResponse({"accepted": accepted})

@app.get("/events")
async def get_events(topic: str | None = None):
    results = store.list_events(topic)
    return JSONResponse(results)

@app.get("/stats")
async def get_stats():
    uptime = time.time() - stats['start_time']
    return JSONResponse({
        'received': stats['received'],
        'unique_processed': stats['unique_processed'],
        'duplicate_dropped': stats['duplicate_dropped'],
        'topics': list(stats['topics']),
        'uptime_seconds': int(uptime)
    })

if __name__ == '__main__':
    uvicorn.run("src.main:app", host='0.0.0.0', port=8080)
