import requests
from datetime import date
from difflib import SequenceMatcher

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


def _normalize(name: str) -> str:
    return name.lower().replace("!", "").replace("'", "").replace(".", "").replace("-", " ").strip()


def _name_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def check_organic_rank(business_name: str, location: str, keyword: str, api_key: str) -> dict:
    params = {
        "engine": "google",
        "q": keyword,
        "location": location,
        "hl": "en",
        "gl": "us",
        "num": 20,
        "api_key": api_key,
    }
    resp = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()

    organic_results = resp.json().get("organic_results", [])

    best_position = None
    best_score = 0.0

    for result in organic_results:
        score = _name_similarity(business_name, result.get("title", ""))
        if score > best_score:
            best_score = score
            if score >= 0.6:
                best_position = result.get("position")

    return {
        "organic_position": best_position,
        "organic_found": best_position is not None,
    }


def check_local_rank(business_name: str, location: str, keyword: str, api_key: str) -> dict:
    params = {
        "engine": "google_local",
        "q": keyword,
        "location": location,
        "hl": "en",
        "gl": "us",
        "api_key": api_key,
    }
    resp = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    local_results = data.get("local_results", [])

    best_position = None
    best_score = 0.0

    for result in local_results:
        title = result.get("title", "")
        score = _name_similarity(business_name, title)
        if score > best_score:
            best_score = score
            if score >= 0.6:
                best_position = result.get("position")

    return {
        "date": date.today().isoformat(),
        "client": business_name,
        "location": location,
        "keyword": keyword,
        "local_pack_position": best_position,
        "found": best_position is not None,
        "match_score": round(best_score, 3),
    }
