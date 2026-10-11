#!/usr/bin/env python3
"""
Fetch Google Business Profile Performance API metrics.
Returns weekly totals for impressions, calls, direction requests, website clicks.
"""
import json
import requests
from datetime import date, timedelta
from pathlib import Path

TOKEN_URL = "https://oauth2.googleapis.com/token"
PERFORMANCE_URL = "https://businessprofileperformance.googleapis.com/v1/{}:getDailyMetricsSummary"
CLIENT_SECRETS = Path(__file__).parent.parent / "credentials" / "gbp_oauth_client.json"

METRICS = [
    "BUSINESS_IMPRESSIONS_DESKTOP_MAPS",
    "BUSINESS_IMPRESSIONS_MOBILE_MAPS",
    "BUSINESS_IMPRESSIONS_DESKTOP_SEARCH",
    "BUSINESS_IMPRESSIONS_MOBILE_SEARCH",
    "CALL_CLICKS",
    "DIRECTION_REQUESTS",
    "WEBSITE_CLICKS",
]


def get_access_token(refresh_token: str) -> str:
    secrets = json.loads(CLIENT_SECRETS.read_text())["installed"]
    resp = requests.post(TOKEN_URL, data={
        "client_id": secrets["client_id"],
        "client_secret": secrets["client_secret"],
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    })
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_weekly_performance(location_id: str, refresh_token: str) -> dict:
    """Fetch last 7 days of performance metrics for a GBP location."""
    token = get_access_token(refresh_token)
    headers = {"Authorization": f"Bearer {token}"}

    end = date.today()
    start = end - timedelta(days=7)

    totals = {}
    for metric in METRICS:
        params = {
            "dailyMetric": metric,
            "dailyRange.start_date.year": start.year,
            "dailyRange.start_date.month": start.month,
            "dailyRange.start_date.day": start.day,
            "dailyRange.end_date.year": end.year,
            "dailyRange.end_date.month": end.month,
            "dailyRange.end_date.day": end.day,
        }
        resp = requests.get(PERFORMANCE_URL.format(location_id), headers=headers, params=params)
        if resp.ok:
            dated_values = resp.json().get("timeSeries", {}).get("datedValues", [])
            totals[metric] = sum(int(d.get("value", 0)) for d in dated_values if d.get("value"))
        else:
            totals[metric] = None

    # Aggregate into cleaner keys
    return {
        "date": end.isoformat(),
        "maps_impressions": (totals.get("BUSINESS_IMPRESSIONS_DESKTOP_MAPS") or 0)
                          + (totals.get("BUSINESS_IMPRESSIONS_MOBILE_MAPS") or 0),
        "search_impressions": (totals.get("BUSINESS_IMPRESSIONS_DESKTOP_SEARCH") or 0)
                            + (totals.get("BUSINESS_IMPRESSIONS_MOBILE_SEARCH") or 0),
        "call_clicks": totals.get("CALL_CLICKS"),
        "direction_requests": totals.get("DIRECTION_REQUESTS"),
        "website_clicks": totals.get("WEBSITE_CLICKS"),
    }
