#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.tracker import check_local_rank, check_organic_rank
from src.reviews import fetch_reviews
from src import db
from scripts.build_dashboard import build as build_dashboard


def main():
    serp_key = os.environ.get("SERPAPI_KEY")
    places_key = os.environ.get("GOOGLE_PLACES_API_KEY")

    if not serp_key:
        print("ERROR: SERPAPI_KEY not set in .env")
        sys.exit(1)
    if not places_key:
        print("WARNING: GOOGLE_PLACES_API_KEY not set — skipping review tracking")

    config_path = Path(__file__).parent.parent / "config" / "clients.json"
    clients = json.loads(config_path.read_text())

    # ── Rankings (local pack + organic) ──
    results = []
    col = "{:<20} {:<12} {:<40} {:>8} {:>9}"
    print("\n" + col.format("Client", "City", "Keyword", "Maps", "Organic"))
    print("-" * 93)

    for client in clients:
        city = client["location"].split(",")[0]
        for keyword in client["keywords"]:
            try:
                record = check_local_rank(
                    business_name=client["name"],
                    location=client["location"],
                    keyword=keyword,
                    api_key=serp_key,
                )
                organic = check_organic_rank(
                    business_name=client["name"],
                    location=client["location"],
                    keyword=keyword,
                    api_key=serp_key,
                )
                record.update(organic)
                results.append(record)

                maps = f"#{record['local_pack_position']}" if record["found"] else "N/R"
                web = f"#{organic['organic_position']}" if organic["organic_found"] else "N/R"
                print(col.format(client["name"], city, keyword, maps, web))
            except Exception as e:
                print(f"  ERROR — {client['name']} / {keyword}: {e}")

    rank_saved = db.append(results)
    print(f"\n✓ Rankings: {rank_saved} record(s) saved/updated")

    # ── Reviews (one per client, not per keyword) ──
    if places_key:
        review_results = []
        seen = set()
        print("\nFetching review stats…")

        for client in clients:
            key = (client["name"], client["location"])
            if key in seen:
                continue
            seen.add(key)
            city = client["location"].split(",")[0]
            try:
                review = fetch_reviews(client, places_key)
                review_results.append(review)
                rating = f"★{review['rating']}" if review["rating"] else "N/A"
                count = f"{review['review_count']} reviews" if review["review_count"] else "N/A"
                print(f"  {client['name']} ({city}): {rating}  {count}")
            except Exception as e:
                print(f"  ERROR — {client['name']} reviews: {e}")

        reviews_saved = db.append_reviews(review_results)
        print(f"✓ Reviews: {reviews_saved} record(s) saved")

        clients = json.loads(config_path.read_text())

    build_dashboard()


if __name__ == "__main__":
    main()
