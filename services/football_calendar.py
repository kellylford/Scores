import requests
from datetime import datetime, date as date_type

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
CORE_BASE = "https://sports.core.api.espn.com/v2/sports"

_WEEK_DATE_CACHE: dict = {}  # (league_key, season, season_type, week) -> (start_YYYYMMDD, end_YYYYMMDD)


def get_football_season_year(league_key="NFL", today=None):
    """Return the ESPN season year for the given date and league.

    ESPN names a football season by the calendar year it *starts* in
    (e.g., the season that kicks off September 2026 is 'year 2026').
    - January–February: still inside the previous year's playoffs/Super Bowl
    - March–December: we're either in the upcoming season or deep in the
      current one, so the current calendar year is correct.
    """
    today = today or datetime.now().date()
    if isinstance(today, datetime):
        today = today.date()
    if today.month <= 2:
        return today.year - 1
    return today.year

# This function fetches the NFL or NCAAF calendar (weeks and date ranges)
def get_football_calendar(league_key, season=None):
    league_path = {
        "NFL": "football/nfl",
        "NCAAF": "football/college-football"
    }.get(league_key)
    if not league_path:
        return []
    
    # Use current season if none specified, try without season parameter first
    if season:
        url = f"{BASE_URL}/{league_path}/scoreboard?season={season}"
    else:
        url = f"{BASE_URL}/{league_path}/scoreboard"
    
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    data = resp.json()
    
    leagues = data.get('leagues', [])
    if not leagues:
        return []
    
    calendar = []
    # Get all calendar types (preseason, regular season, postseason)
    for cal in leagues[0].get('calendar', []):
        cal_label = cal.get('label', '').lower()
        for entry in cal.get('entries', []):
            calendar.append({
                'label': entry.get('label'),
                'week': int(entry.get('value', 0)),
                'start': entry.get('startDate'),
                'end': entry.get('endDate'),
                'season_type': cal_label
            })
    return calendar

# This function finds the current week number for NFL/NCAAF based on today
def get_current_football_week(league_key, season=None, today=None):
    league_path = {
        "NFL": "football/nfl",
        "NCAAF": "football/college-football"
    }.get(league_key)
    if not league_path:
        return None

    today = today or datetime.now().date()
    if isinstance(today, datetime):
        today = today.date()

    # Resolve season year so we always query the right season
    if season is None:
        season = get_football_season_year(league_key, today)

    url = f"{BASE_URL}/{league_path}/scoreboard?season={season}"

    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            # Use the week ESPN says is current for this season
            current_week = data.get('week', {}).get('number')
            if current_week:
                return current_week
    except Exception:
        pass

    # Fallback: scan the calendar for a week that brackets today
    calendar = get_football_calendar(league_key, season)
    if not calendar:
        return 1

    for entry in calendar:
        try:
            start = datetime.fromisoformat(entry['start'].replace('Z', '+00:00')).date()
            end = datetime.fromisoformat(entry['end'].replace('Z', '+00:00')).date()
            if start <= today <= end:
                return entry['week']
        except Exception:
            continue

    # Off-season or no matching week: default to week 1
    return 1


def get_week_dates(league_key, week_num, season, season_type=2):
    """Return (start_YYYYMMDD, end_YYYYMMDD) for a specific week via the ESPN Core API.

    Uses the same approach as the iOS app: Core API gives authoritative date bounds,
    which are then used with the site scoreboard's dates= parameter (avoiding the ESPN
    bug where season= and week= params together return the wrong season).

    Returns (None, None) on failure.
    """
    cache_key = (league_key, season, season_type, week_num)
    if cache_key in _WEEK_DATE_CACHE:
        return _WEEK_DATE_CACHE[cache_key]

    league_map = {"NFL": "nfl", "NCAAF": "college-football"}
    league = league_map.get(league_key, league_key.lower())
    sport = "football"

    url = (f"{CORE_BASE}/{sport}/leagues/{league}"
           f"/seasons/{season}/types/{season_type}/weeks/{week_num}")
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            _WEEK_DATE_CACHE[cache_key] = (None, None)
            return None, None
        data = resp.json()
        start_iso = data.get("startDate", "")
        end_iso = data.get("endDate", "")
        if not start_iso or not end_iso:
            _WEEK_DATE_CACHE[cache_key] = (None, None)
            return None, None
        start_str = datetime.fromisoformat(start_iso.replace("Z", "+00:00")).strftime("%Y%m%d")
        end_str = datetime.fromisoformat(end_iso.replace("Z", "+00:00")).strftime("%Y%m%d")
        _WEEK_DATE_CACHE[cache_key] = (start_str, end_str)
        return start_str, end_str
    except Exception as e:
        print(f"[get_week_dates] {league_key} {season}/t{season_type}/w{week_num}: {e}")
        _WEEK_DATE_CACHE[cache_key] = (None, None)
        return None, None
