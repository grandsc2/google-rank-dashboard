import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "dashboard" / "data.json"


def _load() -> dict:
    if not DATA_FILE.exists():
        return {"rankings": [], "reviews": []}
    raw = json.loads(DATA_FILE.read_text())
    # Support legacy flat-array format (rankings.json before migration)
    if isinstance(raw, list):
        return {"rankings": raw, "reviews": []}
    return raw


def _save(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2))


def load() -> list:
    return _load()["rankings"]


def append(new_records: list) -> int:
    data = _load()
    existing = data["rankings"]

    def key(r):
        return (r["date"], r["client"], r["location"], r["keyword"])

    existing_map = {key(r): i for i, r in enumerate(existing)}
    count = 0

    for r in new_records:
        k = key(r)
        if k in existing_map:
            merged = {**existing[existing_map[k]], **r}
            if merged != existing[existing_map[k]]:
                existing[existing_map[k]] = merged
                count += 1
        else:
            existing.append(r)
            count += 1

    data["rankings"] = existing
    _save(data)
    return count


def load_reviews() -> list:
    return _load()["reviews"]


def append_reviews(new_records: list) -> int:
    data = _load()
    existing = data["reviews"]

    def key(r):
        return (r["date"], r["client"], r["location"])

    existing_keys = {key(r) for r in existing}
    to_add = [r for r in new_records if key(r) not in existing_keys]
    data["reviews"] = existing + to_add
    _save(data)
    return len(to_add)
