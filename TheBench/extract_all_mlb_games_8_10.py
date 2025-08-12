import sys
sys.path.insert(0, '.')
from services.api_service import ApiService
import csv
import json
from datetime import datetime

def extract_all_game_details():
    """Extract comprehensive game details for all MLB games on 8/10/2025"""
    
    api = ApiService()
    date_obj = datetime(2025, 8, 11)
    games = api.get_scores('MLB', date_obj)
    
    all_game_details = []
    
    print(f"Found {len(games)} games on 8/10/2025")
    
    for i, game in enumerate(games):
        print(f"Processing game {i+1}/{len(games)}: {game.get('name', 'Unknown')}")
        
        game_id = game.get('id')
        if not game_id:
            continue
            
        # Get detailed game information
        try:
            detailed_game = api.get_game_details('MLB', game_id)
        except Exception as e:
            print(f"Error getting details for game {game_id}: {e}")
            continue
        
        # Extract teams information
        teams = game.get('teams', [])
        team1 = teams[0] if len(teams) > 0 else {}
        team2 = teams[1] if len(teams) > 1 else {}
        
        # Extract basic game info from scoreboard
        game_status = game.get('status', '')
        start_time = game.get('start_time', '')
        
        # Extract detailed information from game details
        header = detailed_game.get('header', {})
        game_info = detailed_game.get('gameInfo', {})
        venue = game_info.get('venue', {})
        weather = game_info.get('weather', {})
        officials = game_info.get('officials', [])
        
        # Extract boxscore summary
        boxscore = detailed_game.get('boxscore', {})
        teams_boxscore = boxscore.get('teams', [])
        
        # Extract leaders/statistics
        leaders = detailed_game.get('leaders', {})
        
        # Extract broadcasts
        broadcasts = detailed_game.get('broadcasts', [])
        
        # Extract news
        news = detailed_game.get('news', {}).get('articles', [])
        
        # Extract odds if available
        odds = detailed_game.get('odds', [])
        
        # Extract injuries
        injuries = detailed_game.get('injuries', [])
        
        # Extract plays summary
        plays = detailed_game.get('plays', [])
        
        # Calculate game statistics
        total_plays = len(plays)
        pitch_plays = [p for p in plays if 'pitch' in p.get('text', '').lower() or 
                      p.get('type', {}).get('type') in ['strike-looking', 'strike-swinging', 'ball', 'foul']]
        total_pitches = len(pitch_plays)
        
        # Extract scoring plays
        scoring_plays = [p for p in plays if p.get('scoringPlay', False)]
        
        # Extract win probability if available
        win_probability = detailed_game.get('winProbability', [])
        
        # Build comprehensive game record
        game_record = {
            # Basic Game Information
            'game_id': game_id,
            'game_date': '2025-08-10',
            'game_name': game.get('name', ''),
            'game_status': game_status,
            'start_time': start_time,
            
            # Team Information
            'away_team_name': team1.get('name', ''),
            'away_team_abbreviation': team1.get('abbreviation', ''),
            'away_team_score': team1.get('score', ''),
            'away_team_record': '',  # Will extract from detailed data
            
            'home_team_name': team2.get('name', ''),
            'home_team_abbreviation': team2.get('abbreviation', ''),
            'home_team_score': team2.get('score', ''),
            'home_team_record': '',  # Will extract from detailed data
            
            # Venue Information
            'venue_name': venue.get('fullName', ''),
            'venue_city': venue.get('address', {}).get('city', ''),
            'venue_state': venue.get('address', {}).get('state', ''),
            'venue_capacity': venue.get('capacity', ''),
            'venue_grass': venue.get('grass', ''),
            'venue_roof_type': venue.get('roofType', ''),
            
            # Weather Information
            'temperature': weather.get('temperature', ''),
            'condition_description': weather.get('conditionDescription', ''),
            'wind_direction': weather.get('wind', {}).get('direction', {}).get('description', ''),
            'wind_speed': weather.get('wind', {}).get('speed', ''),
            'humidity': weather.get('humidity', ''),
            
            # Game Statistics
            'total_plays': total_plays,
            'total_pitches': total_pitches,
            'scoring_plays_count': len(scoring_plays),
            'innings_completed': max([p.get('period', {}).get('number', 0) for p in plays] + [0]),
            
            # Officials
            'officials_count': len(officials),
            'home_plate_umpire': '',
            
            # Broadcasts
            'broadcast_networks': ', '.join([b.get('network', '') for b in broadcasts]),
            'broadcast_count': len(broadcasts),
            
            # News
            'news_articles_count': len(news),
            'latest_headline': news[0].get('headline', '') if news else '',
            
            # Odds
            'odds_available': len(odds) > 0,
            'odds_count': len(odds),
            
            # Injuries
            'injuries_count': len(injuries),
            
            # Win Probability
            'win_probability_available': len(win_probability) > 0,
            'final_win_probability': '',
            
            # Game Duration/Timing
            'game_duration': '',
            'first_pitch_time': '',
            'last_play_time': '',
            
            # Additional Metadata
            'attendance': game_info.get('attendance', ''),
            'game_number': header.get('gameNumber', ''),
            'series_summary': header.get('series', {}).get('summary', ''),
            'double_header': header.get('doubleHeader', False),
            
            # Raw data for deep analysis
            'raw_header_data': json.dumps(header, separators=(',', ':')),
            'raw_game_info': json.dumps(game_info, separators=(',', ':')),
            'raw_venue_data': json.dumps(venue, separators=(',', ':')),
            'raw_weather_data': json.dumps(weather, separators=(',', ':')),
        }
        
        # Extract more detailed team information if available
        if teams_boxscore:
            for team_box in teams_boxscore:
                is_home = team_box.get('homeAway') == 'home'
                team_stats = team_box.get('statistics', [])
                
                # Extract key statistics
                hits = next((s.get('displayValue', '') for s in team_stats if s.get('name') == 'hits'), '')
                errors = next((s.get('displayValue', '') for s in team_stats if s.get('name') == 'errors'), '')
                runs = team_box.get('score', '')
                
                prefix = 'home' if is_home else 'away'
                game_record[f'{prefix}_team_hits'] = hits
                game_record[f'{prefix}_team_errors'] = errors
                game_record[f'{prefix}_team_runs'] = runs
        
        # Extract officials details
        if officials:
            for official in officials:
                position = official.get('position', {}).get('name', '')
                if 'Home Plate' in position:
                    game_record['home_plate_umpire'] = official.get('displayName', '')
        
        # Extract timing information
        if plays:
            first_play = min(plays, key=lambda x: x.get('wallclock', ''))
            last_play = max(plays, key=lambda x: x.get('wallclock', ''))
            game_record['first_pitch_time'] = first_play.get('wallclock', '')
            game_record['last_play_time'] = last_play.get('wallclock', '')
        
        # Extract win probability
        if win_probability:
            final_wp = win_probability[-1] if win_probability else {}
            if isinstance(final_wp, dict):
                game_record['final_win_probability'] = final_wp.get('homeWinPercentage', '')
        
        all_game_details.append(game_record)
    
    return all_game_details

