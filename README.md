# TetrStats

A lightweight command-line tool for viewing and comparing detailed [TETR.IO](https://tetr.io) player statistics.

## Features

* **Player profiles**

  * Username, role, and country
* **Overall activity statistics**

  * Games played and won
  * Win rate and playtime
* **Tetra League statistics**

  * Current and best rank
  * TR, standing, and percentile
  * APM, PPS, and VS
  * Glicko rating and rating deviation
* **Additional Tetra League statistics**

  * Detailed player statistics and performance metrics
* **Player comparison**

  * Compare two TETR.IO players side by side
  * Compare profile, activity, Tetra League, account, and additional statistics
  * Display numerical differences between players
  * Color-coded results to highlight better, worse, and equal values
* **Personal bests**

  * 40 Lines records
  * Blitz records
* **Account information**

  * Additional account statistics

## Requirements

* Python 3
* `requests`

Install the dependency with:

```bash
pip install requests
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
Country                         EE            XX            N/A

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
├── .gitignore
└── README.md
```

* `main.py` handles command-line arguments, statistics display, formatting, and player comparisons.
* `tetrio_api.py` handles requests to the TETR.IO API.
* `.gitignore` excludes files that should not be tracked by Git.

## Disclaimer

TetrStats is an independent project and is not affiliated with, endorsed by, or officially associated with TETR.IO.

Statistics are retrieved from the TETR.IO API and may change as the API or game changes.

## License

This project is distributed under the terms of the license specified in the [`LICENSE`](LICENSE) file. See that file for the full license text.
