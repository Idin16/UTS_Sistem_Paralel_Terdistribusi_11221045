import asyncio
import aiofiles
import os
import json

async def append_processed(processed_dir: str, topic: str, event: dict):
    """Asynchronously append processed events to per-topic ndjson file."""
    os.makedirs(processed_dir, exist_ok=True)
    file_path = os.path.join(processed_dir, f"{topic}.ndjson")
    async with aiofiles.open(file_path, "a", encoding="utf-8") as f:
        await f.write(json.dumps(event, ensure_ascii=False) + "\n")


async def consumer_worker(queue: asyncio.Queue, dedup_store, processed_dir: str, stats: dict):
    """Consume events from queue, deduplicate, and persist unique events."""
    while True:
        event = await queue.get()
        try:
            topic, eid = event["topic"], event["event_id"]
            if await dedup_store.exists(topic, eid):
                stats["duplicate_dropped"] += 1
                print(f"[DUPLICATE] {topic}:{eid}")
            else:
                await dedup_store.mark(topic, eid)
                await append_processed(processed_dir, topic, event)
                stats["unique_processed"] += 1
                stats["topics"].add(topic)
        except Exception as e:
            print("Consumer error:", e)
        finally:
            queue.task_done()


async def process_pending(queue, dedup_store, processed_dir, stats):
    """Drain queue manually (for testing)."""
    while not queue.empty():
        event = await queue.get()
        try:
            topic, eid = event["topic"], event["event_id"]
            if await dedup_store.exists(topic, eid):
                stats["duplicate_dropped"] += 1
            else:
                await dedup_store.mark(topic, eid)
                await append_processed(processed_dir, topic, event)
                stats["unique_processed"] += 1
                stats["topics"].add(topic)
        finally:
            queue.task_done()
