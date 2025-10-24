import asyncio
import logging

class Consumer:
    def __init__(self, queue, store, stats):
        self.queue = queue
        self.store = store
        self.stats = stats
        self._task = None
        self._running = False

    async def start(self):
        logging.info("Consumer started")
        self._running = True
        # Jalankan loop consumer di background
        self._task = asyncio.create_task(self.run())

    async def stop(self):
        logging.info("Stopping consumer...")
        self._running = False
        if self._task:
            await self._task

    async def run(self):
        while self._running:
            event = await self.queue.get()
            key = (event["topic"], event["event_id"])

            # cek apakah sudah pernah diproses
            if self.store.is_duplicate(*key):
                self.stats['duplicate_dropped'] += 1
                logging.info(f"Duplicate dropped: {key}")
            else:
                self.store.save_event(event)
                self.stats['unique_processed'] += 1
                logging.info(f"Processed event: {key}")

            self.queue.task_done()
