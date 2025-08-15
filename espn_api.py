import requests

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

LEAGUES = {
    "NFL": "football/nfl",
    "NBA": "basketball/nba",
    "MLB": "baseball/mlb",
    "NHL": "hockey/nhl",
    "WNBA": "basketball/wnba",
    "NCAAF": "football/college-football",
    "NCAAM": "basketball/mens-college-basketball",
    "Soccer": "soccer/eng.1",  # English Premier League
    # Add more as needed
}

def get_team_schedule(league_key, team_id, days_ahead=30, days_behind=30, season=None):
    """Get a team's complete schedule using the dedicated team schedule endpoint"""
    from datetime import datetime, timedelta
    
    league_path = LEAGUES.get(league_key)
    if not league_path:
        return []
    
    # Determine if we're viewing a historical season (not current year)
    current_year = datetime.now().year
    is_historical_season = season is not None and season != current_year
    
    # Use dedicated team schedule endpoints for major sports
    if league_key in ["MLB", "NFL", "NBA", "NCAAF"]:
        base_url = f"{BASE_URL}/{league_path}/teams/{team_id}/schedule"
        
        # Use appropriate season parameters for each sport
        if league_key == "NFL":
            # NFL: Use specified season or default to 2025 regular season (seasontype=2)
            season_year = season if season else 2025
            url = f"{base_url}?season={season_year}&seasontype=2"
        elif league_key == "NBA":
            # NBA: Use specified season or default to 2025-26 season (2026 = 2025-26 season)
            season_year = season if season else 2026
            url = f"{base_url}?season={season_year}"
        elif league_key == "NCAAF":
            # NCAAF: Use specified season or current year with seasontype=2 for regular season
            season_year = season if season else datetime.now().year
            url = f"{base_url}?season={season_year}&seasontype=2"
        else:  # MLB
            # MLB: Use specified season or no season parameter for current
            if season:
                url = f"{base_url}?season={season}"
            else:
                url = base_url
    else:
        # For other leagues, fall back to the date range approach
        today = datetime.now()
        start_date = today - timedelta(days=days_behind)
        end_date = today + timedelta(days=days_ahead)
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        url = f"{BASE_URL}/{league_path}/scoreboard?dates={start_str}-{end_str}"
        return parse_schedule_from_api(url, team_id, datetime.now(), season)
    
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            return []
            
        data = resp.json()
        events = data.get('events', [])
        
        # NCAAF fallback: if current year has no games, try previous year with seasontype=2
        if league_key == "NCAAF" and len(events) == 0:
            from datetime import datetime
            previous_year = datetime.now().year - 1
            fallback_url = f"{BASE_URL}/{league_path}/teams/{team_id}/schedule?season={previous_year}&seasontype=2"
            try:
                fallback_resp = requests.get(fallback_url)
                if fallback_resp.status_code == 200:
                    fallback_data = fallback_resp.json()
                    events = fallback_data.get('events', [])
            except:
                pass  # If fallback fails, continue with empty events
        
        schedule = []
        today = datetime.now()
        
        for event in events:
            # Parse event date
            event_date_str = event.get('date', '')
            if event_date_str:
                try:
                    event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                    event_date = event_date.replace(tzinfo=None)
                except:
                    continue
            else:
                continue
                
            # Get competition data
            competitions = event.get('competitions', [])
            if not competitions:
                continue
                
            comp = competitions[0]
            competitors = comp.get('competitors', [])
            
            # Find home and away teams
            home_team = away_team = None
            home_score = away_score = ''
            
            for competitor in competitors:
                team_info = competitor.get('team', {})
                if competitor.get('homeAway') == 'home':
                    home_team = team_info.get('displayName', 'Unknown')
                    score_data = competitor.get('score', '')
                    if isinstance(score_data, dict):
                        home_score = score_data.get('displayValue', '')
                    else:
                        home_score = str(score_data) if score_data else ''
                else:
                    away_team = team_info.get('displayName', 'Unknown')
                    score_data = competitor.get('score', '')
                    if isinstance(score_data, dict):
                        away_score = score_data.get('displayValue', '')
                    else:
                        away_score = str(score_data) if score_data else ''
            
            # Determine if this is home or away for our team
            team_name = None
            is_home = False
            for competitor in competitors:
                if competitor.get('team', {}).get('id') == team_id:
                    team_name = competitor.get('team', {}).get('displayName', 'Unknown')
                    is_home = competitor.get('homeAway') == 'home'
                    break
                    
            if not team_name:
                continue
                
            opponent = away_team if is_home else home_team
            home_away = 'vs' if is_home else '@'
            
            # Get game status
            status = comp.get('status', {})
            status_type = status.get('type', {})
            game_status = status_type.get('description', 'Unknown')
            
            # Get start time
            start_time = 'TBD'
            if 'shortDetail' in status_type:
                start_time = status_type['shortDetail']
            elif 'detail' in status_type:
                start_time = status_type['detail']
            
            # Get venue
            venue = comp.get('venue', {})
            venue_name = venue.get('fullName', 'TBD')
            
            # Determine date display format - include year for historical seasons
            if is_historical_season:
                date_display = event_date.strftime('%a, %b %d, %Y')
            else:
                date_display = event_date.strftime('%a, %b %d')
            
            schedule.append({
                'date': event_date.strftime('%Y-%m-%d'),
                'date_display': date_display,
                'opponent': opponent,
                'home_away': home_away,
                'time': start_time,
                'status': game_status,
                'venue': venue_name,
                'home_score': home_score,
                'away_score': away_score,
                'game_id': event.get('id', ''),
                'is_today': event_date.date() == today.date()
            })
            
        # Sort by date
        schedule.sort(key=lambda x: x['date'])
        return schedule
        
    except Exception as e:
        print(f"Error fetching team schedule: {e}")
        return []

def get_mlb_full_season_schedule(league_path, team_id, today):
    """Get full MLB season using monthly API calls to avoid 100-event limit"""
    import time
    
    schedule = []
    
    # MLB season months for 2025
    months = [
        ("20250401", "20250430"),  # April
        ("20250501", "20250531"),  # May
        ("20250601", "20250630"),  # June
        ("20250701", "20250731"),  # July
        ("20250801", "20250831"),  # August
        ("20250901", "20250930"),  # September
        ("20251001", "20251031"),  # October
    ]
    
    for start_str, end_str in months:
        url = f"{BASE_URL}/{league_path}/scoreboard?dates={start_str}-{end_str}"
        month_schedule = parse_schedule_from_api(url, team_id, today)
        schedule.extend(month_schedule)
        
        # Small delay to be respectful to the API
        time.sleep(0.1)
    
    # Sort by date
    schedule.sort(key=lambda x: x["date"])
    return schedule

