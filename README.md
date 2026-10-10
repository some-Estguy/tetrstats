# TetrStats

A lightweight command-line tool for viewing and comparing detailed [TETR.IO](https://tetr.io) player statistics.

## Features

- **Player profiles**
  - Username, role, and country
  - Account information and cosmetics

- **Overall activity statistics**
  - Games played, won, and lost
  - Win rate and playtime
  - Friend count and XP

- **Tetra League statistics**
  - Current and best rank
  - TR, standing, and percentile
  - APM, PPS, and VS
  - Glicko rating and rating deviation
  - Additional performance metrics
  - Past-season statistics when available

- **Quick Play statistics**
  - Zenith and Expert Zenith
  - Altitude and floor reached
  - Run time and score
  - Current and best global leaderboard ranks
  - Country leaderboard ranks when available
  - APM, PPS, and VS
  - Lines, pieces placed, inputs, holds, and T-Spins
  - Combo, back-to-back, and finesse statistics
  - Garbage statistics and line-clear breakdowns

- **Personal bests**
  - 40 Lines records
  - Blitz records

- **Player comparison**
  - Compare two TETR.IO players side by side
  - Compare profile, activity, Tetra League, account, and additional statistics
  - Display numerical differences between players
  - Color-coded results to highlight better, worse, and equal values where applicable

## Requirements

- Python 3
- `requests`

Install the dependency with:

```bash
python3 -m pip install requests
```

## Usage

### View a player's statistics

```bash
python3 main.py <username>
```

Example:

```bash
python3 main.py estonian-guy
```

### Compare two players

Use the `--compare` option followed by the second player's username:

```bash
python3 main.py <username> --compare <other_username>
```

Example:

```bash
python3 main.py estonian-guy --compare lowlight
```

The comparison displays both players' statistics side by side, with a difference column for numerical values. Color-coded output helps distinguish better, worse, and equal results where applicable.

## Example Output

The following is a simplified illustration of the comparison output:

```text
PROFILE
Stat                      Player 1      Player 2    Difference
----------------------------------------------------------------
Username              estonian-guy      lowlight            N/A
Role                          user          user            N/A
Country                         EE            EE            N/A

OVERALL ACTIVITY
Stat                      Player 1      Player 2    Difference
----------------------------------------------------------------
Games Played                 10000          8000      +2,000.00
Games Won                     6000          4000      +2,000.00
```

*Example values are illustrative and do not represent live player statistics.*

## Project Structure

```text
tetrstats/
├── main.py
├── tetrio_api.py
├── stats.py
├── comparisons.py
├── summary.py
├── README.md
├── LICENSE
└── .gitignore
```

- `main.py` handles command-line arguments, statistics display, formatting, and program flow.
- `tetrio_api.py` handles requests to the TETR.IO API.
- `stats.py` contains statistics-related helpers.
- `comparisons.py` handles player comparison logic.
- `summary.py` contains summary-related functionality.
- `.gitignore` excludes files that should not be tracked by Git.

## Disclaimer

TetrStats is an independent project and is not affiliated with, endorsed by, or officially associated with TETR.IO.

Statistics are retrieved from the TETR.IO API and may change as the API or game changes. Some statistics or leaderboard positions may be unavailable.

## License

This project is distributed under the terms of the license specified in the [`LICENSE`](LICENSE) file. See that file for the full license text.
