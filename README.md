# TetrStats

A lightweight command-line tool for viewing detailed [TETR.IO](https://tetr.io) player statistics.

## Features

* Player profile information
* Overall activity statistics
* Tetra League statistics
* Win rates
* Playtime
* Current and best rank
* APM, PPS and VS
* Glicko and rating deviation
* Past Tetra League seasons
* Account information
* Connections
* Badges
* Previous usernames
* Avatar and banner revisions

## Requirements

* Python 3
* `requests`

Install the dependency with:

```bash
pip install requests
```

## Usage

Run TetrStats with a TETR.IO username:

```bash
python3 main.py <username>
```

Example:

```bash
python3 main.py estonian-guy
```

## Example Output

```text
╔══════════════════════════════╗
║          TETR.IO STATS       ║
╚══════════════════════════════╝

--- Profile ---
Player ID:          ...
Username:           estonian-guy
Role:               user
Country:            EE
Created:            ...

--- Tetra League ---
TR:                 ...
Rank:               SS
Best Rank:          SS
Standing:           ...
Percentile:         ...
APM:                ...
PPS:                ...
VS:                 ...

--- Past Seasons ---

Season ...
Placement:          ...
TR:                 ...
Rank:               ...
```

## Project Structure

```text
tetrstats/
├── main.py
├── tetrio_api.py
├── .gitignore
└── README.md
```

`main.py` handles the command-line interface, formatting and statistics display.

`tetrio_api.py` handles requests to the TETR.IO API.

## Disclaimer

TetrStats is an independent project and is not affiliated with or endorsed by TETR.IO.

## License

This project is currently unlicensed.
