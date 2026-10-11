#!/usr/bin/env python3
"""
One-time OAuth authorization for Google Business Profile API.
Run this once to generate a refresh token stored in .env.

  python scripts/auth_gbp.py

A browser window will open — log in as the GBP manager account.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/business.manage"]
CLIENT_SECRETS = Path(__file__).parent.parent / "credentials" / "gbp_oauth_client.json"
ENV_FILE = Path(__file__).parent.parent / ".env"


def main():
    if not CLIENT_SECRETS.exists():
        print("ERROR: credentials/gbp_oauth_client.json not found.")
        print("Download it from Google Cloud Console → Credentials → OAuth client → Download JSON")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
    creds = flow.run_local_server(port=0)

    env_text = ENV_FILE.read_text() if ENV_FILE.exists() else ""
    lines = [l for l in env_text.splitlines() if not l.startswith("GBP_REFRESH_TOKEN=")]
    lines.append(f"GBP_REFRESH_TOKEN={creds.refresh_token}")
    ENV_FILE.write_text("\n".join(lines) + "\n")

    print(f"✓ Refresh token saved to .env")
    print(f"\nNext: run  python scripts/discover_gbp_locations.py  to find the Han's Noodles location ID")


if __name__ == "__main__":
    main()
