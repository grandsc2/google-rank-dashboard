# google_rank_dashboard — CLAUDE.md

## What this project is
Weekly Google local SEO rank tracker for a GBP/SEO agency. Tracks Google Local Pack positions, organic search positions, review ratings, and review counts for Chinese restaurant clients in the DFW area.

## Clients
Configured in `config/clients.json`. Place IDs are already discovered and cached — **do not trigger place ID re-discovery** unless a client is new or a place_id is explicitly null.

| Client | Location | Place ID cached |
|--------|----------|-----------------|
| Zhang's Bistro | Carrollton, TX | ✓ |
| Yo! Bowl | Carrollton, TX | ✓ |
| Yo! Bowl | Plano, TX | ✓ |
| Han's Noodles | Carrollton, TX | ✓ |

## Data files — always additive, never replace
- `dashboard/rankings.json` — all historical rank records (local pack + organic). Append only via `src/db.py:append()` which upserts by `(date, client, location, keyword)`.
- `dashboard/reviews.json` — weekly rating + review count snapshots. Append only via `src/db.py:append_reviews()`.
- `config/clients.json` — client config with cached place_ids. Auto-updated by `src/reviews.py` on first discovery.

**Do not run `scripts/run_check.py` to populate dashboard data for sessions that are only updating the UI.** The data files are already populated. Load them directly.

## Updating the dashboard only (no new data needed)
Edit `dashboard/index.html`, then republish the artifact at `https://claude.ai/artifact/WBuM9RvVMmr62u27fdbL6e` using:
```
files: {
  "rankings.json": {"from": "dashboard/rankings.json"},
  "reviews.json":  {"from": "dashboard/reviews.json"},
  "logo-icon.png": {"from": "dashboard/logo-icon.png"}
}
```

## Running a fresh weekly check
```bash
python scripts/run_check.py   # local pack + organic rank + reviews
python scripts/export_reports.py  # per-client JSON snapshots → reports/<date>/
```
This is automated via `.github/workflows/weekly_rank_check.yml` every Monday 6am UTC.

## API budget (free tiers)
- **SerpAPI**: 100 searches/month free. Each weekly run uses ~24 searches (12 keywords × 2: local + organic). Never run more than once per week unless explicitly requested.
- **Google Places API**: $200/month credit (very generous). Place IDs are cached after first discovery so each subsequent run costs only 4 `place/details` calls.

## Brand / design
- Primary accent: `#F47820` (orange, from logo)
- Dark mode accent: `#FF9838`
- Logo: `dashboard/logo-icon.png` (also at repo root `logo-icon.png`)
- Chart series palette: Okabe-Ito CVD-safe — `#0072B2`, `#E69F00`, `#009E73`

## SerpAPI location format
Must use canonical SerpAPI location strings, NOT abbreviations:
- ✓ `"Carrollton,Texas,United States"`
- ✗ `"Carrollton, TX"`
Validate new locations via: `https://serpapi.com/locations.json?q=<city>&limit=5`
