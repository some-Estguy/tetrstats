
import requests

BASE_URL = "https://ch.tetr.io/api"
HEADERS = {"User-Agent": "tetrstats/0.1"}
TIMEOUT = 10


def api_get(endpoint):
    """Fetch data from the TETR.IO API."""
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    if response.status_code == 404:
        return None

    payload = response.json()

    if not isinstance(payload, dict):
        raise ValueError(f"Unexpected API response format: {endpoint}")

    if not payload.get("success"):
        raise ValueError(f"TETR.IO API request failed: {endpoint}")

    if "data" not in payload:
        raise ValueError(f"API response has no data field: {endpoint}")

    return payload["data"]


def get_user(username):
    """Return a user's profile, or None if not found."""
    user = api_get(f"users/{username}")

    if user is None:
        print(f"Player '{username}' was not found.")

    return user


def get_league(username):
    """Return a user's league stats, or None if not found."""
    league = api_get(f"users/{username}/summaries/league")

    if league is None:
        print(f"Player '{username}' was not found.")

    return league