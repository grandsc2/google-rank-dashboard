#!/usr/bin/env python3
"""
Export per-client ranking snapshots to reports/<date>/<slug>.json
Run after run_check.py to save individual client files.
"""
import json
import re
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))
from src import db


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def main():
    today = date.today().isoformat()
    all_records = db.load()
    today_records = [r for r in all_records if r["date"] == today]

    if not today_records:
        print(f"No records found for {today}. Run scripts/run_check.py first.")
        sys.exit(1)

    # Group by client + location
    groups: dict[str, list] = {}
    for r in today_records:
        key = f"{r['client']}||{r['location']}"
        groups.setdefault(key, []).append(r)

    out_dir = Path(__file__).parent.parent / "reports" / today
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nExporting reports to reports/{today}/\n")
    for key, records in groups.items():
        client_name = records[0]["client"]
        location = records[0]["location"].split(",")[0]  # just city
        filename = slugify(f"{client_name}_{location}") + ".json"

        report = {
            "client": client_name,
            "location": records[0]["location"],
            "date": today,
            "rankings": [
                {
                    "keyword": r["keyword"],
                    "position": r["local_pack_position"],
                    "found": r["found"],
                }
                for r in sorted(records, key=lambda x: x["keyword"])
            ],
        }

        (out_dir / filename).write_text(json.dumps(report, indent=2))
        print(f"  ✓ {filename}")
        for r in report["rankings"]:
            pos = f"#{r['position']}" if r["found"] else "N/R"
            print(f"      {r['keyword']:<45} {pos}")
        print()

    print(f"Saved {len(groups)} report(s) to reports/{today}/")


if __name__ == "__main__":
    main()
