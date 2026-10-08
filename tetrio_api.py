import requests

def get_user(username):
    r = requests.get("https://ch.tetr.io/api/users/" + username, headers={"User-Agent": "tetrstats/0.1"}, timeout=10)
    
    if r.status_code == 404:
        print(f"Player '{username}' was not found.")
        return None
    
    r.raise_for_status()
    data = r.json()["data"]
    return data

def get_league(username):
    r = requests.get("https://ch.tetr.io/api/users/" + username + "/summaries/league", headers={"User-Agent": "tetrstats/0.1"}, timeout=10)
    if r.status_code == 404:
        print(f"Player '{username}' was not found.")
        return None
    
    r.raise_for_status()
    data = r.json()["data"]
    return data