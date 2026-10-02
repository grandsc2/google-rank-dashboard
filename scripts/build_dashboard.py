#!/usr/bin/env python3
"""
Inline rankings.json and reviews.json into dashboard/index.html so the
dashboard works without a fetch() call (required for the artifact sandbox
and speeds up GitHub Pages load).

Run after every run_check.py, or standalone:
  python scripts/build_dashboard.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
HTML = ROOT / "dashboard" / "index.html"


def build():
    rankings = json.loads((ROOT / "dashboard" / "rankings.json").read_text())
    reviews  = json.loads((ROOT / "dashboard" / "reviews.json").read_text())
    html     = HTML.read_text()

    def inject(src, key, data):
        replacement = (
            f"<!-- INJECT:{key} -->"
            f"<script>window.__{key.upper()}__={json.dumps(data, separators=(',', ':'))}</script>"
            f"<!-- /INJECT:{key} -->"
        )
        return re.sub(
            rf"<!-- INJECT:{key} -->.*?<!-- /INJECT:{key} -->",
            replacement,
            src,
            flags=re.DOTALL,
        )

    html = inject(html, "rankings", rankings)
    html = inject(html, "reviews",  reviews)
    HTML.write_text(html)

    print(f"✓ Dashboard built — {len(rankings)} rank records, {len(reviews)} review records inlined")


if __name__ == "__main__":
    build()
