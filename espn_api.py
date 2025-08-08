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

def get_leagues():
    return list(LEAGUES.keys())

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
                "name": team.get("displayName", "Unknown"),
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
                scores.append(f"{team.get('abbreviation', team.get('displayName', 'Unknown'))}: {score}")
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
    print(f"DEBUG: _parse_boxscore_data called with: {type(boxscore_data)}")
    if boxscore_data:
        print(f"DEBUG: boxscore_data keys: {list(boxscore_data.keys()) if isinstance(boxscore_data, dict) else 'not a dict'}")
    
    if not boxscore_data or not isinstance(boxscore_data, dict):
        print("DEBUG: No boxscore data or not a dict - returning None")
        return None
    
    parsed_boxscore = {
        "teams": [],
        "players": []
    }
    
    # Parse team statistics
    teams_data = boxscore_data.get("teams", [])
    print(f"DEBUG: Found {len(teams_data)} teams in boxscore data")
    for team_data in teams_data:
        team_info = team_data.get("team", {})
        team_name = team_info.get("displayName", "Unknown Team")
        
        # Parse team statistics
        team_stats = {}
        statistics = team_data.get("statistics", [])
        for stat_category in statistics:
            category_name = stat_category.get("name", "").lower()
            if category_name in ["batting", "pitching", "fielding"]:
                stats = stat_category.get("stats", [])
                for stat in stats:
                    stat_name = stat.get("name", "")
                    stat_value = stat.get("displayValue", "")
                    if stat_name and stat_value:
                        # Only include key stats to avoid clutter
                        if stat_name in ["hits", "runs", "errors", "atBats", "rbi", "homeRuns", 
                                       "avg", "strikeouts", "walks", "era", "wins", "losses", "saves"]:
                            team_stats[stat_name] = stat_value
        
        parsed_boxscore["teams"].append({
            "name": team_name,
            "stats": team_stats
        })
    
    # Parse player statistics (if available)
    players_data = boxscore_data.get("players", [])
    print(f"DEBUG: Found {len(players_data)} player groups in boxscore data")
    for i, team_players in enumerate(players_data):
        print(f"DEBUG: Player group {i} has keys: {list(team_players.keys()) if isinstance(team_players, dict) else 'not a dict'}")
        if isinstance(team_players, dict) and "statistics" in team_players:
            print(f"DEBUG: Player group {i} statistics: {len(team_players['statistics'])} stat groups")
        team_info = team_players.get("team", {})
        team_name = team_info.get("displayName", "Unknown Team")
        
        # Get position groups (batters, pitchers, etc.)
        statistics = team_players.get("statistics", [])
        team_player_data = {"team": team_name, "players": []}
        print(f"DEBUG: Team {team_name} has {len(statistics)} stat groups")
        
        for j, stat_group in enumerate(statistics):
            group_name = stat_group.get("name", "").lower()
            athletes = stat_group.get("athletes", [])
            print(f"DEBUG: Stat group {j}: '{group_name}', athletes: {len(athletes)}")
            
            # ESPN doesn't always have meaningful group names, so process all groups with athletes
            if athletes:  # Process any group that has athletes
                athletes = stat_group.get("athletes", [])
                for athlete_data in athletes:
                    athlete = athlete_data.get("athlete", {})
                    player_name = athlete.get("displayName", "Unknown Player")
                    position = athlete.get("position", {}).get("abbreviation", "")
                    
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
    
    print(f"DEBUG: Returning parsed_boxscore with {len(parsed_boxscore['teams'])} teams and {len(parsed_boxscore['players'])} player groups")
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
        
        if "officials" in value and isinstance(value["officials"], list):
            officials_count = len(value["officials"])
            if officials_count > 0:
                info_parts.append(f"Officials: {officials_count} assigned")
        
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
            return f"Statistical leaders available ({leader_count} categories) - Press Enter to view"
        elif isinstance(value, dict):
            if "header" in value:
                category_count = len([k for k in value.keys() if k != "header"])
                return f"Statistical leaders available ({category_count} categories) - Press Enter to view"
            else:
                category_count = len(value.keys())
                return f"Statistical leaders available ({category_count} categories) - Press Enter to view"
        else:
            return "Leaders data available"
    
    elif key == "standings":
        if isinstance(value, list):
            if not value:
                return "No standings available"
            team_count = len(value)
            return f"Standings available for {team_count} teams - Press Enter to view"
        elif isinstance(value, dict):
            if "entries" in value and isinstance(value["entries"], list):
                team_count = len(value["entries"])
                return f"Standings available for {team_count} teams - Press Enter to view"
            elif "header" in value:
                return "Current standings available - Press Enter to view"
            else:
                return "Standings data available - Press Enter to view"
        else:
            return "Standings available"
    
    elif key == "injuries" and isinstance(value, list):
        if not value:
            return "No injuries reported"
        injury_count = len(value)
        return f"Injury reports available ({injury_count} players) - Press Enter to view details"
    
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
    """Get current standings for a specific league using teams API"""
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
            wins, losses, win_pct = _get_team_record(team_id, league_key)
            
            standings.append({
                "team_name": team_name,
                "abbreviation": abbreviation,
                "wins": wins,
                "losses": losses,
                "win_percentage": win_pct,
                "games_back": "N/A",  # We'll calculate this after sorting by division
                "division": division,
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
    """Get individual team's win/loss record"""
    if not team_id:
        return 0, 0, "0.000"
        
    league_path = LEAGUES.get(league_key)
    if not league_path:
        return 0, 0, "0.000"
    
    try:
        # Get detailed team information
        team_url = f"{BASE_URL}/{league_path}/teams/{team_id}"
        resp = requests.get(team_url)
        
        if resp.status_code != 200:
            return 0, 0, "0.000"
        
        data = resp.json()
        team = data.get("team", {})
        record = team.get("record", {})
        items = record.get("items", [])
        
        # Look for overall record
        for item in items:
            if item.get("type") == "total":
                summary = item.get("summary", "0-0")
                try:
                    # Parse summary like "54-61"
                    wins, losses = map(int, summary.split("-"))
                    total_games = wins + losses
                    win_pct = f"{wins/total_games:.3f}" if total_games > 0 else "0.000"
                    return wins, losses, win_pct
                except (ValueError, IndexError):
                    pass
                break
        
        return 0, 0, "0.000"
        
    except Exception as e:
        print(f"Error getting team {team_id} record: {e}")
        return 0, 0, "0.000"

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
