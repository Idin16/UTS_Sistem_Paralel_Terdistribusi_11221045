import aiosqlite
import os

class DedupStore:
    """SQLite-based deduplication store (async, persistent)."""

    def __init__(self, db_path: str = "data/dedup.db"):
        self.db_path = db_path

    async def init(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            # Buat tabel jika belum ada
            await db.execute("""
                CREATE TABLE IF NOT EXISTS dedup (
                    topic TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    PRIMARY KEY (topic, event_id)
                )
            """)
            await db.commit()

    async def exists(self, topic: str, event_id: str) -> bool:
        """Check if event (topic, event_id) already exists."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM dedup WHERE topic = ? AND event_id = ? LIMIT 1",
                (topic, event_id)
            ) as cursor:
                row = await cursor.fetchone()
                return row is not None

    async def mark(self, topic: str, event_id: str):
        """Mark an event as processed (insert into dedup)."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO dedup (topic, event_id) VALUES (?, ?)",
                (topic, event_id)
            )
            await db.commit()