def parse_schedule_from_api(url, team_id, today, season=None):
    """Parse schedule data from ESPN API response"""
    from datetime import datetime
    
    # Determine if this is a historical season
    current_year = datetime.now().year
    is_historical_season = season is not None and season != current_year
    
    schedule = []
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            events = data.get("events", [])
            
            for event in events:
                competitions = event.get("competitions", [])
                if not competitions:
                    continue
                
                comp = competitions[0]
                competitors = comp.get("competitors", [])
                
                # Check if this team is playing
                team_playing = False
                home_team = away_team = None
                home_score = away_score = ""
                
                for competitor in competitors:
                    team_info = competitor.get("team", {})
                    if team_info.get("id") == team_id:
                        team_playing = True
                    
                    if competitor.get("homeAway") == "home":
                        home_team = team_info.get("displayName", "Unknown")
                        score_data = competitor.get("score", "")
                        if isinstance(score_data, dict):
                            home_score = score_data.get("displayValue", "")
                        else:
                            home_score = str(score_data) if score_data else ""
                    else:
                        away_team = team_info.get("displayName", "Unknown")
                        score_data = competitor.get("score", "")
                        if isinstance(score_data, dict):
                            away_score = score_data.get("displayValue", "")
                        else:
                            away_score = str(score_data) if score_data else ""
                
                if team_playing:
                    # Parse event date
                    event_date_str = event.get("date", "")
                    if event_date_str:
                        try:
                            event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
                            event_date = event_date.replace(tzinfo=None)
                        except:
                            event_date = today
                    else:
                        event_date = today
                    
                    # Get game details
                    status = comp.get("status", {})
                    status_type = status.get("type", {})
                    game_status = status_type.get("description", "Unknown")
                    
                    # Get start time
                    start_time = "TBD"
                    if "shortDetail" in status_type:
                        start_time = status_type["shortDetail"]
                    elif "detail" in status_type:
                        start_time = status_type["detail"]
                    
                    # Get venue
                    venue = comp.get("venue", {})
                    venue_name = venue.get("fullName", "TBD")
                    
                    # Determine date display format - include year for historical seasons
                    if is_historical_season:
                        date_display = event_date.strftime("%a, %b %d, %Y")
                    else:
                        date_display = event_date.strftime("%a, %b %d")
                    
                    schedule.append({
                        "date": event_date.strftime("%Y-%m-%d"),
                        "date_display": date_display,
                        "opponent": away_team if home_team and team_id in [c.get("team", {}).get("id") for c in competitors if c.get("homeAway") == "home"] else home_team,
                        "home_away": "vs" if any(c.get("homeAway") == "home" and c.get("team", {}).get("id") == team_id for c in competitors) else "@",
                        "time": start_time,
                        "status": game_status,
                        "venue": venue_name,
                        "home_score": home_score,
                        "away_score": away_score,
                        "game_id": event.get("id", ""),
                        "is_today": event_date.date() == today.date()
                    })
        
    except Exception as e:
        print(f"Error fetching schedule from {url}: {e}")
    
    return schedule
def get_live_scores_all_sports():
    """Get all live games from all supported sports"""
    live_games = []
    
    for league_key in LEAGUES.keys():
        try:
            # Get today's scores for each league
            league_scores = get_scores(league_key)
            
            # Filter for only live/in-progress games
            for game in league_scores:
                status = game.get("status", "").lower()
                start_time = game.get("start_time", "").lower()
                
                # Check for various live status indicators
                # Include games that are actively in progress or recently finished
                is_live = any(live_indicator in status for live_indicator in [
                    "in progress", "live", "1st", "2nd", "3rd", "4th", "top", "bottom", 
                    "end", "overtime", "halftime", "half", "quarter", "inning"
                ])
                
                # Also check start_time for live indicators
                is_live_time = any(live_indicator in start_time for live_indicator in [
                    "1st", "2nd", "3rd", "4th", "top", "bottom", "end", "overtime", 
                    "halftime", "half", "quarter", "inning", "final"
                ])
                
                if is_live or is_live_time:
                    # Add league information to the game
                    game["league"] = league_key
                    
                    # Try to get recent play information if available
                    try:
                        game_details = get_game_details(league_key, game.get("id", ""))
                        recent_play = extract_recent_play(game_details)
                        if recent_play:
                            game["recent_play"] = recent_play
                    except:
                        # If we can't get play details, continue without them
                        pass
                    
                    live_games.append(game)
        except Exception as e:
            # Continue with other leagues if one fails
            print(f"Error fetching live scores for {league_key}: {e}")
            continue
    
    return live_games

def extract_recent_play(game_details):
    """Extract the most recent play from game details"""
    if not game_details:
        return None
    
    # Look for plays in various data structures
    plays_data = game_details.get("plays")
    if plays_data and isinstance(plays_data, list) and len(plays_data) > 0:
        # Get the most recent play
        recent_play = plays_data[-1]
        if isinstance(recent_play, dict):
            # Extract meaningful play information
            text = recent_play.get("text", "")
            description = recent_play.get("description", "")
            return text or description
    
    # Alternative: look for current situation or last play in header
    header = game_details.get("header", {})
    if header:
        situation = header.get("situation", {})
        if situation:
            last_play = situation.get("lastPlay", {})
            if last_play:
                return last_play.get("text", "")
    
    return None

def get_leagues():
    return list(LEAGUES.keys())

def get_available_seasons(league_key):
    """Get available seasons for a league
    
    Based on ESPN API historical data availability:
    - MLB: Comprehensive data from 2001 onward
    - NFL: Comprehensive data from 2001 onward  
    - NBA: Comprehensive data from 2000 onward
    - NCAAF: Comprehensive data from 2005 onward
    """
    from datetime import datetime
    current_year = datetime.now().year
    
    if league_key == "NFL":
        # NFL seasons typically go from year to year+1 (2024 season = 2024-2025)
        # ESPN has comprehensive data from 2001 onward
        return [(year, f"{year} Season") for year in range(current_year, 2000, -1)]
    elif league_key == "NBA":
        # NBA seasons are year+1 format (2025-26 season = 2026)
        # ESPN has comprehensive data from 2000-01 season onward
        return [(year, f"{year-1}-{str(year)[2:]} Season") for year in range(current_year + 1, 2000, -1)]
    elif league_key == "NCAAF":
        # NCAAF seasons are by year
        # ESPN has comprehensive data from 2005 onward
        return [(year, f"{year} Season") for year in range(current_year, 2004, -1)]
    elif league_key == "MLB":
        # MLB seasons are by year  
        # ESPN has comprehensive data from 2001 onward
        return [(year, f"{year} Season") for year in range(current_year, 2000, -1)]
    else:
        # For other leagues, return last 10 years as a reasonable default
        return [(year, f"{year} Season") for year in range(current_year, current_year - 10, -1)]

def get_scores(league_key, date=None):
    league_path = LEAGUES.get(league_key)
    if not league_path:
        return []
    
    url = f"{BASE_URL}/{league_path}/scoreboard"
    
    # Add date parameter if provided
    if date:
        date_str = date.strftime("%Y%m%d")
        url += f"?dates={date_str}"
    
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    data = resp.json()
    events = data.get("events", [])
    scores = []
    
    for event in events:
        name = event.get("name", "Unknown Game")
        eid = event.get("id", "")
        
        # Extract competition data
        competitions = event.get("competitions", [])
        if not competitions:
            continue
            
        comp = competitions[0]
        
        # Extract start time and status
        status = comp.get("status", {})
        start_time = None
        game_status = None
        if status:
            type_info = status.get("type", {})
            if "shortDetail" in type_info:
                start_time = type_info["shortDetail"]
            elif "detail" in type_info:
                start_time = type_info["detail"]
            game_status = type_info.get("description", "")
        
        # Extract scores from competitors
        competitors = comp.get("competitors", [])
        team_scores = []
        for competitor in competitors:
            team = competitor.get("team", {})
            score = competitor.get("score", "")
            home_away = competitor.get("homeAway", "")
            team_info = {
                "name": team.get("name", team.get("abbreviation", "Unknown")),
                "abbreviation": team.get("abbreviation", ""),
                "score": score,
                "home_away": home_away
            }
            team_scores.append(team_info)
        
        scores.append({
            "id": eid, 
            "name": name, 
            "start_time": start_time,
            "status": game_status,
            "teams": team_scores
        })
    return scores

def get_news(league_key):
    """Get news headlines and links for a specific league"""
    league_path = LEAGUES.get(league_key)
    if not league_path:
        return []
    url = f"{BASE_URL}/{league_path}/news"
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    data = resp.json()
    articles = data.get("articles", [])
    news_items = []
    for article in articles:
        news_item = {
            "headline": article.get("headline", "No headline"),
            "description": article.get("description", ""),
            "web_url": article.get("links", {}).get("web", {}).get("href", ""),
            "mobile_url": article.get("links", {}).get("mobile", {}).get("href", ""),
            "published": article.get("published", ""),
            "byline": article.get("byline", "")
        }
        news_items.append(news_item)
    return news_items

