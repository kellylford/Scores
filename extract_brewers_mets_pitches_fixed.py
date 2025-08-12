
import sys
sys.path.insert(0, '.')
from services.api_service import ApiService
import csv
import json
from datetime import datetime

def extract_pitch_data(game_details, game_id, game_date, teams):
    """Extract all pitch data from a single MLB game"""
    plays = game_details.get('plays', [])
    pitches = []
    current_batter = None
    current_pitcher = None
    current_inning = None
    current_inning_half = None
    current_at_bat_id = None
    balls = 0
    strikes = 0
    for play in plays:
        play_type = play.get('type', {}).get('type', '')
        # Track inning changes
        if play_type == 'start-inning':
            period = play.get('period', {})
            current_inning = period.get('number')
            current_inning_half = period.get('type')
        elif play_type == 'start-batterpitcher':
            participants = play.get('participants', [])
            for participant in participants:
                athlete = participant.get('athlete', {})
                position = participant.get('position', {}).get('displayName', '')
                if 'Pitcher' in position:
                    current_pitcher = athlete.get('displayName', '')
                else:
                    current_batter = athlete.get('displayName', '')
            balls = 0
            strikes = 0
            current_at_bat_id = play.get('atBatId')
        elif 'pitch' in play.get('text', '').lower() or play_type in [
            'strike-looking', 'strike-swinging', 'ball', 'foul', 
            'hit-by-pitch', 'in-play'
        ]:
            if play_type in ['strike-looking', 'strike-swinging', 'foul']:
                if strikes < 2:
                    strikes += 1
            elif play_type == 'ball':
                balls += 1
            elif play_type in ['hit-by-pitch', 'in-play']:
                pass
            pitch_coordinate = play.get('pitchCoordinate', {})
            x_coord = pitch_coordinate.get('x') if pitch_coordinate else None
            y_coord = pitch_coordinate.get('y') if pitch_coordinate else None
            pitch_velocity = play.get('pitchVelocity')
            if isinstance(pitch_velocity, dict):
                velocity = pitch_velocity.get('value')
            else:
                velocity = pitch_velocity
            pitch_type_info = play.get('pitchType', {})
            pitch_type = pitch_type_info.get('text') if pitch_type_info else None
            pitch_type_abbrev = pitch_type_info.get('abbreviation') if pitch_type_info else None
            bats_info = play.get('bats', {})
            batter_side = bats_info.get('abbreviation') if bats_info else None
            pitcher_info = None
            batter_info = None
            for participant in play.get('participants', []):
                if participant.get('type') == 'pitcher':
                    pitcher_info = participant.get('athlete', {})
                elif participant.get('type') == 'batter':
                    batter_info = participant.get('athlete', {})
            pitch_data = {
                'game_id': game_id,
                'game_date': game_date,
                'teams': teams,
                'inning': current_inning,
                'inning_half': current_inning_half,
                'at_bat_id': current_at_bat_id,
                'batter': current_batter,
                'batter_id': batter_info.get('id') if batter_info else None,
                'pitcher': current_pitcher,
                'pitcher_id': pitcher_info.get('id') if pitcher_info else None,
                'play_id': play.get('id'),
                'sequence_number': play.get('sequenceNumber'),
                'pitch_number': play.get('text', '').split('Pitch ')[-1].split(' :')[0] if 'Pitch ' in play.get('text', '') else '',
                'at_bat_pitch_number': play.get('atBatPitchNumber'),
                'bat_order': play.get('batOrder'),
                'play_type': play_type,
                'play_type_text': play.get('type', {}).get('text', ''),
                'play_description': play.get('text', ''),
                'balls_before': balls,
                'strikes_before': strikes,
                'coordinate_x': x_coord,
                'coordinate_y': y_coord,
                'velocity_mph': velocity,
                'pitch_type': pitch_type,
                'pitch_type_abbrev': pitch_type_abbrev,
                'batter_side': batter_side,
                'away_score': play.get('awayScore', 0),
                'home_score': play.get('homeScore', 0),
                'wallclock': play.get('wallclock', ''),
                'scoring_play': play.get('scoringPlay', False),
                'participants_count': len(play.get('participants', [])),
                'alternative_text': play.get('alternativeText', ''),
                'raw_play_data': json.dumps(play, separators=(',', ':'))
            }
            pitches.append(pitch_data)
            if play_type in ['hit-by-pitch', 'in-play'] or (play_type in ['strike-looking', 'strike-swinging'] and strikes >= 3):
                balls = 0
                strikes = 0
    return pitches

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_brewers_mets_pitches_fixed.py YYYY-MM-DD")
        sys.exit(1)
    date_str = sys.argv[1]
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        print("Invalid date format. Use YYYY-MM-DD.")
        sys.exit(1)
    api = ApiService()
    print(f"Fetching MLB games for {date_str}...")
    games = api.get_games('MLB', date_str)
    if not games:
        print(f"No MLB games found for {date_str}.")
        sys.exit(0)
    for game in games:
        game_id = game.get('id')
        teams = f"{game.get('awayTeam', {}).get('displayName', 'Away')} vs {game.get('homeTeam', {}).get('displayName', 'Home')}"
        print(f"Processing game {game_id}: {teams}")
        game_details = api.get_game_details('MLB', game_id)
        pitches = extract_pitch_data(game_details, game_id, date_str, teams)
        if pitches:
            csv_filename = f"mlb_pitches_{game_id}_{date_str}.csv"
            fieldnames = pitches[0].keys()
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(pitches)
            print(f"  Exported {len(pitches)} pitches to {csv_filename}")
        else:
            print(f"  No pitch data found for game {game_id}.")
