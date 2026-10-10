from tetrio_api import get_user, get_league, get_zenith, get_zenithex
import sys
import requests
from comparisons import run_comparison, get_mode_summary
import argparse
import json
from datetime import datetime, timezone
from summary import print_summary

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

from stats import (
    get_40l_time,
    get_mode_stat,
    rounded,
    win_rate,
    get_playtime,
)

# ---------- Helpers ----------

def should_show(section, args):
    if args.league:
        return section in ("league", "past")

    if args.season is not None:
        return section == "season"


    return True

def show(label, value):
    """Print a stat, replacing missing values with None."""
    if value is None or value == "":
        value = "None"
    print(f"{label:<19} {value}")

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

VERSION = "1.0.0"


def parse_args():
    parser = argparse.ArgumentParser(
        prog="tetrstats",
        description="Look up TETR.IO player statistics."
    )

    parser.add_argument(
        "username",
        nargs="?",
        help="TETR.IO username to look up"
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show additional debugging information"
    )

    parser.add_argument(
        "-l", "--league",
        action="store_true",
        help="show only Tetra League information"
    )

    parser.add_argument(
        "-s", "--season",
        type=str,
        help="show stats for a specific past season"
    )

    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="output stats as JSON"
    )

    parser.add_argument(
        "-c", "--compare",
        metavar="USERNAME",
        help="Compare your target with another player"
    )

    parser.add_argument(
    "--summary",
    action="store_true",
    help="Show a short summary of player statistics",
    )

    args = parser.parse_args()

    if args.username is not None:
        args.username = args.username.strip()
        if not args.username:
            parser.error("Username cannot be empty.")
    else:
        parser.error("Please provide a TETR.IO username.")

    return args

args = parse_args()
username = args.username

# ---------- Fetch API data ----------

try:
    user = get_user(username)

    if user is None:
        sys.exit(1)

    league = get_league(username)

    zenith = get_zenith(username)
    zenithex = get_zenithex(username)

    compare_user = None
    compare_league = None

    if args.compare:
        compare_user = get_user(args.compare)
        compare_league = get_league(args.compare)

        if compare_user is None or compare_league is None:
            print(f"Error: Could not retrieve stats for {args.compare}.")
            sys.exit(1)

        user_40l = get_mode_summary(username, "40l")
        user_blitz = get_mode_summary(username, "blitz")

        compare_40l = get_mode_summary(args.compare, "40l")
        compare_blitz = get_mode_summary(args.compare, "blitz")

        your_40l_time = get_40l_time(user_40l)
        their_40l_time = get_40l_time(compare_40l)

        your_40l_pps = get_mode_stat(user_40l, "aggregatestats", "pps")
        their_40l_pps = get_mode_stat(compare_40l, "aggregatestats", "pps")

        your_blitz_score = get_mode_stat(user_blitz, "stats", "score")
        their_blitz_score = get_mode_stat(compare_blitz, "stats", "score")

        your_blitz_pps = get_mode_stat(user_blitz, "aggregatestats", "pps")
        their_blitz_pps = get_mode_stat(compare_blitz, "aggregatestats", "pps")

        your_40l_rank = user_40l.get("rank") if user_40l else None
        their_40l_rank = compare_40l.get("rank") if compare_40l else None

        your_blitz_rank = user_blitz.get("rank") if user_blitz else None
        their_blitz_rank = compare_blitz.get("rank") if compare_blitz else None

        your_blitz_tspins = get_mode_stat(user_blitz, "stats", "tspins")
        their_blitz_tspins = get_mode_stat(compare_blitz, "stats", "tspins")

        your_blitz_pieces = get_mode_stat(user_blitz, "stats", "piecesplaced")
        their_blitz_pieces = get_mode_stat(compare_blitz, "stats", "piecesplaced")

        your_blitz_finesse = (
            get_mode_stat(user_blitz, "stats", "finesse") or {}
        ).get("faults")

        their_blitz_finesse = (
            get_mode_stat(compare_blitz, "stats", "finesse") or {}
        ).get("faults")

        if args.verbose:
            print("YOUR 40L:", json.dumps(user_40l, indent=2))
            print("YOUR BLITZ:", json.dumps(user_blitz, indent=2))
            print("OTHER 40L:", json.dumps(compare_40l, indent=2))
            print("OTHER BLITZ:", json.dumps(compare_blitz, indent=2))
            print(json.dumps(user_blitz, indent=2))

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
hours, minutes, seconds = get_playtime(gametime)

