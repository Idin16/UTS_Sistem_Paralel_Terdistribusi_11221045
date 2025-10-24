import sqlite3, threading
from datetime import datetime

class DedupStore:
    def __init__(self, path="data/dedup.db"):
        self.path = path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS dedup (
                    topic TEXT,
                    event_id TEXT,
                    processed_at TEXT,
                    PRIMARY KEY(topic, event_id)
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT, event_id TEXT, timestamp TEXT, source TEXT, payload TEXT
                )
            """)
            conn.commit()

    def is_duplicate(self, topic, event_id):
        with self._lock, sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            c.execute("SELECT 1 FROM dedup WHERE topic=? AND event_id=?", (topic, event_id))
            return c.fetchone() is not None

    def mark_processed(self, topic, event_id):
        now = datetime.utcnow().isoformat() + "Z"
        with self._lock, sqlite3.connect(self.path) as conn:
            conn.execute("INSERT OR IGNORE INTO dedup VALUES (?,?,?)", (topic, event_id, now))
            conn.commit()

    def add_event(self, topic, event_id, ts, src, payload):
        with self._lock, sqlite3.connect(self.path) as conn:
            conn.execute("INSERT INTO events (topic,event_id,timestamp,source,payload) VALUES (?,?,?,?,?)",
                         (topic, event_id, ts, src, payload))
            conn.commit()

    def list_events(self, topic=None):
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            if topic:
                c.execute("SELECT topic,event_id,timestamp,source,payload FROM events WHERE topic=?", (topic,))
            else:
                c.execute("SELECT topic,event_id,timestamp,source,payload FROM events")
            return [{"topic": t, "event_id": e, "timestamp": ts, "source": s, "payload": p}
                    for t, e, ts, s, p in c.fetchall()]
