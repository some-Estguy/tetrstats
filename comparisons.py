import requests
from datetime import datetime, timezone
from stats import get_40l_time, get_mode_stat, win_rate

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

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

def run_comparison(
    username, args, user, league, compare_user, compare_league,
    user_40l, compare_40l, user_blitz, compare_blitz,
    your_40l_time, their_40l_time,
):
    import json
    import sys
    from stats import get_40l_time, get_mode_stat, win_rate

    compare_username = args.compare

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
        return