games_played = user.get("gamesplayed")
games_won = user.get("gameswon")

league_games = league.get("gamesplayed")
league_wins = league.get("gameswon")

past = league.get("past") or {}
badges = user.get("badges") or []
oldusernames = user.get("oldusernames") or []
connections = user.get("connections") or {}

if args.json:
    output = {
        "profile": user,
        "league": league,
    }
    print(json.dumps(output, indent=4, ensure_ascii=False))
    sys.exit(0)

# ---------- Summary ----------
if args.summary:
    try:
        sprint = get_mode_summary(username, "40l")
        blitz = get_mode_summary(username, "blitz")

        print_summary(
            username,
            user,
            league,
            zenith,
            zenithex,
            sprint,
            blitz,
        )
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching mode stats: {e}")
        sys.exit(1)
    except (ValueError, KeyError) as e:
        print(f"Error while generating summary: {e}")
        sys.exit(1)

    sys.exit(0)


# ---------- Comparison ----------

if args.compare:
    run_comparison(
        username,
        args,
        user,
        league,
        compare_user,
        compare_league,
        user_40l,
        compare_40l,
        user_blitz,
        compare_blitz,
        your_40l_time,
        their_40l_time,
    )
    sys.exit(0)

# ---------- Header ----------

print()

if args.season is not None:
    print("╔══════════════════════════════╗")
    print(f"║       SEASON {args.season:<17}║")
    print("╚══════════════════════════════╝")
elif args.league:
    print("╔══════════════════════════════╗")
    print("║        TETRA LEAGUE          ║")
    print("╚══════════════════════════════╝")
else:
    print("╔══════════════════════════════╗")
    print("║        TETR.IO STATS         ║")
    print("╚══════════════════════════════╝")

# ---------- Profile ----------
if should_show("profile", args):
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
if should_show("activity", args):
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

if should_show("league", args):
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

if args.season is not None and not args.league and args.season not in past:
    print(f"Error: Season {args.season} not found.")
    sys.exit(1)

if should_show("past", args) or should_show("season", args):
    
    print("\n--- Tetra League: Past Seasons ---")

    if past:
        def season_number(key):
            try:
                return int(key)
            except (ValueError, TypeError):
                return -1

        
        for season_key in sorted(past, key=season_number):
            # If a season was requested, skip all other seasons.
            if args.season is not None and not args.league and season_key != args.season:
                continue

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



# ---------- Quick Play ----------

def get_qp_best_record(summary):
    """Get the best available Quick Play record."""
    if not isinstance(summary, dict):
        return None

    best = summary.get("best")
    if isinstance(best, dict):
        record = best.get("record")
        if isinstance(record, dict):
            return record

    record = summary.get("record")
    return record if isinstance(record, dict) else None


def qp_number(value, decimals=0):
    """Format a numeric Quick Play stat."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{value:,.{decimals}f}"
    return None


def qp_rank(value):
    """Format a leaderboard position."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"#{int(value):,}"
    return None




def get_qp_rank(summary, field, best=False):
    if not isinstance(summary, dict):
        return None

    if best:
        source = summary.get("best")
    else:
        source = summary

    if not isinstance(source, dict):
        return None

    value = source.get(field)

    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value > 0
    ):
        return value

    return None


