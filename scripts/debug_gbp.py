#!/usr/bin/env python3
import json, os, sys, requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

CLIENT_SECRETS = Path(__file__).parent.parent / "credentials" / "gbp_oauth_client.json"

def get_token(refresh_token):
    secrets = json.loads(CLIENT_SECRETS.read_text())["installed"]
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": secrets["client_id"],
        "client_secret": secrets["client_secret"],
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    })
    print("Token exchange:", resp.status_code)
    if not resp.ok:
        print(resp.text)
        return None
    data = resp.json()
    print("Scopes granted:", data.get("scope"))
    return data["access_token"]

def try_api(url, token, label):
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    print(f"\n{label}")
    print(f"  Status: {resp.status_code}")
    print(f"  Body:   {resp.text[:500]}")

token = get_token(os.environ["GBP_REFRESH_TOKEN"])
if not token:
    sys.exit(1)

try_api("https://mybusinessaccountmanagement.googleapis.com/v1/accounts", token, "Account Management API")
try_api("https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses", token, "Logged-in account (sanity check)")
