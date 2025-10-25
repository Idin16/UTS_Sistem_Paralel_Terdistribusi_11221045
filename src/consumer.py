import asyncio
import logging
import aiofiles
import os
import json


class Consumer:
    """Consumer utama untuk memproses event dari queue dengan deduplication."""
    def __init__(self, queue, store=None, stats=None):
        self.queue = queue
        self.store = store
        self.stats = stats or {
            "unique_processed": 0,
            "duplicate_dropped": 0,
            "topics": set(),
        }
        self._task = None
        self._running = False

    async def start(self):
        logging.info("Consumer started")
        self._running = True
        self._task = asyncio.create_task(self.run())

    async def stop(self):
        logging.info("Stopping consumer...")
        self._running = False
        if self._task:
            await self._task

    async def run(self):
        """Loop utama untuk memproses event dari queue."""
        while self._running:
            event = await self.queue.get()
            try:
                topic, eid = event["topic"], event["event_id"]
                if self.store.is_duplicate(topic, eid):
                    self.stats["duplicate_dropped"] += 1
                    logging.info(f"[DUPLICATE] {topic}:{eid}")
                else:
                    self.store.save_event(event)
                    self.stats["unique_processed"] += 1
                    self.stats["topics"].add(topic)
                    logging.info(f"[PROCESSED] {topic}:{eid}")
            except Exception as e:
                logging.error(f"Consumer error: {e}")
            finally:
                self.queue.task_done()


# 🔹 Fungsi async tambahan (dipakai manual/test)
async def append_processed(processed_dir: str, topic: str, event: dict):
    os.makedirs(processed_dir, exist_ok=True)
    file_path = os.path.join(processed_dir, f"{topic}.ndjson")
    async with aiofiles.open(file_path, "a", encoding="utf-8") as f:
        await f.write(json.dumps(event, ensure_ascii=False) + "\n")


async def consumer_worker(queue: asyncio.Queue, dedup_store, processed_dir: str, stats: dict):
    """Versi worker untuk testing/manual"""
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
                print(f"[PROCESSED] {topic}:{eid}")
        except Exception as e:
            print("Consumer error:", e)
        finally:
            queue.task_done()


async def process_pending(queue, dedup_store, processed_dir, stats):
    """Drain queue secara manual (untuk debug/test)."""
    while not queue.empty():
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
                print(f"[PROCESSED] {topic}:{eid}")
        except Exception as e:
            print("Consumer error:", e)
        finally:
            queue.task_done()


# 🔹 Alias agar test lama tetap bisa jalan
EventConsumer = Consumer