def print_qp_mode(title, summary, mode):
    record = get_qp_best_record(summary)
    print(json.dumps(summary, indent=2))

    if record is None:
        print(f"\n--- {title} ---")
        print("No record available.")
        return

    results = record.get("results")
    if not isinstance(results, dict):
        print(f"\n--- {title} ---")
        print("No record statistics available.")
        return

    stats = results.get("stats")
    if not isinstance(stats, dict):
        stats = {}

    aggregate = results.get("aggregatestats")
    if not isinstance(aggregate, dict):
        aggregate = {}

    mode_stats = stats.get(mode)

    # TETR.IO may use "zenith" for Expert Zenith stats too.
    if not isinstance(mode_stats, dict):
        mode_stats = stats.get("zenith")

    if not isinstance(mode_stats, dict):
        mode_stats = {}

    clears = stats.get("clears")
    if not isinstance(clears, dict):
        clears = {}

    finesse = stats.get("finesse")
    if not isinstance(finesse, dict):
        finesse = {}

    garbage = stats.get("garbage")
    if not isinstance(garbage, dict):
        garbage = {}

    # Leaderboard positions are stored outside the record.
    best_data = summary.get("best")

    if (
        isinstance(best_data, dict)
        and best_data.get("record") is record
    ):
        position = best_data.get("p")
    else:
        position = summary.get("p")

    if not isinstance(position, dict):
        position = record.get("p")

    if not isinstance(position, dict):
        position = {}
    # TETR.IO stores finaltime in milliseconds.
    finaltime = mode_stats.get("finaltime")

    if not isinstance(finaltime, (int, float)):
        finaltime = stats.get("finaltime")
    time_text = None

    if (
        isinstance(finaltime, (int, float))
        and not isinstance(finaltime, bool)
        and finaltime >= 0
    ):
        total_seconds = finaltime / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        time_text = f"{minutes}m {seconds:05.2f}s"

    print(f"\n--- {title} ---")

    rows = [
        ("Altitude:", qp_number(mode_stats.get("altitude"), 2)),
        ("Floor:", qp_number(mode_stats.get("floor"))),
        ("Time:", time_text),
        ("Current Global Rank:", qp_rank(get_qp_rank(summary, "rank"))),
        ("Current Country Rank:", qp_rank(get_qp_rank(summary, "rank_local"))),
        ("Best Global Rank:", qp_rank(get_qp_rank(summary, "rank", best=True))),
        ("Best Country Rank:", qp_rank(get_qp_rank(summary, "rank_local", best=True))),
        ("Score:", qp_number(stats.get("score"))),
        ("Lines:", qp_number(stats.get("lines"))),
        ("APM:", qp_number(aggregate.get("apm"), 2)),
        ("PPS:", qp_number(aggregate.get("pps"), 2)),
        ("VS:", qp_number(aggregate.get("vsscore"), 2)),
        ("Pieces Placed:", qp_number(stats.get("piecesplaced"))),
        ("Inputs:", qp_number(stats.get("inputs"))),
        ("Holds:", qp_number(stats.get("holds"))),
        ("T-Spins:", qp_number(stats.get("tspins"))),
        ("Top Combo:", qp_number(stats.get("topcombo"))),
        ("B2B:", qp_number(stats.get("btb"))),
        ("Top B2B:", qp_number(stats.get("topbtb"))),
        ("Finesse Faults:", qp_number(finesse.get("faults"))),
        ("Perfect Pieces:", qp_number(finesse.get("perfectpieces"))),
        ("Garbage Sent:", qp_number(garbage.get("sent"))),
        ("Max Spike:", qp_number(garbage.get("maxspike"))),
        ("Singles:", qp_number(clears.get("singles"))),
        ("Doubles:", qp_number(clears.get("doubles"))),
        ("Triples:", qp_number(clears.get("triples"))),
        ("Quads:", qp_number(clears.get("quads"))),
        ("All Clears:", qp_number(clears.get("allclear"))),
    ]

    for label, value in rows:
        show(label, value)


if should_show("quickplay", args):
    print_qp_mode("QUICK PLAY — ZENITH", zenith, "zenith")
    print_qp_mode("EXPERT QUICK PLAY — ZENITH", zenithex, "zenithex")






# ---------- Account ----------
if should_show("account", args):

    print("\n--- Account ---")

    show("Bad Standing:", user.get("badstanding"))
    show("Verified:", user.get("verified"))
    show("Supporter:", user.get("supporter"))
    show("Supporter Tier:", user.get("supporter_tier"))


# ---------- Connections ----------
if should_show("connections", args):
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

if should_show("cosmetics", args):

    print("\n--- Cosmetics ---")
    show("Avatar Revision:", user.get("avatar_revision"))
    show("Banner Revision:", user.get("banner_revision"))


# ---------- Badges ----------

if should_show("badges", args):
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

if should_show("old usernames", args):

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