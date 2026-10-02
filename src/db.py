import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "dashboard" / "rankings.json"


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

    existing_keys = {key(r) for r in existing}
    to_add = [r for r in new_records if key(r) not in existing_keys]
    save(existing + to_add)
    return len(to_add)
