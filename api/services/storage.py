import json
import os
from api.config import DATA_DIR

os.makedirs(DATA_DIR, exist_ok=True)

def _path(paper_id: str) -> str:
    return f"{DATA_DIR}/{paper_id}.json"

def save_task(paper_id: str, data: dict):
    with open(_path(paper_id), "w") as f:
        json.dump(data, f)

def load_task(paper_id: str) -> dict | None:
    p = _path(paper_id)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)

def update_task(paper_id: str, updates: dict):
    data = load_task(paper_id) or {}
    data.update(updates)
    save_task(paper_id, data)
