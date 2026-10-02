import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "dashboard" / "rankings.json"
REVIEWS_FILE = Path(__file__).parent.parent / "dashboard" / "reviews.json"


def load() -> list:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())


def save(records: list) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(records, indent=2))


def append(new_records: list) -> int:
    existing = load()

    def key(r):
        return (r["date"], r["client"], r["location"], r["keyword"])

    existing_map = {key(r): i for i, r in enumerate(existing)}
    count = 0

    for r in new_records:
        k = key(r)
        if k in existing_map:
            # Merge: new record fields win (fills in organic_* on existing local-only records)
            merged = {**existing[existing_map[k]], **r}
            if merged != existing[existing_map[k]]:
                existing[existing_map[k]] = merged
                count += 1
        else:
            existing.append(r)
            count += 1

    save(existing)
    return count


# ── reviews ──

def load_reviews() -> list:
    if not REVIEWS_FILE.exists():
        return []
    return json.loads(REVIEWS_FILE.read_text())


def save_reviews(records: list) -> None:
    REVIEWS_FILE.parent.mkdir(parents=True, exist_ok=True)
    REVIEWS_FILE.write_text(json.dumps(records, indent=2))


def append_reviews(new_records: list) -> int:
    existing = load_reviews()

    def key(r):
        return (r["date"], r["client"], r["location"])

    existing_keys = {key(r) for r in existing}
    to_add = [r for r in new_records if key(r) not in existing_keys]
    save_reviews(existing + to_add)
    return len(to_add)
