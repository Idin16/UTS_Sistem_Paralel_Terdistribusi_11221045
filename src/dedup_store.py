import asyncio
import aiosqlite
import os
import time


class DedupStore:
    """Asynchronous SQLite deduplication store using aiosqlite."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: aiosqlite.Connection | None = None
        self.lock = asyncio.Lock()

    async def init(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS dedup (
                topic TEXT NOT NULL,
                event_id TEXT NOT NULL,
                received_at REAL,
                PRIMARY KEY (topic, event_id)
            )
        """)
        await self.conn.commit()

    async def exists(self, topic: str, event_id: str) -> bool:
        async with self.lock:
            async with self.conn.execute(
                "SELECT 1 FROM dedup WHERE topic=? AND event_id=? LIMIT 1", (topic, event_id)
            ) as cur:
                row = await cur.fetchone()
                return row is not None

    async def mark(self, topic: str, event_id: str):
        async with self.lock:
            await self.conn.execute(
                "INSERT OR IGNORE INTO dedup (topic, event_id, received_at) VALUES (?, ?, ?)",
                (topic, event_id, time.time()),
            )
            await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None
