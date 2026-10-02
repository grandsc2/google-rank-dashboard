#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.tracker import check_local_rank
from src import db


def main():
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        print("ERROR: SERPAPI_KEY not set in environment or .env file")
        sys.exit(1)

    config_path = Path(__file__).parent.parent / "config" / "clients.json"
    clients = json.loads(config_path.read_text())

    results = []
    col = "{:<25} {:<18} {:<42} {:>8}"
    print("\n" + col.format("Client", "Location", "Keyword", "Position"))
    print("-" * 97)

    for client in clients:
        for keyword in client["keywords"]:
            try:
                result = check_local_rank(
                    business_name=client["name"],
                    location=client["location"],
                    keyword=keyword,
                    api_key=api_key,
                )
                results.append(result)
                pos = str(result["local_pack_position"]) if result["found"] else "N/R"
                print(col.format(client["name"], client["location"], keyword, pos))
            except Exception as e:
                print(f"  ERROR — {client['name']} / {keyword}: {e}")

    added = db.append(results)
    print(f"\n✓ Saved {added} new record(s) to dashboard/rankings.json")


if __name__ == "__main__":
    main()
