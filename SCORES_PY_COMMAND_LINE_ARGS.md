# scores.py Command Line Arguments Added ✅

## Problem
When running `python scores.py --help`, no help was displayed because `scores.py` didn't have command line argument parsing. Only `main.py` had the argparse implementation.

## Solution
Added full command line argument parsing to `scores.py` matching the functionality in `main.py`.

## Changes Made

### 1. Import argparse (line 17)
```python
import sys
import argparse  # NEW
import webbrowser
```

### 2. Full Argument Parser (lines 8570-8658)
Added complete argument parsing in the `if __name__ == "__main__":` block:

**Arguments Added:**
- `--help, -h` - Show help message and exit
- `--live-scores` - Launch to Live Scores view (all sports)
- `--live` - Shorthand for --live-scores

**Sports Game Views:**
- `--mlb`, `--nfl`, `--nba`, `--wnba`, `--nhl`, `--ncaaf`, `--ncaam`, `--ncaawb`

**Teams Views:**
- `--mlb-teams`, `--nfl-teams`, `--nba-teams`, `--wnba-teams`, `--nhl-teams`, `--ncaaf-teams`, `--ncaam-teams`, `--ncaawb-teams`

**Standings Views:**
- `--mlb-standings`, `--nfl-standings`, `--nba-standings`, `--wnba-standings`, `--nhl-standings`, `--ncaaf-standings`, `--ncaam-standings`, `--ncaawb-standings`

### 3. Startup Parameters Logic
Added logic to determine which view to launch based on arguments:
```python
# Determine startup parameters
startup_params = None

# Check for live scores view (both --live-scores and --live)
if getattr(args, 'live_scores', False) or getattr(args, 'live', False):
    startup_params = {'action': 'live_scores'}

# Check for league game views
for sport in ['mlb', 'nfl', 'nba', 'wnba', 'nhl', 'ncaaf', 'ncaam', 'ncaawb']:
    if getattr(args, sport, False):
        startup_params = {'action': 'league', 'league': sport.upper()}
        break

# Check for teams views
if not startup_params:
    for sport in ['mlb', 'nfl', 'nba', 'wnba', 'nhl', 'ncaaf', 'ncaam', 'ncaawb']:
        if getattr(args, f'{sport}_teams', False):
            startup_params = {'action': 'teams', 'league': sport.upper()}
            break

# Check for standings views  
if not startup_params:
    for sport in ['mlb', 'nfl', 'nba', 'wnba', 'nhl', 'ncaaf', 'ncaam', 'ncaawb']:
        if getattr(args, f'{sport}_standings', False):
            startup_params = {'action': 'standings', 'league': sport.upper()}
            break
```

### 4. Launch with Parameters
Modified the application launch to pass startup parameters:
```python
app = QApplication(sys.argv)
window = SportsScoresApp(startup_params=startup_params)  # Pass params
sys.exit(app.exec())
```

## Testing Results

### ✅ Help Output Works
```bash
$ python scores.py --help

usage: scores.py [-h] [--live-scores | --live | --mlb | --nfl | --nba |
                 --wnba | --nhl | --ncaaf | --ncaam | --ncaawb |
                 --mlb-teams | --nfl-teams | --nba-teams | --wnba-teams |
                 --nhl-teams | --ncaaf-teams | --ncaam-teams |
                 --ncaawb-teams | --mlb-standings | --nfl-standings |
                 --nba-standings | --wnba-standings | --nhl-standings |
                 --ncaaf-standings | --ncaam-standings | --ncaawb-standings]

Sports Scores Application - View live scores, standings, and team information

options:
  -h, --help          show this help message and exit
  --live-scores       Launch directly to Live Scores view (all sports)
  --live              Launch directly to Live Scores view (shorthand)
  --mlb               Launch to MLB games view
  --nfl               Launch to NFL games view
  --nba               Launch to NBA games view
  --wnba              Launch to WNBA games view
  --nhl               Launch to NHL games view
  --ncaaf             Launch to NCAA Football games view
  --ncaam             Launch to NCAA Men's Basketball games view
  --ncaawb            Launch to NCAA Women's Basketball games view
  --mlb-teams         Launch to MLB teams view
  --nfl-teams         Launch to NFL teams view
  --nba-teams         Launch to NBA teams view
  --wnba-teams        Launch to WNBA teams view
  --nhl-teams         Launch to NHL teams view
  --ncaaf-teams       Launch to NCAA Football teams view
  --ncaam-teams       Launch to NCAA Men's Basketball teams view
  --ncaawb-teams      Launch to NCAA Women's Basketball teams view
  --mlb-standings     Launch to MLB standings view
  --nfl-standings     Launch to NFL standings view
  --nba-standings     Launch to NBA standings view
  --wnba-standings    Launch to WNBA standings view
  --nhl-standings     Launch to NHL standings view
  --ncaaf-standings   Launch to NCAA Football standings view
  --ncaam-standings   Launch to NCAA Men's Basketball standings view
  --ncaawb-standings  Launch to NCAA Women's Basketball standings view

Examples:
  scores                    Launch home screen
  scores --live             Launch directly to Live Scores view (shorthand)
  scores --live-scores      Launch directly to Live Scores view (all sports)
  scores --mlb              Launch directly to MLB games
  scores --nfl              Launch directly to NFL games
  scores --mlb-teams        Launch directly to MLB teams view
  scores --nfl-standings    Launch directly to NFL standings view
```

### ✅ No Errors
- No compile or lint errors
- Full parity with main.py argument handling

## Usage Examples

```bash
# Show help
python scores.py --help

# Launch to home screen
python scores.py

# Launch directly to live scores
python scores.py --live
python scores.py --live-scores

# Launch to specific sport
python scores.py --mlb
python scores.py --nfl
python scores.py --nba
python scores.py --wnba

# Launch to teams view
python scores.py --mlb-teams
python scores.py --nba-teams

# Launch to standings view
python scores.py --nfl-standings
python scores.py --wnba-standings
```

## Files Modified
- `scores.py` - Added argparse import and full command line argument handling

## Status: COMPLETE ✅
`scores.py` now has full command line argument support identical to `main.py`.
