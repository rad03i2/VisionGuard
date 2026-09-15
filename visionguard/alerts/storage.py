"""
Persistent SQLite audit and incident storage engine.
"""

import sqlite3
import os
import time
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("visionguard.storage")


class SQLiteEventStore:
    """Stores security events, intrusion breaches, and snapshot metadata in a local SQLite database."""

    def __init__(self, db_path: str = "events.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone_id TEXT NOT NULL,
                    zone_name TEXT NOT NULL,
                    track_id INTEGER NOT NULL,
                    class_name TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    is_loitering INTEGER NOT NULL,
                    snapshot_path TEXT,
                    timestamp REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()
            logger.info(f"SQLite event store initialized at [{self.db_path}]")
        finally:
            conn.close()

    def record_event(
        self,
        zone_id: str,
        zone_name: str,
        track_id: int,
        class_name: str,
        duration_seconds: float,
        is_loitering: bool,
        snapshot_path: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> int:
        ts = timestamp or time.time()
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO security_events (
                    zone_id, zone_name, track_id, class_name,
                    duration_seconds, is_loitering, snapshot_path, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    zone_id,
                    zone_name,
                    track_id,
                    class_name,
                    duration_seconds,
                    1 if is_loitering else 0,
                    snapshot_path,
                    ts,
                ),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent incident events."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, zone_id, zone_name, track_id, class_name,
                       duration_seconds, is_loitering, snapshot_path, timestamp, created_at
                FROM security_events
                ORDER BY id DESC
                LIMIT ?
            """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
