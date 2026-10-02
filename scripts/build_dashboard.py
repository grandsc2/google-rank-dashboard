#!/usr/bin/env python3
"""
Inline rankings.json and reviews.json into dashboard/index.html so the
dashboard works without a fetch() call (required for the artifact sandbox
and speeds up GitHub Pages load).

Run after every run_check.py, or standalone:
  python scripts/build_dashboard.py
"""
import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
HTML = ROOT / "dashboard" / "index.html"


def build():
    raw      = json.loads((ROOT / "dashboard" / "data.json").read_text())
    rankings = raw.get("rankings", raw) if isinstance(raw, dict) else raw
    reviews  = raw.get("reviews", [])  if isinstance(raw, dict) else []
    html     = HTML.read_text()

    def inject_json(src, key, data):
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

    def inject_chartjs(src):
        vendor = ROOT / "vendor" / "chart.umd.min.js"
        if not vendor.exists():
            return src
        js = vendor.read_text()
        blob = f"<!-- INJECT:chartjs --><script>{js}</script><!-- /INJECT:chartjs -->"
        return re.sub(
            r"<!-- INJECT:chartjs -->.*?<!-- /INJECT:chartjs -->",
            lambda _: blob,
            src,
            flags=re.DOTALL,
        )

    def inject_logo(src):
        logo_path = ROOT / "logo-icon.png"
        if not logo_path.exists():
            logo_path = ROOT / "dashboard" / "logo-icon.png"
        if not logo_path.exists():
            return src
        b64 = base64.b64encode(logo_path.read_bytes()).decode()
        data_uri = f"data:image/png;base64,{b64}"
        replacement = f'<!-- INJECT:logo --><img src="{data_uri}" style="width:32px;height:32px;object-fit:contain" alt=""><!-- /INJECT:logo -->'
        return re.sub(
            r"<!-- INJECT:logo -->.*?<!-- /INJECT:logo -->",
            replacement,
            src,
            flags=re.DOTALL,
        )

    html = inject_json(html, "rankings", rankings)
    html = inject_json(html, "reviews",  reviews)
    html = inject_logo(html)
    html = inject_chartjs(html)
    HTML.write_text(html)

    print(f"✓ Dashboard built — {len(rankings)} rank records, {len(reviews)} review records inlined, logo embedded, Chart.js inlined")


if __name__ == "__main__":
    build()
