import sys
sys.path.insert(0, '.')
from services.api_service import ApiService
import csv
import json

def extract_pitch_data():
    """Extract all pitch data from Brewers vs Mets game on 8/10/2025"""
    
    api = ApiService()
    game_details = api.get_game_details('MLB', '401696676')
    
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
            
        # Track batter/pitcher changes
        elif play_type == 'start-batterpitcher':
            participants = play.get('participants', [])
            for participant in participants:
                athlete = participant.get('athlete', {})
                position = participant.get('position', {}).get('displayName', '')
                if 'Pitcher' in position:
                    current_pitcher = athlete.get('displayName', '')
                else:
                    current_batter = athlete.get('displayName', '')
            
            # Reset count for new batter
            balls = 0
            strikes = 0
            current_at_bat_id = play.get('atBatId')
            
        # Extract pitch data
        elif 'pitch' in play.get('text', '').lower() or play_type in [
            'strike-looking', 'strike-swinging', 'ball', 'foul', 
            'hit-by-pitch', 'in-play'
        ]:
            
            # Update count based on play type
            if play_type in ['strike-looking', 'strike-swinging', 'foul']:
                if strikes < 2:  # Foul with 2 strikes doesn't increment
                    strikes += 1
            elif play_type == 'ball':
                balls += 1
            elif play_type in ['hit-by-pitch', 'in-play']:
                # These end the at-bat, reset count after recording
                pass
                
            # Extract coordinate data
            pitch_coordinate = play.get('pitchCoordinate', {})
            x_coord = pitch_coordinate.get('x') if pitch_coordinate else None
            y_coord = pitch_coordinate.get('y') if pitch_coordinate else None
            
            # Extract velocity and pitch type if available
            pitch_velocity = play.get('pitchVelocity')
            if isinstance(pitch_velocity, dict):
                velocity = pitch_velocity.get('value')
            else:
                velocity = pitch_velocity  # If it's already a number
            pitch_type_info = play.get('pitchType', {})
            pitch_type = pitch_type_info.get('text') if pitch_type_info else None
            pitch_type_abbrev = pitch_type_info.get('abbreviation') if pitch_type_info else None
            
            # Extract batter handedness
            bats_info = play.get('bats', {})
            batter_side = bats_info.get('abbreviation') if bats_info else None
            
            # Extract pitcher information from participants
            pitcher_info = None
            batter_info = None
            for participant in play.get('participants', []):
                if participant.get('type') == 'pitcher':
                    pitcher_info = participant.get('athlete', {})
                elif participant.get('type') == 'batter':
                    batter_info = participant.get('athlete', {})
            
            pitch_data = {
                'game_id': '401696676',
                'game_date': '2025-08-10',
                'teams': 'Milwaukee Brewers vs New York Mets',
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
            
            # Reset count if at-bat ended
            if play_type in ['hit-by-pitch', 'in-play'] or (play_type in ['strike-looking', 'strike-swinging'] and strikes >= 3):
                balls = 0
                strikes = 0
    
    return pitches

if __name__ == "__main__":
    print("Extracting pitch data from Brewers vs Mets game (8/10/2025)...")
    
    pitches = extract_pitch_data()
    
    # Write to CSV
    csv_filename = 'brewers_mets_8_10_2025_pitches.csv'
    
    if pitches:
        fieldnames = pitches[0].keys()
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(pitches)
        
        print(f"Successfully exported {len(pitches)} pitches to {csv_filename}")
        
        # Show summary
        print(f"\nSummary:")
        print(f"Total pitches: {len(pitches)}")
        
        # Count by inning
        innings = {}
        for pitch in pitches:
            inning_key = f"{pitch['inning_half']} {pitch['inning']}"
            innings[inning_key] = innings.get(inning_key, 0) + 1
        
        print(f"Pitches by inning:")
        for inning, count in sorted(innings.items()):
            print(f"  {inning}: {count} pitches")
            
        # Count with coordinates
        with_coords = sum(1 for p in pitches if p['coordinate_x'] is not None)
        print(f"Pitches with coordinate data: {with_coords}")
        
        # Count by pitch type
        pitch_types = {}
        for pitch in pitches:
            pt = pitch['pitch_type'] or 'Unknown'
            pitch_types[pt] = pitch_types.get(pt, 0) + 1
        
        print(f"Pitch types:")
        for ptype, count in sorted(pitch_types.items()):
            print(f"  {ptype}: {count}")
            
        # Sample of coordinate data
        coords_sample = [(p['coordinate_x'], p['coordinate_y']) for p in pitches[:10] if p['coordinate_x'] is not None]
        if coords_sample:
            print(f"Sample coordinates (first 10): {coords_sample}")
        
    else:
        print("No pitch data found!")
