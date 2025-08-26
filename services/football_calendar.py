import requests
from datetime import datetime

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

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
    
    # First try to get current week directly from the API
    if season:
        url = f"{BASE_URL}/{league_path}/scoreboard?season={season}"
    else:
        url = f"{BASE_URL}/{league_path}/scoreboard"
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            # Check if there's a current week in the response
            week_info = data.get('week', {})
            current_week = week_info.get('number')
            if current_week:
                return current_week
    except Exception:
        pass
    
    # Fallback: use calendar method
    calendar = get_football_calendar(league_key, season)
    if not calendar:
        return 1  # Default to week 1 if no calendar available
    
    today = today or datetime.now().date()
    for entry in calendar:
        try:
            start = datetime.fromisoformat(entry['start'].replace('Z', '+00:00')).date()
            end = datetime.fromisoformat(entry['end'].replace('Z', '+00:00')).date()
            if start <= today <= end:
                return entry['week']
        except Exception:
            continue
    
    # If no current week found, default to week 1
    return 1