def get_game_details(league_key, game_id):
    league_path = LEAGUES.get(league_key)
    if not league_path:
        return {}
    url = f"{BASE_URL}/{league_path}/summary?event={game_id}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return {}
    return resp.json()

def extract_meaningful_game_info(details):
    """Extract meaningful information from game details for display"""
    if not details or not isinstance(details, dict):
        return {}
    
    info = {}
    
    # Basic game info
    if 'header' in details and 'competitions' in details['header']:
        comp = details['header']['competitions'][0]
        
        # Teams, records, and scores
        competitors = comp.get('competitors', [])
        teams = []
        scores = []
        for competitor in competitors:
            team = competitor.get('team', {})
            record = competitor.get('record', [])
            score = competitor.get('score', '')
            team_info = {
                'name': team.get('displayName', 'Unknown'),
                'abbreviation': team.get('abbreviation', 'N/A'),
                'record': record[0].get('summary', 'N/A') if record else 'N/A',
                'home_away': competitor.get('homeAway', 'unknown'),
                'score': score
            }
            teams.append(team_info)
            if score:
                scores.append(f"{team.get('name', team.get('abbreviation', 'Unknown'))}: {score}")
        info['teams'] = teams
        info['scores'] = scores
        
        # Game status and time
        status = comp.get('status', {})
        info['status'] = status.get('type', {}).get('description', 'Unknown')
        info['detailed_status'] = status.get('type', {}).get('detail', 'N/A')
        
        # Date
        info['date'] = comp.get('date', 'N/A')
    
    # Venue information
    if 'gameInfo' in details and 'venue' in details['gameInfo']:
        venue = details['gameInfo']['venue']
        info['venue'] = venue.get('fullName', 'Unknown')
        address = venue.get('address', {})
        info['venue_city'] = address.get('city', 'Unknown')
        info['venue_state'] = address.get('state', '')
    
    # Weather (if available)
    if 'gameInfo' in details and 'weather' in details['gameInfo']:
        weather = details['gameInfo']['weather']
        info['weather'] = f"{weather.get('displayValue', 'N/A')}"
        if weather.get('temperature'):
            info['temperature'] = f"{weather['temperature']}°F"
    
    # Process boxscore data properly
    if 'boxscore' in details:
        info['boxscore'] = _parse_boxscore_data(details['boxscore'])
    
    # Odds (if available)
    if 'odds' in details and details['odds']:
        odds = details['odds'][0] if details['odds'] else {}
        if 'details' in odds:
            info['betting_line'] = odds['details']
        if 'overUnder' in odds:
            info['over_under'] = f"O/U {odds['overUnder']}"
    
    # Broadcast information
    if 'broadcasts' in details and details['broadcasts']:
        networks = []
        for broadcast in details['broadcasts']:
            names = broadcast.get('names', [])
            if names:
                networks.extend(names)
        if networks:
            info['broadcast'] = ', '.join(networks)
    
    # Injuries summary
    if 'injuries' in details:
        injury_count = len(details['injuries'])
        if injury_count > 0:
            info['injuries'] = f"{injury_count} injury report(s) available"
    
    return info


def _parse_boxscore_data(boxscore_data):
    """Parse ESPN boxscore data into structured format"""
    if not boxscore_data or not isinstance(boxscore_data, dict):
        return None
    
    parsed_boxscore = {
        "teams": [],
        "players": []
    }
    
    # Parse team statistics
    teams_data = boxscore_data.get("teams", [])
    if not teams_data:
        # Sometimes boxscore data is in a different structure - try alternatives
        # Check if the entire boxscore_data is actually the teams array
        if isinstance(boxscore_data, list):
            teams_data = boxscore_data
        elif "statistics" in boxscore_data:
            # Sometimes teams data is nested under statistics
            teams_data = boxscore_data.get("statistics", [])
    
    for i, team_data in enumerate(teams_data):
        if not isinstance(team_data, dict):
            continue
            
        team_info = team_data.get("team", {})
        
        # Try multiple ways to get team name
        team_name = (team_info.get("displayName") or 
                    team_info.get("name") or 
                    team_info.get("abbreviation") or 
                    team_data.get("displayName") or
                    team_data.get("name") or
                    f"Team {i + 1}")
        
        # Parse team statistics - try multiple approaches
        team_stats = {}
        
        # Method 1: Look for statistics array
        statistics = team_data.get("statistics", [])
        
        for stat_category in statistics:
            if not isinstance(stat_category, dict):
                continue
                
            category_name = stat_category.get("name", "").lower()
            
            # Don't filter by category name - process all stats
            stats = stat_category.get("stats", [])
            
            for stat in stats:
                if not isinstance(stat, dict):
                    continue
                stat_name = stat.get("name", "")
                stat_value = stat.get("displayValue", "") or stat.get("value", "")
                if stat_name and stat_value:
                    team_stats[stat_name] = stat_value
        
        # Method 2: Look for direct stats in team data
        if not team_stats and "stats" in team_data:
            direct_stats = team_data.get("stats", {})
            if isinstance(direct_stats, dict):
                team_stats.update(direct_stats)
        
        # Only add team if we have meaningful data
        if team_name != f"Team {i + 1}" or team_stats:
            parsed_boxscore["teams"].append({
                "name": team_name,
                "stats": team_stats
            })
    
    # Parse player statistics (if available)
    players_data = boxscore_data.get("players", [])
    for i, team_players in enumerate(players_data):
        if not isinstance(team_players, dict):
            continue
            
        team_info = team_players.get("team", {})
        team_name = (team_info.get("displayName") or 
                    team_info.get("name") or 
                    team_info.get("abbreviation") or
                    f"Team {i + 1}")
        
        # Get position groups (batters, pitchers, etc.)
        statistics = team_players.get("statistics", [])
        team_player_data = {"team": team_name, "players": []}
        
        for j, stat_group in enumerate(statistics):
            if not isinstance(stat_group, dict):
                continue
                
            group_name = stat_group.get("name", "").lower()
            athletes = stat_group.get("athletes", [])
            
            # ESPN doesn't always have meaningful group names, so process all groups with athletes
            if athletes:  # Process any group that has athletes
                for athlete_data in athletes:
                    if not isinstance(athlete_data, dict):
                        continue
                        
                    athlete = athlete_data.get("athlete", {})
                    if not isinstance(athlete, dict):
                        continue
                        
                    player_name = athlete.get("displayName", "Unknown Player")
                    position = athlete.get("position", {}).get("abbreviation", "") if isinstance(athlete.get("position"), dict) else ""
                    
                    # Parse player stats
                    stats = athlete_data.get("stats", [])
                    player_stats = {
                        "name": player_name,
                        "position": position
                    }
                    
                    # Determine if this is batting or pitching based on position or stats
                    is_pitcher = position in ["P", "RP", "SP", "CP"]
                    
                    # Map common baseball stats based on player type
                    if not is_pitcher and len(stats) >= 3:
                        # Batting stats: AB, R, H, RBI, BB, SO, AVG, etc.
                        stat_names = ["ab", "r", "h", "rbi", "bb", "so", "avg"]
                        for i, stat_name in enumerate(stat_names):
                            if i < len(stats):
                                player_stats[stat_name] = stats[i]
                    elif is_pitcher and len(stats) >= 3:
                        # Pitching stats: IP, H, R, ER, BB, SO, ERA, etc.
                        stat_names = ["ip", "h", "r", "er", "bb", "so", "era"]
                        for i, stat_name in enumerate(stat_names):
                            if i < len(stats):
                                player_stats[stat_name] = stats[i]
                    else:
                        # For players with insufficient stats, just store what we have
                        for i, stat_value in enumerate(stats):
                            player_stats[f"stat_{i}"] = stat_value
                    
                    team_player_data["players"].append(player_stats)
        
        if team_player_data["players"]:
            parsed_boxscore["players"].append(team_player_data)
    
    # Return None if no meaningful data was found
    if not parsed_boxscore["teams"] and not parsed_boxscore["players"]:
        return None
    
    return parsed_boxscore


def format_complex_data(key, value):
    """Format complex data structures for better display"""
    if not value:
        return "No data available"
    
    # Handle cases where value has a "header" key (common ESPN pattern)
    if isinstance(value, dict) and "header" in value:
        # Skip the header and process the actual content
        if len(value) == 1:
            return "No content data available"
        # Process other keys in the dict besides "header"
        content_keys = [k for k in value.keys() if k != "header"]
        if content_keys:
            # Use the first non-header key's data
            actual_value = value[content_keys[0]]
            return format_complex_data(key, actual_value)
        return "No usable data found"
    if isinstance(value, dict) and "header" in value and len(value) == 1:
        return f"Available: {value['header']}"
    
    if key == "gameInfo" and isinstance(value, dict):
        info_parts = []
        # Show useful game information
        if "venue" in value:
            venue = value["venue"]
            if isinstance(venue, dict):
                venue_name = venue.get("fullName", venue.get("displayName", "Unknown Venue"))
                info_parts.append(f"Venue: {venue_name}")
        
        if "attendance" in value:
            info_parts.append(f"Attendance: {value['attendance']:,}")
        
        # Skip officials here - they're handled interactively in the main game details
        # if "officials" in value and isinstance(value["officials"], list):
        #     officials_count = len(value["officials"])
        #     if officials_count > 0:
        #         info_parts.append(f"Officials: {officials_count} assigned")
        
        if "weather" in value:
            weather = value["weather"]
            if isinstance(weather, dict):
                weather_desc = weather.get("displayValue", "")
                temp = weather.get("temperature", "")
                if weather_desc or temp:
                    weather_info = weather_desc
                    if temp:
                        weather_info += f" ({temp}°F)" if weather_desc else f"{temp}°F"
                    info_parts.append(f"Weather: {weather_info}")
        
        return "\n".join(info_parts) if info_parts else "No additional game info available"
    
    elif key == "news":
        if isinstance(value, list):
            if not value:
                return "No news available"
            headlines = []
            for item in value[:3]:  # Show first 3 items
                if isinstance(item, dict):
                    headline = item.get("headline", "")
                    if not headline:
                        headline = item.get("title", "")
                    if headline:
                        headlines.append(f"• {headline}")
            return "\n".join(headlines) if headlines else "No headlines available"
        elif isinstance(value, dict):
            if "articles" in value and isinstance(value["articles"], list):
                # Handle ESPN news format with articles array
                articles = value["articles"][:3]
                headlines = []
                for article in articles:
                    if isinstance(article, dict):
                        headline = article.get("headline", "")
                        if headline:
                            headlines.append(f"• {headline}")
                return "\n".join(headlines) if headlines else "No headlines found"
            elif "header" in value:
                # Just show that news is available
                return "News headlines available (click to view)"
            else:
                return "News section available"
        else:
            return "News available"
    
    elif key == "leaders":
        if isinstance(value, list):
            if not value:
                return "No leaders data available"
            leader_count = len(value)
            return f"Statistical leaders available ({leader_count} categories)"
        elif isinstance(value, dict):
            if "header" in value:
                category_count = len([k for k in value.keys() if k != "header"])
                return f"Statistical leaders available ({category_count} categories)"
            else:
                category_count = len(value.keys())
                return f"Statistical leaders available ({category_count} categories)"
        else:
            return "Leaders data available"
    
    elif key == "standings":
        if isinstance(value, list):
            if not value:
                return "No standings available"
            team_count = len(value)
            return f"Standings available for {team_count} teams"
        elif isinstance(value, dict):
            if "entries" in value and isinstance(value["entries"], list):
                team_count = len(value["entries"])
                return f"Standings available for {team_count} teams"
            elif "header" in value:
                return "Current standings available"
            else:
                return "Standings data available"
        else:
            return "Standings available"
    
    elif key == "injuries" and isinstance(value, list):
        if not value:
            return "No injuries reported"
        injury_count = len(value)
        return f"Injury reports available ({injury_count} players)"
    
    elif key == "broadcasts":
        if isinstance(value, list):
            if not value:
                return "No broadcast info"
            networks = []
            for broadcast in value:
                if isinstance(broadcast, dict):
                    names = broadcast.get("names", [])
                    networks.extend(names)
            return ", ".join(networks[:3]) if networks else "No networks listed"
        elif isinstance(value, dict):
            if "header" in value:
                return f"Broadcast info available: {value['header']}"
            else:
                return "Broadcast data available"
        else:
            return "Broadcast section available"
    
    elif key == "odds":
        if isinstance(value, list):
            if not value:
                return "No odds available"
            odds_info = []
            for odd in value[:2]:  # Show first 2
                if isinstance(odd, dict):
                    provider = odd.get("provider", {}).get("name", "Unknown")
                    details = odd.get("details", "No details")
                    over_under = odd.get("overUnder", "")
                    info = f"• {provider}: {details}"
                    if over_under:
                        info += f" (O/U: {over_under})"
                    odds_info.append(info)
            return "\n".join(odds_info) if odds_info else "No odds details"
        elif isinstance(value, dict):
            if "header" in value:
                return f"Odds available: {value['header']}"
            else:
                return "Odds data available"
        else:
            return "Odds section available"
    
    elif key == "boxscore" and isinstance(value, dict):
        teams = value.get("teams", [])
        if teams:
            boxscore_info = []
            for team in teams[:2]:
                if isinstance(team, dict):
                    team_info = team.get("team", {})
                    name = team_info.get("displayName", "Unknown")
                    stats = team.get("statistics", [])
                    if stats:
                        # Show a few key stats
                        key_stats = []
                        for stat in stats[:3]:
                            if isinstance(stat, dict):
                                stat_name = stat.get("name", "")
                                stat_value = stat.get("displayValue", "")
                                if stat_name and stat_value:
                                    key_stats.append(f"{stat_name}: {stat_value}")
                        if key_stats:
                            boxscore_info.append(f"• {name}: {', '.join(key_stats)}")
            return "\n".join(boxscore_info) if boxscore_info else "No boxscore data"
        return "No team stats available"
    
    elif isinstance(value, list):
        return f"List with {len(value)} items" + (f": {', '.join(str(v)[:30] + '...' if len(str(v)) > 30 else str(v) for v in value[:3])}" if value and len(str(value[0])) < 50 else "")
    
    elif isinstance(value, dict):
        if len(value) <= 3:
            # For small dicts, show the key-value pairs
            items = []
            for k, v in list(value.items())[:3]:
                if isinstance(v, (str, int, float)):
                    items.append(f"{k}: {v}")
            return "; ".join(items) if items else f"Dict with {len(value)} items"
        return f"Dict with {len(value)} items: {', '.join(list(value.keys())[:5])}"
    
    return str(value)[:100] + ("..." if len(str(value)) > 100 else "")

def get_standings(league_key):
    """Get current standings for a specific league using optimized API endpoint"""
    if league_key == "MLB":
        return _get_mlb_standings_fast()
    elif league_key == "NFL":
        return _get_nfl_standings_fast()
    elif league_key == "NBA":
        return _get_nba_standings_fast()
    elif league_key == "NCAAF":
        return _get_ncaaf_standings_fast()
    else:
        # Fallback to original method for other leagues
        return _get_standings_original(league_key)

def _get_mlb_standings_fast():
    """Fast MLB standings using dedicated endpoint (0.15s vs 7s)"""
    try:
        # Use the fast dedicated standings endpoint
        url = "https://site.api.espn.com/apis/v2/sports/baseball/mlb/standings"
        resp = requests.get(url)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        standings = []
        
        # Division mapping for games back calculation
        division_teams = {}
        
        # Process each league (AL/NL)
        for league in data.get('children', []):
            league_name = league.get('name', '')
            
            # Each league contains the standings entries
            league_standings = league.get('standings', {})
            entries = league_standings.get('entries', [])
            
            for entry in entries:
                team_info = entry.get('team', {})
                stats = entry.get('stats', [])
                
                # Create stats lookup
                stats_dict = {}
                for stat in stats:
                    stats_dict[stat.get('name', '')] = stat.get('value', 0)
                
                # Extract team data
                team_name = team_info.get('displayName', 'Unknown')
                team_id = str(team_info.get('id', ''))
                abbreviation = team_info.get('abbreviation', '')
                
                # Get wins/losses from stats
                wins = int(stats_dict.get('wins', 0))
                losses = int(stats_dict.get('losses', 0))
                win_pct = stats_dict.get('winPercent', 0.0)
                
                # Get division from team info or determine from abbreviation
                division = _get_team_division(abbreviation, league_name)
                
                # Get streak (look for streak stats)
                streak = ""
                streak_val = stats_dict.get('streak', 0)
                if streak_val != 0:
                    streak_type = "W" if streak_val > 0 else "L"
                    streak = f"{streak_type}{abs(int(streak_val))}"
                
                team_data = {
                    "team_name": team_name,
                    "team_id": team_id,
                    "abbreviation": abbreviation,
                    "wins": wins,
                    "losses": losses,
                    "win_percentage": f"{win_pct:.3f}",
                    "games_back": "0.0",  # Will calculate after grouping
                    "division": division,
                    "streak": streak,
                    "logo": team_info.get("logos", [{}])[0].get("href", "") if team_info.get("logos") else ""
                }
                
                standings.append(team_data)
                
                # Group by division for games back calculation
                if division not in division_teams:
                    division_teams[division] = []
                division_teams[division].append(team_data)
        
        # Calculate games back for each division
        for division, teams in division_teams.items():
            # Sort by wins descending, then by win percentage
            teams.sort(key=lambda x: (-x["wins"], -float(x["win_percentage"])))
            
            if teams:
                leader = teams[0]
                leader_wins = leader["wins"]
                leader_losses = leader["losses"]
                
                for i, team in enumerate(teams):
                    if i == 0:
                        team["games_back"] = "—"  # Leader
                    else:
                        team_wins = team["wins"]
                        team_losses = team["losses"]
                        games_back = ((leader_wins - team_wins) + (team_losses - leader_losses)) / 2
                        team["games_back"] = f"{games_back:.1f}" if games_back > 0 else "0.0"
        
        # Sort final standings by division, then by wins
        standings.sort(key=lambda x: (x["division"], -x["wins"], -float(x["win_percentage"])))
        
        return standings
        
    except Exception as e:
        print(f"Error in fast MLB standings: {e}")
        # Fallback to original method
        return _get_standings_original("MLB")

def _get_team_division(abbreviation, league_name):
    """Get team division from abbreviation and league"""
    # MLB Division mapping
    mlb_divisions = {
        # American League East
        "BAL": "AL East", "BOS": "AL East", "NYY": "AL East", "TB": "AL East", "TOR": "AL East",
        # American League Central  
        "CWS": "AL Central", "CLE": "AL Central", "DET": "AL Central", "KC": "AL Central", "MIN": "AL Central",
        # American League West
        "HOU": "AL West", "LAA": "AL West", "OAK": "AL West", "SEA": "AL West", "TEX": "AL West",
        # National League East
        "ATL": "NL East", "MIA": "NL East", "NYM": "NL East", "PHI": "NL East", "WSH": "NL East",
        # National League Central
        "CHC": "NL Central", "CIN": "NL Central", "MIL": "NL Central", "PIT": "NL Central", "STL": "NL Central",
        # National League West
        "ARI": "NL West", "COL": "NL West", "LAD": "NL West", "SD": "NL West", "SF": "NL West"
    }
    
    # Handle Oakland abbreviation
    if abbreviation == "ATH":
        abbreviation = "OAK"
    
    return mlb_divisions.get(abbreviation, f"{league_name} League")

def _get_nfl_standings_fast():
    """Fast NFL standings using dedicated endpoint"""
    try:
        url = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
        resp = requests.get(url)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        standings = []
        
        # NFL divisions mapping
        nfl_divisions = {
            # AFC East
            "BUF": "AFC East", "MIA": "AFC East", "NE": "AFC East", "NYJ": "AFC East",
            # AFC North  
            "BAL": "AFC North", "CIN": "AFC North", "CLE": "AFC North", "PIT": "AFC North",
            # AFC South
            "HOU": "AFC South", "IND": "AFC South", "JAX": "AFC South", "TEN": "AFC South",
            # AFC West
            "DEN": "AFC West", "KC": "AFC West", "LV": "AFC West", "LAC": "AFC West",
            # NFC East
            "DAL": "NFC East", "NYG": "NFC East", "PHI": "NFC East", "WSH": "NFC East",
            # NFC North
            "CHI": "NFC North", "DET": "NFC North", "GB": "NFC North", "MIN": "NFC North",
            # NFC South
            "ATL": "NFC South", "CAR": "NFC South", "NO": "NFC South", "TB": "NFC South",
            # NFC West
            "ARI": "NFC West", "LAR": "NFC West", "SF": "NFC West", "SEA": "NFC West"
        }
        
        # Process each conference
        division_teams = {}
        for conference in data.get('children', []):
            conf_standings = conference.get('standings', {})
            entries = conf_standings.get('entries', [])
            
            for entry in entries:
                team_info = entry.get('team', {})
                stats = entry.get('stats', [])
                
                # Create stats lookup
                stats_dict = {}
                for stat in stats:
                    stats_dict[stat.get('name', '')] = stat.get('value', 0)
                
                # Extract team data
                team_name = team_info.get('displayName', 'Unknown')
                team_id = str(team_info.get('id', ''))
                abbreviation = team_info.get('abbreviation', '')
                
                # Get wins/losses from stats
                wins = int(stats_dict.get('wins', 0))
                losses = int(stats_dict.get('losses', 0))
                ties = int(stats_dict.get('ties', 0))
                win_pct = stats_dict.get('winPercent', 0.0)
                
                # Get division
                division = nfl_divisions.get(abbreviation, "Unknown Division")
                
                # NFL record format includes ties
                record_display = f"{wins}-{losses}"
                if ties > 0:
                    record_display += f"-{ties}"
                
                team_data = {
                    "team_name": team_name,
                    "team_id": team_id,
                    "abbreviation": abbreviation,
                    "wins": wins,
                    "losses": losses,
                    "ties": ties,
                    "win_percentage": f"{win_pct:.3f}",
                    "games_back": "0.0",
                    "division": division,
                    "streak": "",  # Can be enhanced later
                    "logo": team_info.get("logos", [{}])[0].get("href", "") if team_info.get("logos") else "",
                    "record_display": record_display
                }
                
                standings.append(team_data)
                
                if division not in division_teams:
                    division_teams[division] = []
                division_teams[division].append(team_data)
        
        # Calculate games back for each division
        for division, teams in division_teams.items():
            teams.sort(key=lambda x: (-x["wins"], x["losses"]))
            
            if teams:
                leader = teams[0]
                leader_wins = leader["wins"]
                leader_losses = leader["losses"]
                
                for i, team in enumerate(teams):
                    if i == 0:
                        team["games_back"] = "—"
                    else:
                        team_wins = team["wins"]
                        team_losses = team["losses"]
                        games_back = ((leader_wins - team_wins) + (team_losses - leader_losses)) / 2
                        team["games_back"] = f"{games_back:.1f}" if games_back > 0 else "0.0"
        
        # Sort by division, then by wins
        standings.sort(key=lambda x: (x["division"], -x["wins"], x["losses"]))
        
        return standings
        
    except Exception as e:
        print(f"Error in fast NFL standings: {e}")
        return _get_standings_original("NFL")

def _get_nba_standings_fast():
    """Fast NBA standings using dedicated endpoint"""
    try:
        # Use 2025-26 season (season=2026) for fresh standings with all teams at 0-0
        url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings?season=2026"
        resp = requests.get(url)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        standings = []
        
        # NBA divisions mapping
        nba_divisions = {
            # Eastern Conference - Atlantic
            "BOS": "Atlantic", "BKN": "Atlantic", "NYK": "Atlantic", "NY": "Atlantic", "PHI": "Atlantic", "TOR": "Atlantic",
            # Eastern Conference - Central
            "CHI": "Central", "CLE": "Central", "DET": "Central", "IND": "Central", "MIL": "Central",
            # Eastern Conference - Southeast
            "ATL": "Southeast", "CHA": "Southeast", "MIA": "Southeast", "ORL": "Southeast", "WSH": "Southeast",
            # Western Conference - Northwest
            "DEN": "Northwest", "MIN": "Northwest", "OKC": "Northwest", "POR": "Northwest", "UTA": "Northwest", "UTAH": "Northwest",
            # Western Conference - Pacific
            "GSW": "Pacific", "GS": "Pacific", "LAC": "Pacific", "LAL": "Pacific", "PHX": "Pacific", "SAC": "Pacific",
            # Western Conference - Southwest
            "DAL": "Southwest", "HOU": "Southwest", "MEM": "Southwest", "NO": "Southwest", "SA": "Southwest"
        }
        
        # Process each conference
        division_teams = {}
        has_entries = False
        
        # Check if any conference has entries
        for conference in data.get('children', []):
            conf_standings = conference.get('standings', {})
            if conf_standings.get('entries', []):
                has_entries = True
                break
        
        # If no entries (early season), create fresh 0-0 standings from teams endpoint
        if not has_entries:
            return _get_nba_fresh_standings()
        
        for conference in data.get('children', []):
            conf_name = conference.get('name', '')
            conf_standings = conference.get('standings', {})
            entries = conf_standings.get('entries', [])
            
            for entry in entries:
                team_info = entry.get('team', {})
                stats = entry.get('stats', [])
                
                # Create stats lookup
                stats_dict = {}
                for stat in stats:
                    stats_dict[stat.get('name', '')] = stat.get('value', 0)
                
                # Extract team data
                team_name = team_info.get('displayName', 'Unknown')
                team_id = str(team_info.get('id', ''))
                abbreviation = team_info.get('abbreviation', '')
                
                # Get wins/losses from stats
                wins = int(stats_dict.get('wins', 0))
                losses = int(stats_dict.get('losses', 0))
                win_pct = stats_dict.get('winPercent', 0.0)
                
                # Get division with conference prefix
                base_division = nba_divisions.get(abbreviation, "Unknown")
                division = f"{conf_name} {base_division}" if base_division != "Unknown" else conf_name
                
                team_data = {
                    "team_name": team_name,
                    "team_id": team_id,
                    "abbreviation": abbreviation,
                    "wins": wins,
                    "losses": losses,
                    "win_percentage": f"{win_pct:.3f}",
                    "games_back": "0.0",
                    "division": division,
                    "streak": "",
                    "logo": team_info.get("logos", [{}])[0].get("href", "") if team_info.get("logos") else ""
                }
                
                standings.append(team_data)
                
                if division not in division_teams:
                    division_teams[division] = []
                division_teams[division].append(team_data)
        
        # Calculate games back for each division
        for division, teams in division_teams.items():
            teams.sort(key=lambda x: (-x["wins"], x["losses"]))
            
            if teams:
                leader = teams[0]
                leader_wins = leader["wins"]
                leader_losses = leader["losses"]
                
                for i, team in enumerate(teams):
                    if i == 0:
                        team["games_back"] = "—"
                    else:
                        team_wins = team["wins"]
                        team_losses = team["losses"]
                        games_back = ((leader_wins - team_wins) + (team_losses - leader_losses)) / 2
                        team["games_back"] = f"{games_back:.1f}" if games_back > 0 else "0.0"
        
        # Sort by division, then by wins
        standings.sort(key=lambda x: (x["division"], -x["wins"], x["losses"]))
        
        return standings
        
    except Exception as e:
        print(f"Error in fast NBA standings: {e}")
        return _get_standings_original("NBA")

def _get_nba_fresh_standings():
    """Create fresh NBA standings with all teams at 0-0 for new season"""
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        resp = requests.get(url)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        standings = []
        
        # NBA divisions mapping (same as main function)
        nba_divisions = {
            # Eastern Conference - Atlantic
            "BOS": "Atlantic", "BKN": "Atlantic", "NYK": "Atlantic", "NY": "Atlantic", "PHI": "Atlantic", "TOR": "Atlantic",
            # Eastern Conference - Central
            "CHI": "Central", "CLE": "Central", "DET": "Central", "IND": "Central", "MIL": "Central",
            # Eastern Conference - Southeast
            "ATL": "Southeast", "CHA": "Southeast", "MIA": "Southeast", "ORL": "Southeast", "WSH": "Southeast",
            # Western Conference - Northwest
            "DEN": "Northwest", "MIN": "Northwest", "OKC": "Northwest", "POR": "Northwest", "UTA": "Northwest", "UTAH": "Northwest",
            # Western Conference - Pacific
            "GSW": "Pacific", "GS": "Pacific", "LAC": "Pacific", "LAL": "Pacific", "PHX": "Pacific", "SAC": "Pacific",
            # Western Conference - Southwest
            "DAL": "Southwest", "HOU": "Southwest", "MEM": "Southwest", "NO": "Southwest", "SA": "Southwest"
        }
        
        # Conference mapping based on divisions
        eastern_divisions = ["Atlantic", "Central", "Southeast"]
        western_divisions = ["Northwest", "Pacific", "Southwest"]
        
        # Get teams from API
        if 'sports' in data and data['sports']:
            leagues = data['sports'][0].get('leagues', [])
            if leagues:
                teams = leagues[0].get('teams', [])
                
                for team in teams:
                    team_info = team.get('team', {})
                    
                    team_name = team_info.get('displayName', 'Unknown')
                    team_id = str(team_info.get('id', ''))
                    abbreviation = team_info.get('abbreviation', '')
                    
                    # Get division
                    base_division = nba_divisions.get(abbreviation, "Unknown")
                    
                    # Determine conference
                    if base_division in eastern_divisions:
                        conference = "Eastern Conference"
                    elif base_division in western_divisions:
                        conference = "Western Conference"
                    else:
                        conference = "Unknown Conference"
                    
                    division = f"{conference} {base_division}" if base_division != "Unknown" else conference
                    
                    # Create fresh team data with 0-0 record
                    team_data = {
                        "team_name": team_name,
                        "team_id": team_id,
                        "abbreviation": abbreviation,
                        "wins": 0,
                        "losses": 0,
                        "win_percentage": "0.000",
                        "games_back": "—",
                        "division": division,
                        "streak": "",
                        "logo": team_info.get("logos", [{}])[0].get("href", "") if team_info.get("logos") else ""
                    }
                    
                    standings.append(team_data)
        
        # Sort by division, then by team name (since all records are 0-0)
        standings.sort(key=lambda x: (x["division"], x["team_name"]))
        
        return standings
        
    except Exception as e:
        print(f"Error in fresh NBA standings: {e}")
        return []

def _get_ncaaf_standings_fast():
    """Fast NCAAF standings using dedicated endpoint"""
    try:
        url = "https://site.api.espn.com/apis/v2/sports/football/college-football/standings"
        resp = requests.get(url)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        standings = []
        
        # Process each conference/group
        for conference in data.get('children', []):
            conf_name = conference.get('name', 'Independent')
            conf_standings = conference.get('standings', {})
            entries = conf_standings.get('entries', [])
            
            for entry in entries:
                team_info = entry.get('team', {})
                stats = entry.get('stats', [])
                
                # Create stats lookup
                stats_dict = {}
                for stat in stats:
                    stats_dict[stat.get('name', '')] = stat.get('value', 0)
                
                # Extract team data
                team_name = team_info.get('displayName', 'Unknown')
                team_id = str(team_info.get('id', ''))
                abbreviation = team_info.get('abbreviation', '')
                
                # Get wins/losses from stats
                wins = int(stats_dict.get('wins', 0))
                losses = int(stats_dict.get('losses', 0))
                win_pct = stats_dict.get('winPercent', 0.0)
                
                team_data = {
                    "team_name": team_name,
                    "team_id": team_id,
                    "abbreviation": abbreviation,
                    "wins": wins,
                    "losses": losses,
                    "win_percentage": f"{win_pct:.3f}",
                    "games_back": "—",  # College football doesn't use games back
                    "division": conf_name,  # Conference name as division
                    "streak": "",
                    "logo": team_info.get("logos", [{}])[0].get("href", "") if team_info.get("logos") else ""
                }
                
                standings.append(team_data)
        
        # Sort by conference, then by wins
        standings.sort(key=lambda x: (x["division"], -x["wins"], x["losses"]))
        
        return standings
        
    except Exception as e:
        print(f"Error in fast NCAAF standings: {e}")
        return _get_standings_original("NCAAF")

def _get_standings_original(league_key):
    """Original standings method (slower but works for all leagues)"""
    league_path = LEAGUES.get(league_key)
    if not league_path:
        return []
    
    # Use teams API to get all teams and their records
    teams_url = f"{BASE_URL}/{league_path}/teams"
    resp = requests.get(teams_url)
    
    if resp.status_code != 200:
        return []
    
    data = resp.json()
    return _parse_standings_from_teams_api(data, league_key)

def _parse_standings_from_teams_api(data, league_key):
    """Parse standings from the teams API with detailed team records"""
    standings = []
    
    # MLB Division mapping - Fixed Oakland abbreviation
    mlb_divisions = {
        # American League East
        "BAL": "AL East", "BOS": "AL East", "NYY": "AL East", "TB": "AL East", "TOR": "AL East",
        # American League Central  
        "CWS": "AL Central", "CLE": "AL Central", "DET": "AL Central", "KC": "AL Central", "MIN": "AL Central",
        # American League West
        "HOU": "AL West", "LAA": "AL West", "OAK": "AL West", "SEA": "AL West", "TEX": "AL West",
        # National League East
        "ATL": "NL East", "MIA": "NL East", "NYM": "NL East", "PHI": "NL East", "WSH": "NL East",
        # National League Central
        "CHC": "NL Central", "CIN": "NL Central", "MIL": "NL Central", "PIT": "NL Central", "STL": "NL Central",
        # National League West
        "ARI": "NL West", "COL": "NL West", "LAD": "NL West", "SD": "NL West", "SF": "NL West"
    }
    
    try:
        # Navigate through the teams structure
        sports = data.get("sports", [])
        if not sports:
            return []
            
        leagues = sports[0].get("leagues", [])
        if not leagues:
            return []
            
        teams = leagues[0].get("teams", [])
        
        for team_entry in teams:
            team = team_entry.get("team", {})
            
            # Get team info
            team_name = team.get("displayName", "Unknown")
            abbreviation = team.get("abbreviation", "")
            team_id = team.get("id", "")
            
            # Get division from mapping (fix Oakland)
            if abbreviation == "ATH":  # ESPN uses ATH for Athletics
                abbreviation = "OAK"   # But our mapping uses OAK
            division = mlb_divisions.get(abbreviation, "League") if league_key == "MLB" else "League"
            
            # Get detailed team record by making individual API call
            wins, losses, win_pct, streak = _get_team_record(team_id, league_key)
            
            standings.append({
                "team_name": team_name,
                "team_id": team_id,
                "abbreviation": abbreviation,
                "wins": wins,
                "losses": losses,
                "win_percentage": win_pct,
                "games_back": "N/A",  # We'll calculate this after sorting by division
                "division": division,
                "streak": streak,  # Add streak information
                "logo": team.get("logos", [{}])[0].get("href", "") if team.get("logos") else ""
            })
        
        # Sort by division, then by wins (descending), then by win percentage
        standings.sort(key=lambda x: (x["division"], -int(x["wins"]), -float(x["win_percentage"])))
        
        # Calculate games back within each division
        if standings:
            # Group by division and calculate games back for each division
            divisions = {}
            for team in standings:
                div = team["division"]
                if div not in divisions:
                    divisions[div] = []
                divisions[div].append(team)
            
            # Calculate games back for each division
            for div_name, div_teams in divisions.items():
                if div_teams:
                    leader_wins = int(div_teams[0]["wins"])
                    leader_losses = int(div_teams[0]["losses"])
                    
                    for i, team in enumerate(div_teams):
                        if i == 0:
                            team["games_back"] = "—"  # Leader
                        else:
                            team_wins = int(team["wins"])
                            team_losses = int(team["losses"])
                            games_back = ((leader_wins - team_wins) + (team_losses - leader_losses)) / 2
                            team["games_back"] = f"{games_back:.1f}" if games_back > 0 else "0.0"
        
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error parsing teams API data: {e}")
        return []
    
    return standings

def _get_team_record(team_id, league_key):
    """Get individual team's win/loss record with streak information"""
    if not team_id:
        return 0, 0, "0.000", ""
        
    league_path = LEAGUES.get(league_key)
    if not league_path:
        return 0, 0, "0.000", ""
    
    try:
        # Get detailed team information
        team_url = f"{BASE_URL}/{league_path}/teams/{team_id}"
        resp = requests.get(team_url)
        
        if resp.status_code != 200:
            return 0, 0, "0.000", ""
        
        data = resp.json()
        team = data.get("team", {})
        record = team.get("record", {})
        items = record.get("items", [])
        
        # Look for overall record
        for item in items:
            if item.get("type") == "total":
                summary = item.get("summary", "0-0")
                stats = item.get("stats", [])
                
                # Extract basic record info
                try:
                    # Parse summary like "54-61"
                    wins, losses = map(int, summary.split("-"))
                    total_games = wins + losses
                    win_pct = f"{wins/total_games:.3f}" if total_games > 0 else "0.000"
                except (ValueError, IndexError):
                    wins, losses, win_pct = 0, 0, "0.000"
                
                # Extract streak information from stats
                streak = ""
                for stat in stats:
                    if stat.get("name") == "streak":
                        streak_value = stat.get("value", 0)
                        if isinstance(streak_value, (int, float)) and streak_value != 0:
                            if streak_value > 0:
                                streak = f"W{int(streak_value)}"
                            else:
                                streak = f"L{int(abs(streak_value))}"
                        break
                
                return wins, losses, win_pct, streak
        
        return 0, 0, "0.000", ""
        
    except Exception as e:
        print(f"Error getting team {team_id} record: {e}")
        return 0, 0, "0.000", ""

