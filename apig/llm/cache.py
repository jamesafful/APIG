from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any


def _hash_payload(payload: Dict[str, Any]) -> str:
    """Stable hash for a JSON-serializable payload."""
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class LLMCache:
    """SQLite-backed cache for LLM calls.

    Caching is essential for reproducibility (and cost control). The cache key is
    a hash of the full request payload including:
    - provider
    - model
    - system + user messages
    - decoding parameters
    """

    path: Path

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_cache (
                k TEXT PRIMARY KEY,
                v TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def make_key(self, payload: Dict[str, Any]) -> str:
        return _hash_payload(payload)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        cur = self._conn.execute("SELECT v FROM llm_cache WHERE k=?", (key,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row[0])

    def set(self, key: str, value: Dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO llm_cache (k, v) VALUES (?, ?)",
            (key, json.dumps(value, ensure_ascii=False)),
        )
        self._conn.commit()

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass
