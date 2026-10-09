import requests

BASE_URL = "https://ch.tetr.io/api"
HEADERS = {"User-Agent": "tetrstats/0.1"}
TIMEOUT = 10


def api_get(endpoint):
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
    user = api_get(f"users/{username}")

    if user is None:
        print(f"Player '{username}' was not found.")

    return user


def get_league(username):
    league = api_get(f"users/{username}/summaries/league")

    if league is None:
        print(f"Player '{username}' was not found.")

    return league

def get_zenith(username):
    zenith = api_get(f"users/{username}/summaries/zenith")

    if zenith is None:
        print(f"Player '{username}' was not found.")

    return zenith

def get_zenithex(username):
    zenithex = api_get(f"users/{username}/summaries/zenithex")

    if zenithex is None:
        print(f"Player '{username}' was not found.")

    return zenithex