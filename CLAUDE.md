# google_rank_dashboard — CLAUDE.md

## What this project is
Weekly Google local SEO rank tracker for a GBP/SEO agency. Tracks Google Local Pack positions, review ratings, and review counts for Chinese restaurant clients in the DFW area.

## Clients
Configured in `config/clients.json`. Place IDs are already discovered and cached — **do not trigger place ID re-discovery** unless a client is new or a place_id is explicitly null.

| Client | Location | Place ID cached |
|--------|----------|-----------------|
| Zhang's Bistro | Carrollton, TX | ✓ |
| Yo! Bowl | Carrollton, TX | ✓ |
| Yo! Bowl | Plano, TX | ✓ |
| Han's Noodles | Carrollton, TX | ✓ |

## Data pipeline — always follow this order

### 1. Collect fresh data (weekly, or on demand)
```bash
python scripts/run_check.py
```
- Calls SerpAPI for Map Search position per keyword (~24 API calls)
- Calls Google Places API for rating + review count per client (4 calls)
- **Appends** results to `dashboard/data.json` — never overwrites, never replaces

### 2. Build the dashboard
```bash
python scripts/build_dashboard.py
```
- Reads ALL historical records from `dashboard/data.json`
- Inlines `rankings`, `reviews`, Chart.js, and logo into `dashboard/index.html`
- **Always embeds the full history** — charts plot every data point ever collected

### 3. Publish the artifact
Republish `dashboard/index.html` to `https://claude.ai/artifact/WBuM9RvVMmr62u27fdbL6e`.
No supporting files needed — everything is inlined by step 2.

**For dashboard UI changes only** (no new data): skip step 1, run steps 2 and 3.

## Data file
- **`dashboard/data.json`** — single source of truth, structure: `{"rankings": [...], "reviews": [...]}`
  - `rankings`: upsert by `(date, client, location, keyword)` via `src/db.py:append()`
  - `reviews`: dedup by `(date, client, location)` via `src/db.py:append_reviews()`
  - `config/clients.json` — place_ids cached here; auto-updated on first discovery

**Never manually edit data.json. Never truncate or replace it. It is append-only.**

## Automation
`.github/workflows/weekly_rank_check.yml` runs every Monday 6am UTC:
1. `python scripts/run_check.py` (collects + appends + builds dashboard)
2. Commits `dashboard/data.json` + `dashboard/index.html` + `config/clients.json`

## API budget (free tiers)
- **SerpAPI**: 100 searches/month free. Each weekly run uses ~24 searches (12 keywords × 2: local + organic). Never run more than once per week unless explicitly requested.
- **Google Places API**: $200/month credit. Place IDs are cached so each run costs only 4 `place/details` calls.

## Brand / design
- Dashboard title: "Client Performance Tracking, powered by Local Buzz Marketing"
- Primary accent: `#F47820` (orange, from logo)
- Dark mode accent: `#FF9838`
- Logo: `logo-icon.png` (repo root) — inlined as base64 by build script
- Chart.js: inlined from `vendor/chart.umd.min.js` (no CDN dependency)
- Chart series palette: Okabe-Ito CVD-safe — `#0072B2`, `#E69F00`, `#009E73`
- Layout: rank chart full-width, rating + review count side-by-side below

## SerpAPI location format
Must use canonical SerpAPI location strings, NOT abbreviations:
- ✓ `"Carrollton,Texas,United States"`
- ✗ `"Carrollton, TX"`
Validate new locations via: `https://serpapi.com/locations.json?q=<city>&limit=5`
