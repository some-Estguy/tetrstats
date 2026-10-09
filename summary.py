from stats import get_40l_time, get_mode_stat, get_playtime, rounded, win_rate


def get_best_altitude(summary):
    """Safely extract the all-time-best Zenith altitude."""
    if not isinstance(summary, dict):
        return None

    best = summary.get("best")
    if not isinstance(best, dict):
        return None

    record = best.get("record")
    if not isinstance(record, dict):
        return None

    results = record.get("results")
    if not isinstance(results, dict):
        return None

    stats = results.get("stats")
    if not isinstance(stats, dict):
        return None

    # Zenith and Expert Zenith may use different stat keys.
    for mode in ("zenith", "zenithex"):
        mode_stats = stats.get(mode)
        if isinstance(mode_stats, dict):
            altitude = mode_stats.get("altitude")
            if isinstance(altitude, (int, float)) and not isinstance(altitude, bool):
                return round(altitude)

    return None


def show(label, value):
    """Print a summary field with a consistent layout."""
    if value is None or value == "":
        value = "N/A"

    print(f"{label:<15} {value}")


def print_summary(username, user, league, zenith, zenithex, sprint, blitz):
    gametime = user.get("gametime") or 0
    hours, minutes, seconds = get_playtime(gametime)

    print()
    print("╔══════════════════════════════╗")
    print("║            SUMMARY           ║")
    print("╚══════════════════════════════╝")

    show("Username:", user.get("username", username))
    show("Country:", user.get("country"))
    show("Game Time:", f"{hours}h {minutes}m {seconds}s")

    print("\n--- Tetra League ---")
    show("TR:", rounded(league.get("tr")))
    show("Rank:", league.get("rank"))
    show("APM:", f"{league['apm']:.2f}" if isinstance(league.get("apm"), (int, float)) else "N/A")
    show("PPS:", f"{league['pps']:.2f}" if isinstance(league.get("pps"), (int, float)) else "N/A")
    show("VS:", f"{league['vs']:.2f}" if isinstance(league.get("vs"), (int, float)) else "N/A")
    show("Win Rate:", win_rate(
        league.get("gameswon"),
        league.get("gamesplayed"),
    ))

    print("\n--- Personal Bests ---")
    show("QP Altitude:", get_best_altitude(zenith))
    show("Expert QP:", get_best_altitude(zenithex))

    sprint_time = get_40l_time(sprint)
    show(
        "40L Sprint:",
        f"{sprint_time:.2f}s" if sprint_time is not None else None,
    )

    blitz_score = get_mode_stat(blitz, "stats", "score")
    show(
        "Blitz Score:",
        f"{blitz_score:,}" if isinstance(blitz_score, (int, float)) else None,
    )