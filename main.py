from tetrio_api import get_user, get_league
import sys
import requests
from datetime import datetime, timezone


# ---------- Helpers ----------

def show(label, value):
    """Print a stat, replacing missing values with None."""
    if value is None or value == "":
        value = "None"
    print(f"{label:<19} {value}")


def rounded(value):
    """Round a number safely."""
    if isinstance(value, (int, float)):
        return round(value)
    return value if value is not None else "None"


def win_rate(wins, games):
    """Calculate win percentage safely."""
    if isinstance(wins, (int, float)) and isinstance(games, (int, float)) and games > 0:
        return f"{wins / games * 100:.2f}%"
    return "None"


def format_date(value):
    """Format an ISO date or Unix timestamp when possible."""
    if value is None:
        return "None"

    try:
        if isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(value, tz=timezone.utc)
        elif isinstance(value, str):
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            return str(value)

        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, TypeError, OverflowError, OSError):
        return str(value)


# ---------- Arguments ----------

if len(sys.argv) < 2:
    print("Usage: python3 main.py <username>")
    sys.exit(1)

username = sys.argv[1].strip()

if not username:
    print("Error: Username cannot be empty.")
    sys.exit(1)


# ---------- Fetch API data ----------

try:
    user = get_user(username)

    if user is None:
        sys.exit(1)

    league = get_league(username)

    if league is None:
        print("Error: Could not retrieve Tetra League stats.")
        sys.exit(1)

except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
    sys.exit(1)

except (ValueError, KeyError) as e:
    print(f"Error: Unexpected or invalid API response ({e}).")
    sys.exit(1)


# ---------- Calculated values ----------

gametime = user.get("gametime") or 0
hours = int(gametime // 3600)
minutes = int((gametime % 3600) // 60)
seconds = int(gametime % 60)

games_played = user.get("gamesplayed")
games_won = user.get("gameswon")

league_games = league.get("gamesplayed")
league_wins = league.get("gameswon")

past = league.get("past") or {}
badges = user.get("badges") or []
oldusernames = user.get("oldusernames") or []
connections = user.get("connections") or {}


# ---------- Header ----------

print()
print("╔══════════════════════════════╗")
print("║        TETR.IO STATS         ║")
print("╚══════════════════════════════╝")


# ---------- Profile ----------

print("\n--- Profile ---")

show("Player ID:", user.get("_id"))
show("Username:", user.get("username", username))
show("Role:", user.get("role"))
show("Country:", user.get("country"))
show("Bio:", user.get("bio"))
show("Distinguishment:", user.get("distinguishment"))
show("Created:", format_date(user.get("created_at")))
show("Last API update:", format_date(user.get("ts")))


# ---------- Overall Activity ----------

print("\n--- Overall Activity ---")

show("XP:", user.get("xp"))
show("Games Played:", games_played)
show("Games Won:", games_won)
show("Win Rate:", win_rate(games_won, games_played))
show("Games Lost:", (
    games_played - games_won
    if isinstance(games_played, (int, float))
    and isinstance(games_won, (int, float))
    else None
))
show("Game Time:", f"{hours}h {minutes}m {seconds}s")
show("Total Hours:", f"{gametime / 3600:.2f}" if isinstance(gametime, (int, float)) else "None")
show("Friend Count:", user.get("friend_count"))


# ---------- Tetra League ----------

print("\n--- Tetra League ---")

show("TR:", rounded(league.get("tr")))
show("Rank:", league.get("rank"))
show("Best Rank:", league.get("bestrank"))
show("Standing:", league.get("standing"))
show("Percentile:", league.get("percentile"))
show("Glicko:", rounded(league.get("glicko")))
show("Rating Deviation:", rounded(league.get("rd")))
show("APM:", league.get("apm"))
show("PPS:", league.get("pps"))
show("VS:", league.get("vs"))
show("Games Played:", league_games)
show("Games Won:", league_wins)
show("Win Rate:", win_rate(league_wins, league_games))
show("Current Streak:", league.get("streak"))
show("Decaying:", league.get("decaying"))


# ---------- Past Seasons ----------

print("\n--- Tetra League: Past Seasons ---")

if past:
    def season_number(key):
        try:
            return int(key)
        except (ValueError, TypeError):
            return -1

    for season_key in sorted(past, key=season_number):
        season = past[season_key]

        if not isinstance(season, dict):
            continue

        print(f"\nSeason {season_key}")

        show("Placement:", season.get("placement"))
        show("TR:", rounded(season.get("tr")))
        show("Rank:", season.get("rank"))
        show("Best Rank:", season.get("bestrank"))
        show("Standing:", season.get("standing"))
        show("Percentile:", season.get("percentile"))
        show("Glicko:", rounded(season.get("glicko")))
        show("Rating Deviation:", rounded(season.get("rd")))
        show("Games Played:", season.get("gamesplayed"))
        show("Games Won:", season.get("gameswon"))
        show("Win Rate:", win_rate(
            season.get("gameswon"),
            season.get("gamesplayed")
        ))
        show("APM:", season.get("apm"))
        show("PPS:", season.get("pps"))
        show("VS:", season.get("vs"))
else:
    print("No past season data available.")


# ---------- Account ----------

print("\n--- Account ---")

show("Bad Standing:", user.get("badstanding"))
show("Verified:", user.get("verified"))
show("Supporter:", user.get("supporter"))
show("Supporter Tier:", user.get("supporter_tier"))


# ---------- Connections ----------

print("\n--- Connections ---")

if connections:
    for name, details in connections.items():
        if isinstance(details, dict):
            # Show whether a connection exists without printing
            # potentially sensitive connection details.
            connected = details.get("connected")
            show(f"{name.title()}:", connected if connected is not None else "Connected")
        else:
            show(f"{name.title()}:", details)
else:
    print("No connection data available.")


# ---------- Cosmetics ----------

print("\n--- Cosmetics ---")

show("Avatar Revision:", user.get("avatar_revision"))
show("Banner Revision:", user.get("banner_revision"))


# ---------- Badges ----------

print("\n--- Badges ---")

if badges:
    for badge in badges:
        if isinstance(badge, dict):
            label = badge.get("label", "Unknown badge")
            badge_id = badge.get("id")
            badge_ts = badge.get("ts")

            details = [label]

            if badge_id:
                details.append(f"ID: {badge_id}")

            if badge_ts:
                details.append(f"Date: {format_date(badge_ts)}")

            print("- " + " | ".join(details))
        else:
            print("-", badge)
else:
    print("None")


# ---------- Old Usernames ----------

print("\n--- Old Usernames ---")

if oldusernames:
    for olduser in oldusernames:
        if isinstance(olduser, dict):
            old_name = olduser.get("username", "Unknown username")
            changed_at = olduser.get("ts")

            if changed_at:
                print(f"- {old_name} (changed: {format_date(changed_at)})")
            else:
                print(f"- {old_name}")
        else:
            print("-", olduser)
else:
    print("None")

