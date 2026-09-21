from __future__ import annotations

import json
from pathlib import Path

from app.models import Task

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TASKS_PATH = DATA_DIR / "tasks.json"


def load_tasks() -> list[Task]:
    if not TASKS_PATH.exists():
        return []
    raw = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    return [Task.from_dict(item) for item in raw]


def save_tasks(tasks: list[Task]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = [task.to_dict() for task in tasks]
    TASKS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
