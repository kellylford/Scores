import sys
import argparse
sys.path.insert(0, '.')
from services.api_service import ApiService
import csv
import json
from datetime import datetime

def extract_all_game_details(date_str):
    """Extract comprehensive game details for all MLB games on the given date (YYYY-MM-DD)"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")
        return []
    api = ApiService()
    games = api.get_scores('MLB', date_obj)
    all_game_details = []
    missing_fields_log = []
    print(f"Found {len(games)} games on {date_str}")
    for i, game in enumerate(games):
        print(f"Processing game {i+1}/{len(games)}: {game.get('name', 'Unknown')}")
        game_id = game.get('id')
        if not game_id:
            continue
        try:
            detailed_game = api.get_game_details('MLB', game_id)
        except Exception as e:
            print(f"Error getting details for game {game_id}: {e}")
            continue
        teams = game.get('teams', [])
        team1 = teams[0] if len(teams) > 0 else {}
        team2 = teams[1] if len(teams) > 1 else {}
        game_status = game.get('status', '')
        start_time = game.get('start_time', '')
        header = detailed_game.get('header', {})
        game_info = detailed_game.get('gameInfo', {})
        venue = game_info.get('venue', {}) or detailed_game.get('venue', {})
        # Weather fallback: check game_info['weather'], detailed_game['weather'], and scoreboard['weather']
        weather = game_info.get('weather', {}) or detailed_game.get('weather', {}) or game.get('weather', {})
        # Officials fallback: check game_info['officials'], detailed_game['officials']
        officials = game_info.get('officials', []) or detailed_game.get('officials', [])
        boxscore = detailed_game.get('boxscore', {})
        teams_boxscore = boxscore.get('teams', [])
        leaders = detailed_game.get('leaders', {})
        broadcasts = detailed_game.get('broadcasts', [])
        news = detailed_game.get('news', {}).get('articles', [])
        odds = detailed_game.get('odds', [])
        injuries = detailed_game.get('injuries', [])
        plays = detailed_game.get('plays', [])
        total_plays = len(plays)
        pitch_plays = [p for p in plays if 'pitch' in p.get('text', '').lower() or 
                      p.get('type', {}).get('type') in ['strike-looking', 'strike-swinging', 'ball', 'foul']]
        total_pitches = len(pitch_plays)
        scoring_plays = [p for p in plays if p.get('scoringPlay', False)]
        win_probability = detailed_game.get('winProbability', [])
        missing_fields = []
        def check_missing(field, value):
            if value in ('', None, [], {}):
                missing_fields.append(field)
        game_record = {
            'game_id': game_id,
            'game_date': date_str,
            'game_name': game.get('name', ''),
            'game_status': game_status,
            'start_time': start_time,
            'away_team_name': team1.get('name', ''),
            'away_team_abbreviation': team1.get('abbreviation', ''),
            'away_team_score': team1.get('score', ''),
            'away_team_record': '',
            'home_team_name': team2.get('name', ''),
            'home_team_abbreviation': team2.get('abbreviation', ''),
            'home_team_score': team2.get('score', ''),
            'home_team_record': '',
            'venue_name': venue.get('fullName', venue.get('name', '')),
            'venue_city': venue.get('address', {}).get('city', ''),
            'venue_state': venue.get('address', {}).get('state', ''),
            'venue_capacity': venue.get('capacity', ''),
            'venue_grass': venue.get('grass', ''),
            'venue_roof_type': venue.get('roofType', ''),
            'temperature': weather.get('temperature', weather.get('temp', '')),
            'condition_description': weather.get('conditionDescription', weather.get('description', '')),
            'wind_direction': weather.get('wind', {}).get('direction', {}).get('description', ''),
            'wind_speed': weather.get('wind', {}).get('speed', ''),
            'humidity': weather.get('humidity', ''),
            'total_plays': total_plays,
            'total_pitches': total_pitches,
            'scoring_plays_count': len(scoring_plays),
            'innings_completed': max([p.get('period', {}).get('number', 0) for p in plays] + [0]),
            'officials_count': len(officials),
            'home_plate_umpire': '',
            'broadcast_networks': ', '.join([b.get('network', '') for b in broadcasts]),
            'broadcast_count': len(broadcasts),
            'news_articles_count': len(news),
            'latest_headline': news[0].get('headline', '') if news else '',
            'odds_available': len(odds) > 0,
            'odds_count': len(odds),
            'injuries_count': len(injuries),
            'win_probability_available': len(win_probability) > 0,
            'final_win_probability': '',
            'game_duration': '',
            'first_pitch_time': '',
            'last_play_time': '',
            'attendance': game_info.get('attendance', ''),
            'game_number': header.get('gameNumber', ''),
            'series_summary': header.get('series', {}).get('summary', ''),
            'double_header': header.get('doubleHeader', False),
            'raw_header_data': json.dumps(header, separators=(',', ':')),
            'raw_game_info': json.dumps(game_info, separators=(',', ':')),
            'raw_venue_data': json.dumps(venue, separators=(',', ':')),
            'raw_weather_data': json.dumps(weather, separators=(',', ':')),
        }
        if teams_boxscore:
            for team_box in teams_boxscore:
                is_home = team_box.get('homeAway') == 'home'
                team_stats = team_box.get('statistics', [])
                hits = next((s.get('displayValue', '') for s in team_stats if s.get('name') == 'hits'), '')
                errors = next((s.get('displayValue', '') for s in team_stats if s.get('name') == 'errors'), '')
                runs = team_box.get('score', '')
                prefix = 'home' if is_home else 'away'
                game_record[f'{prefix}_team_hits'] = hits
                game_record[f'{prefix}_team_errors'] = errors
                game_record[f'{prefix}_team_runs'] = runs
        # Umpire fallback: try officials, then header['officials']
        home_plate_umpire = ''
        if officials:
            for official in officials:
                position = official.get('position', {}).get('name', '')
                if 'Home Plate' in position:
                    home_plate_umpire = official.get('displayName', '')
        if not home_plate_umpire and 'officials' in header:
            for official in header['officials']:
                position = official.get('position', {}).get('name', '')
                if 'Home Plate' in position:
                    home_plate_umpire = official.get('displayName', '')
        game_record['home_plate_umpire'] = home_plate_umpire
        if plays:
            first_play = min(plays, key=lambda x: x.get('wallclock', ''))
            last_play = max(plays, key=lambda x: x.get('wallclock', ''))
            game_record['first_pitch_time'] = first_play.get('wallclock', '')
            game_record['last_play_time'] = last_play.get('wallclock', '')
        if win_probability:
            final_wp = win_probability[-1] if win_probability else {}
            if isinstance(final_wp, dict):
                game_record['final_win_probability'] = final_wp.get('homeWinPercentage', '')
        # Check for missing fields
        for k, v in game_record.items():
            check_missing(k, v)
        if missing_fields:
            missing_fields_log.append({
                'game_id': game_id,
                'missing_fields': missing_fields,
                'game_name': game.get('name', ''),
                'raw_game': game,
                'raw_details': detailed_game
            })
        all_game_details.append(game_record)
    # Save missing fields log for analysis
    if missing_fields_log:
        with open(f"mlb_missing_fields_{date_str.replace('-', '_')}.json", "w", encoding="utf-8") as f:
            json.dump(missing_fields_log, f, ensure_ascii=False, indent=2)
    return all_game_details

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract comprehensive MLB game details for a given date.")
    parser.add_argument('--date', type=str, required=True, help='Date in YYYY-MM-DD format')
    args = parser.parse_args()
    date_str = args.date
    print(f"Extracting comprehensive game details for all MLB games on {date_str}...")
    games_data = extract_all_game_details(date_str)
    csv_filename = f"mlb_games_{date_str.replace('-', '_')}_comprehensive.csv"
    if games_data:
        fieldnames = games_data[0].keys()
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(games_data)
        print(f"Successfully exported {len(games_data)} games to {csv_filename}")
        print(f"\nSummary:")
        print(f"Total games: {len(games_data)}")
        statuses = {}
        for game in games_data:
            status = game['game_status']
            statuses[status] = statuses.get(status, 0) + 1
        print(f"Game statuses:")
        for status, count in statuses.items():
            print(f"  {status}: {count} games")
        venues = set(game['venue_name'] for game in games_data if game['venue_name'])
        print(f"Unique venues: {len(venues)}")
        total_pitches = sum(int(game['total_pitches']) for game in games_data if game['total_pitches'])
        print(f"Total pitches across all games: {total_pitches}")
        weather_conditions = set(game['condition_description'] for game in games_data if game['condition_description'])
        print(f"Weather conditions: {', '.join(weather_conditions)}")
        print(f"\nSample game data (first game):")
        first_game = games_data[0]
        print(f"  {first_game['away_team_name']} @ {first_game['home_team_name']}")
        print(f"  Score: {first_game['away_team_score']} - {first_game['home_team_score']}")
        print(f"  Venue: {first_game['venue_name']}")
        print(f"  Pitches: {first_game['total_pitches']}")
        print(f"  Weather: {first_game['condition_description']}")
    else:
        print("No game data found!")