import json
import requests
from datetime import date
from pathlib import Path

FIND_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def _discover_place_id(business_name: str, location: str, api_key: str) -> str | None:
    city = location.split(",")[0].strip()
    state = location.split(",")[1].strip() if "," in location else ""
    resp = requests.get(
        FIND_URL,
        params={
            "input": f"{business_name} {city} {state}",
            "inputtype": "textquery",
            "fields": "place_id,name,formatted_address",
            "key": api_key,
        },
        timeout=10,
    )
    resp.raise_for_status()
    candidates = resp.json().get("candidates", [])
    return candidates[0]["place_id"] if candidates else None


def _cache_place_id(client_name: str, location: str, place_id: str) -> None:
    config_path = Path(__file__).parent.parent / "config" / "clients.json"
    clients = json.loads(config_path.read_text())
    for c in clients:
        if c["name"] == client_name and c["location"] == location:
            c["place_id"] = place_id
            break
    config_path.write_text(json.dumps(clients, indent=2))


def fetch_reviews(client: dict, api_key: str) -> dict:
    place_id = client.get("place_id")

    if not place_id:
        place_id = _discover_place_id(client["name"], client["location"], api_key)
        if place_id:
            _cache_place_id(client["name"], client["location"], place_id)

    if not place_id:
        return {
            "date": date.today().isoformat(),
            "client": client["name"],
            "location": client["location"],
            "place_id": None,
            "rating": None,
            "review_count": None,
        }

    resp = requests.get(
        DETAILS_URL,
        params={
            "place_id": place_id,
            "fields": "rating,user_ratings_total,name",
            "key": api_key,
        },
        timeout=10,
    )
    resp.raise_for_status()
    result = resp.json().get("result", {})

    return {
        "date": date.today().isoformat(),
        "client": client["name"],
        "location": client["location"],
        "place_id": place_id,
        "rating": result.get("rating"),
        "review_count": result.get("user_ratings_total"),
    }