if __name__ == "__main__":
    print("Extracting comprehensive game details for all MLB games on 8/10/2025...")
    
    games_data = extract_all_game_details()
    
    # Write to CSV
    csv_filename = 'mlb_games_8_10_2025_comprehensive.csv'
    
    if games_data:
        fieldnames = games_data[0].keys()
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(games_data)
        
        print(f"Successfully exported {len(games_data)} games to {csv_filename}")
        
        # Show summary
        print(f"\nSummary:")
        print(f"Total games: {len(games_data)}")
        
        # Game status summary
        statuses = {}
        for game in games_data:
            status = game['game_status']
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"Game statuses:")
        for status, count in statuses.items():
            print(f"  {status}: {count} games")
        
        # Venue summary
        venues = set(game['venue_name'] for game in games_data if game['venue_name'])
        print(f"Unique venues: {len(venues)}")
        
        # Pitch count summary
        total_pitches = sum(int(game['total_pitches']) for game in games_data if game['total_pitches'])
        print(f"Total pitches across all games: {total_pitches}")
        
        # Weather conditions
        weather_conditions = set(game['condition_description'] for game in games_data if game['condition_description'])
        print(f"Weather conditions: {', '.join(weather_conditions)}")
        
        # Sample of data
        print(f"\nSample game data (first game):")
        first_game = games_data[0]
        print(f"  {first_game['away_team_name']} @ {first_game['home_team_name']}")
        print(f"  Score: {first_game['away_team_score']} - {first_game['home_team_score']}")
        print(f"  Venue: {first_game['venue_name']}")
        print(f"  Pitches: {first_game['total_pitches']}")
        print(f"  Weather: {first_game['condition_description']}")
        
    else:
        print("No game data found!")
