import json
import os
import tempfile
from pathlib import Path

from .config import DATA_FILE, DEFAULT_SETTINGS


def load(path=DATA_FILE):
    empty = {"settings": dict(DEFAULT_SETTINGS), "skills": []}
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return empty
    if not isinstance(raw, dict):
        return empty
    settings, skills = raw.get("settings"), raw.get("skills")
    return {
        "settings": {**DEFAULT_SETTINGS, **(settings if isinstance(settings, dict) else {})},
        "skills": skills if isinstance(skills, list) else [],
    }


def save(data, path=DATA_FILE):
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.resolve().parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise
