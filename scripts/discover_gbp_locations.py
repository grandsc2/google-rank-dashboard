#!/usr/bin/env python3
"""
List all GBP locations accessible with the authorized account.
Run after auth_gbp.py to find the location ID for Han's Noodles.

  python scripts/discover_gbp_locations.py
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

import requests

CLIENT_SECRETS = Path(__file__).parent.parent / "credentials" / "gbp_oauth_client.json"
TOKEN_URL = "https://oauth2.googleapis.com/token"


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


def main():
    refresh_token = os.environ.get("GBP_REFRESH_TOKEN")
    if not refresh_token:
        print("ERROR: GBP_REFRESH_TOKEN not in .env — run  python scripts/auth_gbp.py  first")
        sys.exit(1)

    token = get_access_token(refresh_token)
    headers = {"Authorization": f"Bearer {token}"}

    # List accounts
    accounts_resp = requests.get(
        "https://mybusinessaccountmanagement.googleapis.com/v1/accounts",
        headers=headers,
    )
    accounts_resp.raise_for_status()
    accounts = accounts_resp.json().get("accounts", [])

    if not accounts:
        print("No GBP accounts found for this Google account.")
        return

    print(f"\nFound {len(accounts)} account(s):\n")

    for account in accounts:
        print(f"  Account: {account['name']}  ({account.get('accountName', '')})")

        # List locations in this account
        loc_resp = requests.get(
            f"https://mybusinessbusinessinformation.googleapis.com/v1/{account['name']}/locations",
            headers=headers,
            params={"readMask": "name,title"},
        )
        if not loc_resp.ok:
            print(f"    Could not list locations: {loc_resp.text}")
            continue

        locations = loc_resp.json().get("locations", [])
        if not locations:
            print("    No locations found.")
            continue

        for loc in locations:
            print(f"    ✓ {loc.get('title', '(no title)')}")
            print(f"      Location ID: {loc['name']}")

    print("\nCopy the Location ID for Han's Noodles and add it to config/clients.json as 'gbp_location_id'.")


if __name__ == "__main__":
    main()
