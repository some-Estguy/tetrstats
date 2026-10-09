from tetrio_api import get_user, get_league
import sys
import requests
import argparse
import json
from datetime import datetime, timezone

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

def print_comparison_row(label, value1, value2, lower_is_better=False,
                         decimals=2, suffix=""):
    label_width = 22
    value_width = 14
    diff_width = 14

    if value1 is None:
        text1 = "N/A"
    else:
        text1 = f"{value1:,.{decimals}f}{suffix}"

    if value2 is None:
        text2 = "N/A"
    else:
        text2 = f"{value2:,.{decimals}f}{suffix}"

    if value1 is None or value2 is None:
        diff_text = "N/A"
    else:
        difference = value1 - value2
        diff_text = f"{difference:+,.{decimals}f}{suffix}"

        if value1 == value2:
            text1 = f"{YELLOW}{text1:>{value_width}}{RESET}"
            text2 = f"{YELLOW}{text2:>{value_width}}{RESET}"
        else:
            first_better = (
                value1 < value2 if lower_is_better else value1 > value2
            )

            if first_better:
                text1 = f"{GREEN}{text1:>{value_width}}{RESET}"
                text2 = f"{RED}{text2:>{value_width}}{RESET}"
            else:
                text1 = f"{RED}{text1:>{value_width}}{RESET}"
                text2 = f"{GREEN}{text2:>{value_width}}{RESET}"

    if not text1.startswith((GREEN, RED, YELLOW)):
        text1 = f"{text1:>{value_width}}"

    if not text2.startswith((GREEN, RED, YELLOW)):
        text2 = f"{text2:>{value_width}}"

    print(
        f"{label:<{label_width}}"
        f"{text1}"
        f"{text2}"
        f"{diff_text:>{diff_width}}"
    )



def print_comparison_text_row(
    label, value1, value2, lower_is_better=False
):
    """Print two values and their difference when numeric."""
    def format_value(value):
        if value is None or value == "":
            return "N/A"
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value)

    text1 = format_value(value1)
    text2 = format_value(value2)
    diff_text = "N/A"
    color1 = ""
    color2 = ""

    numeric1 = (
        isinstance(value1, (int, float))
        and not isinstance(value1, bool)
    )
    numeric2 = (
        isinstance(value2, (int, float))
        and not isinstance(value2, bool)
    )

    if numeric1 and numeric2:
        difference = value1 - value2
        diff_text = f"{difference:+,.2f}"

        if value1 == value2:
            color1 = color2 = YELLOW
        else:
            first_better = (
                value1 < value2
                if lower_is_better
                else value1 > value2
            )
            color1 = GREEN if first_better else RED
            color2 = RED if first_better else GREEN

    elif value1 is not None and value2 is not None:
        if value1 == value2:
            color1 = color2 = YELLOW

    # Keep columns aligned despite ANSI color codes.
    text1 = f"{text1[:40]:>14}"
    text2 = f"{text2[:40]:>14}"

    if color1:
        text1 = f"{color1}{text1}{RESET}"
    if color2:
        text2 = f"{color2}{text2}{RESET}"

    print(f"{label:<22}{text1}{text2}{diff_text:>14}")

def format_stat(key, value):
    if value is None:
        return "None"

    if key in ("apm", "pps", "vs", "glicko", "rd"):
        if isinstance(value, (int, float)):
            return f"{value:.2f}"

    if key in ("tr", "gamesplayed", "gameswon"):
        if isinstance(value, (int, float)):
            return str(round(value))

    return str(value)

def get_mode_summary(username, mode):
    url = f"https://ch.tetr.io/api/users/{username}/summaries/{mode}"

    r = requests.get(
        url,
        headers={"User-Agent": "tetrstats/0.1"},
        timeout=10
    )

    if r.status_code == 404:
        print(f"Player '{username}' was not found.")
        return None

    r.raise_for_status()
    data = r.json()

    if not data.get("success"):
        raise ValueError(f"Could not retrieve {mode} stats for {username}")
    return data["data"]


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


# ---------- Comparison ----------

