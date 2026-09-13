"""
Lightweight JSON-file storage layer.

This replaces a relational database for this project's scope: all data
(users, transactions, budgets, predictions, insights) lives in one JSON
file at data_store/db.json. A process-wide lock guards every read-modify-
write cycle so concurrent requests don't corrupt the file.

This trades scalability for zero setup -- fine for a fresher/portfolio
project with a single-process dev server. It is not a substitute for a
real database in production (no indexing, no concurrent-writer safety
across multiple processes, whole file rewritten on every write).
"""
import json
import os
import threading
from contextlib import contextmanager
from typing import Any, Dict

from app.config import DATA_FILE, DATA_DIR

_lock = threading.Lock()

_EMPTY_DB: Dict[str, Any] = {
    "users": [],
    "transactions": [],
    "budgets": [],
    "predictions": [],
    "insights": [],
    "counters": {
        "users": 0,
        "transactions": 0,
        "budgets": 0,
        "predictions": 0,
        "insights": 0,
    },
}


def init_db() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        _write(json.loads(json.dumps(_EMPTY_DB)))


def _read() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        return json.loads(json.dumps(_EMPTY_DB))
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return json.loads(json.dumps(_EMPTY_DB))
        return json.loads(content)


def _write(db: Dict[str, Any]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp_path = DATA_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)
    os.replace(tmp_path, DATA_FILE)


@contextmanager
def json_db():
    """
    Usage:
        with json_db() as db:
            db["users"].append(...)
    Loads the whole file, yields it for reading/mutating, then writes it
    back once the block exits. Held under a process-wide lock throughout.
    """
    with _lock:
        db = _read()
        yield db
        _write(db)


def next_id(db: Dict[str, Any], table: str) -> int:
    db["counters"][table] += 1
    return db["counters"][table]