def _parse_standings_from_api(data, league_key):
    """Parse standings from the dedicated standings API"""
    standings = []
    
    # MLB Division mapping
    mlb_divisions = {
        # American League East
        "BAL": "AL East", "BOS": "AL East", "NYY": "AL East", "TB": "AL East", "TOR": "AL East",
        # American League Central  
        "CWS": "AL Central", "CLE": "AL Central", "DET": "AL Central", "KC": "AL Central", "MIN": "AL Central",
        # American League West
        "HOU": "AL West", "LAA": "AL West", "OAK": "AL West", "SEA": "AL West", "TEX": "AL West",
        # National League East
        "ATL": "NL East", "MIA": "NL East", "NYM": "NL East", "PHI": "NL East", "WSH": "NL East",
        # National League Central
        "CHC": "NL Central", "CIN": "NL Central", "MIL": "NL Central", "PIT": "NL Central", "STL": "NL Central",
        # National League West
        "ARI": "NL West", "COL": "NL West", "LAD": "NL West", "SD": "NL West", "SF": "NL West"
    }
    
    try:
        # Navigate through the standings structure
        children = data.get("children", [])
        
        for child in children:
            standings_entries = child.get("standings", {}).get("entries", [])
            division_name = child.get("name", "League")
            
            # For MLB, use our custom division mapping instead of ESPN's division names
            if league_key == "MLB":
                for entry in standings_entries:
                    team = entry.get("team", {})
                    abbreviation = team.get("abbreviation", "")
                    division = mlb_divisions.get(abbreviation, "League")
                    
                    # Extract stats
                    stats = entry.get("stats", [])
                    wins = losses = win_pct = games_back = ""
                    
                    for stat in stats:
                        stat_name = stat.get("name", "")
                        if stat_name == "wins":
                            wins = stat.get("value", 0)
                        elif stat_name == "losses":
                            losses = stat.get("value", 0)
                        elif stat_name == "winPercent":
                            win_pct = f"{float(stat.get('value', 0)):.3f}"
                        elif stat_name == "gamesBehind":
                            games_back = stat.get("displayValue", "0.0")
                    
                    standings.append({
                        "team_name": team.get("displayName", "Unknown"),
                        "abbreviation": abbreviation,
                        "wins": wins,
                        "losses": losses,
                        "win_percentage": win_pct,
                        "games_back": games_back,
                        "division": division,
                        "logo": team.get("logo", "")
                    })
            else:
                # For other leagues, use ESPN's division structure
                for entry in standings_entries:
                    team = entry.get("team", {})
                    
                    # Extract stats
                    stats = entry.get("stats", [])
                    wins = losses = win_pct = games_back = ""
                    
                    for stat in stats:
                        stat_name = stat.get("name", "")
                        if stat_name == "wins":
                            wins = stat.get("value", 0)
                        elif stat_name == "losses":
                            losses = stat.get("value", 0)
                        elif stat_name == "winPercent":
                            win_pct = f"{float(stat.get('value', 0)):.3f}"
                        elif stat_name == "gamesBehind":
                            games_back = stat.get("displayValue", "0.0")
                    
                    standings.append({
                        "team_name": team.get("displayName", "Unknown"),
                        "abbreviation": team.get("abbreviation", ""),
                        "wins": wins,
                        "losses": losses,
                        "win_percentage": win_pct,
                        "games_back": games_back,
                        "division": division_name,
                        "logo": team.get("logo", "")
                    })
        
        # Sort by division, then by wins (descending), then by win percentage
        standings.sort(key=lambda x: (x["division"], -int(x["wins"]) if isinstance(x["wins"], int) else 0, -float(x["win_percentage"]) if x["win_percentage"] else 0))
        
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error parsing standings API data: {e}")
        return []
    
    return standings

def _parse_standings_from_scoreboard(data, league_key):
    """Parse standings from scoreboard API (fallback method)"""
    standings = []
    teams_seen = set()  # To avoid duplicates
    
    # MLB Division mapping
    mlb_divisions = {
        # American League East
        "BAL": "AL East", "BOS": "AL East", "NYY": "AL East", "TB": "AL East", "TOR": "AL East",
        # American League Central  
        "CWS": "AL Central", "CLE": "AL Central", "DET": "AL Central", "KC": "AL Central", "MIN": "AL Central",
        # American League West
        "HOU": "AL West", "LAA": "AL West", "OAK": "AL West", "SEA": "AL West", "TEX": "AL West",
        # National League East
        "ATL": "NL East", "MIA": "NL East", "NYM": "NL East", "PHI": "NL East", "WSH": "NL East",
        # National League Central
        "CHC": "NL Central", "CIN": "NL Central", "MIL": "NL Central", "PIT": "NL Central", "STL": "NL Central",
        # National League West
        "ARI": "NL West", "COL": "NL West", "LAD": "NL West", "SD": "NL West", "SF": "NL West"
    }
    
    try:
        events = data.get("events", [])
        
        for event in events:
            competitions = event.get("competitions", [])
            if not competitions:
                continue
                
            comp = competitions[0]
            competitors = comp.get("competitors", [])
            
            for competitor in competitors:
                team_data = competitor.get("team", {})
                team_id = team_data.get("id", "")
                
                # Skip if we've already processed this team
                if team_id in teams_seen:
                    continue
                teams_seen.add(team_id)
                
                # Get team info
                team_name = team_data.get("displayName", "Unknown")
                abbreviation = team_data.get("abbreviation", "")
                
                # Get division from mapping
                division = mlb_divisions.get(abbreviation, "League") if league_key == "MLB" else "League"
                
                # Get record information
                records = competitor.get("records", [])
                wins = losses = 0
                
                # Look for the overall record
                for record in records:
                    if record.get("name") == "overall":
                        summary = record.get("summary", "0-0")
                        try:
                            wins, losses = map(int, summary.split("-"))
                        except ValueError:
                            wins = losses = 0
                        break
                
                # Calculate win percentage
                total_games = wins + losses
                win_pct = f"{wins/total_games:.3f}" if total_games > 0 else "0.000"
                
                standings.append({
                    "team_name": team_name,
                    "abbreviation": abbreviation,
                    "wins": wins,
                    "losses": losses,
                    "win_percentage": win_pct,
                    "games_back": "N/A",  # We'll calculate this after sorting by division
                    "division": division,
                    "logo": team_data.get("logo", "")
                })
        
        # Sort by division, then by wins (descending), then by win percentage
        standings.sort(key=lambda x: (x["division"], -int(x["wins"]), -float(x["win_percentage"])))
        
        # Calculate games back within each division
        if standings:
            # Group by division and calculate games back for each division
            divisions = {}
            for team in standings:
                div = team["division"]
                if div not in divisions:
                    divisions[div] = []
                divisions[div].append(team)
            
            # Calculate games back for each division
            for div_name, div_teams in divisions.items():
                if div_teams:
                    leader_wins = int(div_teams[0]["wins"])
                    leader_losses = int(div_teams[0]["losses"])
                    
                    for i, team in enumerate(div_teams):
                        if i == 0:
                            team["games_back"] = "—"  # Leader
                        else:
                            team_wins = int(team["wins"])
                            team_losses = int(team["losses"])
                            games_back = ((leader_wins - team_wins) + (team_losses - leader_losses)) / 2
                            team["games_back"] = f"{games_back:.1f}" if games_back > 0 else "0.0"
        
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error parsing scoreboard data: {e}")
        return []
    
    return standings

def parse_standings_entry(entry, division="League"):
    """Parse a single standings entry"""
    if not entry or "team" not in entry:
        return None
    
    team = entry["team"]
    stats = entry.get("stats", [])
    
    # Extract common statistics
    wins = losses = win_pct = games_back = ""
    
    for stat in stats:
        if stat.get("name") == "wins":
            wins = stat.get("value", 0)
        elif stat.get("name") == "losses":
            losses = stat.get("value", 0)
        elif stat.get("name") == "winPercent":
            win_pct = f"{float(stat.get('value', 0)):.3f}"
        elif stat.get("name") == "gamesBehind":
            games_back = stat.get("displayValue", "0.0")
    
    return {
        "team_name": team.get("displayName", "Unknown"),
        "abbreviation": team.get("abbreviation", ""),
        "wins": wins,
        "losses": losses,
        "win_percentage": win_pct,
        "games_back": games_back,
        "division": division,
        "logo": team.get("logo", "")
    }