if args.compare:
    print(f"\nComparing {username} vs {args.compare}\n")

    # Extract personal-best record stats.
    # Each mode summary may be missing, so handle that safely.

    def record_stat(summary, section, key):
        return get_mode_stat(summary, section, key)

    def nested_stat(summary, section, parent, key):
        data = record_stat(summary, section, parent)
        return data.get(key) if isinstance(data, dict) else None

    # 40 Lines
    your_40l_stats = [
        ("40L Time", your_40l_time, their_40l_time, True, 2, "s"),
        ("40L PPS",
         record_stat(user_40l, "aggregatestats", "pps"),
         record_stat(compare_40l, "aggregatestats", "pps"),
         False, 2, ""),
        ("40L Score",
         record_stat(user_40l, "stats", "score"),
         record_stat(compare_40l, "stats", "score"),
         False, 0, ""),
        ("40L Pieces",
         record_stat(user_40l, "stats", "piecesplaced"),
         record_stat(compare_40l, "stats", "piecesplaced"),
         False, 0, ""),
        ("40L Inputs",
         record_stat(user_40l, "stats", "inputs"),
         record_stat(compare_40l, "stats", "inputs"),
         True, 0, ""),
        ("40L Holds",
         record_stat(user_40l, "stats", "holds"),
         record_stat(compare_40l, "stats", "holds"),
         False, 0, ""),
        ("40L T-Spins",
         record_stat(user_40l, "stats", "tspins"),
         record_stat(compare_40l, "stats", "tspins"),
         False, 0, ""),
        ("40L Top Combo",
         record_stat(user_40l, "stats", "topcombo"),
         record_stat(compare_40l, "stats", "topcombo"),
         False, 0, ""),
        ("40L B2B",
         record_stat(user_40l, "stats", "btb"),
         record_stat(compare_40l, "stats", "btb"),
         False, 0, ""),
        ("40L Top B2B",
         record_stat(user_40l, "stats", "topbtb"),
         record_stat(compare_40l, "stats", "topbtb"),
         False, 0, ""),
        ("40L Finesse Faults",
         nested_stat(user_40l, "stats", "finesse", "faults"),
         nested_stat(compare_40l, "stats", "finesse", "faults"),
         True, 0, ""),
        ("40L Perfect Pieces",
         nested_stat(user_40l, "stats", "finesse", "perfectpieces"),
         nested_stat(compare_40l, "stats", "finesse", "perfectpieces"),
         False, 0, ""),
        ("40L Singles",
         nested_stat(user_40l, "stats", "clears", "singles"),
         nested_stat(compare_40l, "stats", "clears", "singles"),
         False, 0, ""),
        ("40L Doubles",
         nested_stat(user_40l, "stats", "clears", "doubles"),
         nested_stat(compare_40l, "stats", "clears", "doubles"),
         False, 0, ""),
        ("40L Triples",
         nested_stat(user_40l, "stats", "clears", "triples"),
         nested_stat(compare_40l, "stats", "clears", "triples"),
         False, 0, ""),
        ("40L Quads",
         nested_stat(user_40l, "stats", "clears", "quads"),
         nested_stat(compare_40l, "stats", "clears", "quads"),
         False, 0, ""),
        ("40L All Clears",
         nested_stat(user_40l, "stats", "clears", "allclear"),
         nested_stat(compare_40l, "stats", "clears", "allclear"),
         False, 0, ""),
        ("40L Global Rank",
         user_40l.get("rank") if user_40l else None,
         compare_40l.get("rank") if compare_40l else None,
         True, 0, ""),
        ("40L Country Rank",
         user_40l.get("rank_local") if user_40l else None,
         compare_40l.get("rank_local") if compare_40l else None,
         True, 0, ""),
    ]

    # Blitz
    your_blitz_stats = [
        ("Blitz Score",
         record_stat(user_blitz, "stats", "score"),
         record_stat(compare_blitz, "stats", "score"),
         False, 0, ""),
        ("Blitz Level",
         record_stat(user_blitz, "stats", "level"),
         record_stat(compare_blitz, "stats", "level"),
         False, 0, ""),
        ("Blitz Lines",
         record_stat(user_blitz, "stats", "lines"),
         record_stat(compare_blitz, "stats", "lines"),
         False, 0, ""),
        ("Blitz PPS",
         record_stat(user_blitz, "aggregatestats", "pps"),
         record_stat(compare_blitz, "aggregatestats", "pps"),
         False, 2, ""),
        ("Blitz Pieces",
         record_stat(user_blitz, "stats", "piecesplaced"),
         record_stat(compare_blitz, "stats", "piecesplaced"),
         False, 0, ""),
        ("Blitz Inputs",
         record_stat(user_blitz, "stats", "inputs"),
         record_stat(compare_blitz, "stats", "inputs"),
         True, 0, ""),
        ("Blitz Holds",
         record_stat(user_blitz, "stats", "holds"),
         record_stat(compare_blitz, "stats", "holds"),
         False, 0, ""),
        ("Blitz T-Spins",
         record_stat(user_blitz, "stats", "tspins"),
         record_stat(compare_blitz, "stats", "tspins"),
         False, 0, ""),
        ("Blitz Top Combo",
         record_stat(user_blitz, "stats", "topcombo"),
         record_stat(compare_blitz, "stats", "topcombo"),
         False, 0, ""),
        ("Blitz B2B",
         record_stat(user_blitz, "stats", "btb"),
         record_stat(compare_blitz, "stats", "btb"),
         False, 0, ""),
        ("Blitz Top B2B",
         record_stat(user_blitz, "stats", "topbtb"),
         record_stat(compare_blitz, "stats", "topbtb"),
         False, 0, ""),
        ("Blitz Finesse Faults",
         nested_stat(user_blitz, "stats", "finesse", "faults"),
         nested_stat(compare_blitz, "stats", "finesse", "faults"),
         True, 0, ""),
        ("Blitz Perfect Pieces",
         nested_stat(user_blitz, "stats", "finesse", "perfectpieces"),
         nested_stat(compare_blitz, "stats", "finesse", "perfectpieces"),
         False, 0, ""),
        ("Blitz Singles",
         nested_stat(user_blitz, "stats", "clears", "singles"),
         nested_stat(compare_blitz, "stats", "clears", "singles"),
         False, 0, ""),
        ("Blitz Doubles",
         nested_stat(user_blitz, "stats", "clears", "doubles"),
         nested_stat(compare_blitz, "stats", "clears", "doubles"),
         False, 0, ""),
        ("Blitz Triples",
         nested_stat(user_blitz, "stats", "clears", "triples"),
         nested_stat(compare_blitz, "stats", "clears", "triples"),
         False, 0, ""),
        ("Blitz Quads",
         nested_stat(user_blitz, "stats", "clears", "quads"),
         nested_stat(compare_blitz, "stats", "clears", "quads"),
         False, 0, ""),
        ("Blitz All Clears",
         nested_stat(user_blitz, "stats", "clears", "allclear"),
         nested_stat(compare_blitz, "stats", "clears", "allclear"),
         False, 0, ""),
        ("Blitz Global Rank",
         user_blitz.get("rank") if user_blitz else None,
         compare_blitz.get("rank") if compare_blitz else None,
         True, 0, ""),
        ("Blitz Country Rank",
         user_blitz.get("rank_local") if user_blitz else None,
         compare_blitz.get("rank_local") if compare_blitz else None,
         True, 0, ""),
    ]

    # Profile comparison
    print("\nPROFILE")
    print(
    f"{'Stat':<22}"
    f"{username:>14}"
    f"{args.compare:>14}"
    f"{'Difference':>14}"
)
    print("-" * 64)

    profile_rows = [
        ("Username", user.get("username"), compare_user.get("username")),
        ("Role", user.get("role"), compare_user.get("role")),
        ("Country", user.get("country"), compare_user.get("country")),
    ]

    for label, value1, value2 in profile_rows:
        print_comparison_text_row(label, value1, value2)

    # Overall activity comparison
    print("\nOVERALL ACTIVITY")
    print(
        f"{'Stat':<22}"
        f"{username:>14}"
        f"{args.compare:>14}"
        f"{'Difference':>14}"
    )
    print("-" * 64)

    def get_gametime(profile):
        value = profile.get("gametime")
        if not isinstance(value, (int, float)):
            return None
        return value

    def get_games_lost(profile):
        played = profile.get("gamesplayed")
        won = profile.get("gameswon")

        if (
            isinstance(played, (int, float))
            and isinstance(won, (int, float))
        ):
            return played - won
        return None

    activity_stats = [
        ("XP", user.get("xp"), compare_user.get("xp"), 0, False),
        (
            "Games Played",
            user.get("gamesplayed"),
            compare_user.get("gamesplayed"),
            0,
            False,
        ),
        (
            "Games Won",
            user.get("gameswon"),
            compare_user.get("gameswon"),
            0,
            False,
        ),
        (
            "Games Lost",
            get_games_lost(user),
            get_games_lost(compare_user),
            0,
            True,
        ),
        (
            "Total Hours",
            get_gametime(user) / 3600 if get_gametime(user) is not None else None,
            get_gametime(compare_user) / 3600
            if get_gametime(compare_user) is not None else None,
            2,
            False,
        ),
        (
            "Friend Count",
            user.get("friend_count"),
            compare_user.get("friend_count"),
            0,
            False,
        ),
    ]

    for label, value1, value2, decimals, lower_better in activity_stats:
        print_comparison_row(
            label,
            value1,
            value2,
            lower_is_better=lower_better,
            decimals=decimals,
        )

    print_comparison_text_row(
        "Win Rate",
        win_rate(user.get("gameswon"), user.get("gamesplayed")),
        win_rate(compare_user.get("gameswon"), compare_user.get("gamesplayed")),
    )

    print_comparison_text_row(
        "Game Time",
        (
            f"{int(get_gametime(user) // 3600)}h "
            f"{int((get_gametime(user) % 3600) // 60)}m "
            f"{int(get_gametime(user) % 60)}s"
        ) if get_gametime(user) is not None else None,
        (
            f"{int(get_gametime(compare_user) // 3600)}h "
            f"{int((get_gametime(compare_user) % 3600) // 60)}m "
            f"{int(get_gametime(compare_user) % 60)}s"
        ) if get_gametime(compare_user) is not None else None,
    )

    # Existing Tetra League stats
   
    print("\nTETRA LEAGUE")

    stats = {
        "TR": ("tr", "tr"),
        "APM": ("apm", "apm"),
        "PPS": ("pps", "pps"),
        "VS": ("vs", "vs"),
        "Glicko": ("glicko", "glicko"),
        "Games Played": ("gamesplayed", "gamesplayed"),
        "Games Won": ("gameswon", "gameswon"),
    }

    print(
        f"{'Stat':<22}"
        f"{username:>14}"
        f"{args.compare:>14}"
        f"{'Difference':>14}"
    )
    print("-" * 64)

    for label, (key1, key2) in stats.items():
        raw1 = league.get(key1)
        raw2 = compare_league.get(key2)

        value1 = format_stat(key1, raw1)
        value2 = format_stat(key2, raw2)

        if isinstance(raw1, (int, float)) and isinstance(raw2, (int, float)):
            difference = raw1 - raw2

            decimals = 2 if key1 in ("apm", "pps", "vs", "glicko") else 0
            diff_text = f"{difference:+,.{decimals}f}"

            # Pad before applying colours to preserve alignment.
            value1 = f"{value1:>14}"
            value2 = f"{value2:>14}"

            if raw1 > raw2:
                value1 = f"{GREEN}{value1}{RESET}"
                value2 = f"{RED}{value2}{RESET}"
            elif raw2 > raw1:
                value1 = f"{RED}{value1}{RESET}"
                value2 = f"{GREEN}{value2}{RESET}"
        else:
            value1 = f"{value1:>14}"
            value2 = f"{value2:>14}"
            diff_text = "N/A"

        print(f"{label:<22}{value1}{value2}{diff_text:>14}")

    # Additional Tetra League stats
    print("\nTETRA LEAGUE — ADDITIONAL STATS")
    
    print(
        f"{'Stat':<22}"
        f"{username:>14}"
        f"{args.compare:>14}"
        f"{'Difference':>14}"
    )
    print("-" * 64)

    league_extra_rows = [
        ("Rank", league.get("rank"), compare_league.get("rank")),
        (
            "Best Rank",
            league.get("bestrank"),
            compare_league.get("bestrank"),
        ),
        (
            "Standing",
            league.get("standing"),
            compare_league.get("standing"),
        ),
        (
            "Percentile",
            league.get("percentile"),
            compare_league.get("percentile"),
        ),
        (
            "Rating Deviation",
            league.get("rd"),
            compare_league.get("rd"),
        ),
        (
            "Win Rate",
            win_rate(league.get("gameswon"), league.get("gamesplayed")),
            win_rate(
                compare_league.get("gameswon"),
                compare_league.get("gamesplayed"),
            ),
        ),
        ("Current Streak", league.get("streak"), compare_league.get("streak")),
        ("Decaying", league.get("decaying"), compare_league.get("decaying")),
    ]

    for label, value1, value2 in league_extra_rows:
        print_comparison_text_row(
        label,
        value1,
        value2,
        lower_is_better=label in (
            "Standing",
            "Percentile",
            "Rating Deviation",
        ),
    )


    # Account comparison
    print(
    f"{'Stat':<22}"
    f"{username:>14}"
    f"{args.compare:>14}"
    f"{'Difference':>14}"
    )
    print("-" * 64)

    account_rows = [
        ("Bad Standing", user.get("badstanding"), compare_user.get("badstanding")),
        ("Verified", user.get("verified"), compare_user.get("verified")),
        ("Supporter", user.get("supporter"), compare_user.get("supporter")),
        (
            "Supporter Tier",
            user.get("supporter_tier"),
            compare_user.get("supporter_tier"),
        ),
    ]

    for label, value1, value2 in account_rows:
        print_comparison_text_row(label, value1, value2)

    # Print 40L and Blitz sections
    for section_name, rows in (
        ("40 LINES PERSONAL BEST", your_40l_stats),
        ("BLITZ PERSONAL BEST", your_blitz_stats),
    ):
        print(f"\n{section_name}")
        for label, value1, value2, lower_better, decimals, suffix in rows:
            print_comparison_row(
                label, value1, value2,
                lower_is_better=lower_better,
                decimals=decimals,
                suffix=suffix,
            )

    print("\n" + "-" * 77)
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