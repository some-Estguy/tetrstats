def get_40l_time(summary):
    if not isinstance(summary, dict):
        return None

    record = summary.get("record")
    if not isinstance(record, dict):
        return None

    results = record.get("results")
    if not isinstance(results, dict):
        return None

    stats = results.get("stats")
    if not isinstance(stats, dict):
        return None

    time = stats.get("finaltime")

    if isinstance(time, (int, float)) and not isinstance(time, bool):
        return time / 1000

    return None


def get_mode_stat(summary, section, key):
    if not isinstance(summary, dict):
        return None

    record = summary.get("record")
    if not isinstance(record, dict):
        return None

    results = record.get("results")
    if not isinstance(results, dict):
        return None

    data = results.get(section)
    if not isinstance(data, dict):
        return None

    return data.get(key)


def rounded(value):
    if value is None or value == -1:
        return "N/A"

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return round(value)

    return value


def win_rate(wins, games):
    valid_numbers = (
        isinstance(wins, (int, float))
        and not isinstance(wins, bool)
        and isinstance(games, (int, float))
        and not isinstance(games, bool)
        and wins != -1
        and games != -1
    )

    if valid_numbers and games > 0:
        return wins / games * 100

    return None


def get_playtime(gametime):
    if not isinstance(gametime, (int, float)) or isinstance(gametime, bool):
        return 0, 0, 0

    if gametime < 0:
        return 0, 0, 0

    hours = int(gametime // 3600)
    minutes = int((gametime % 3600) // 60)
    seconds = int(gametime % 60)

    return hours, minutes, seconds