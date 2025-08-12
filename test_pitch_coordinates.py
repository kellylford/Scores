#!/usr/bin/env python3
"""
Test script to examine pitch coordinates from the Brewers-Mets game
"""

import espn_api
import json

def test_pitch_coordinates():
    """Test pitch coordinate interpretation"""
    
    # The specific game ID you provided
    game_id = '401696676'
    
    print("Testing ESPN API pitch coordinates...")
    print(f"Game ID: {game_id}")
    print("=" * 50)
    
    try:
        # Get game details with plays using direct game ID
        details = espn_api.get_game_details(game_id, ['plays'])
        
        if not details:
            print("No details returned - trying alternative approach")
            
            # Try getting yesterday's games and finding this specific one
            from datetime import datetime, timedelta
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime('%Y%m%d')
            
            print(f"Checking games from {date_str}")
            games = espn_api.get_scores('mlb', date_str)
            print(f"Found {len(games)} games")
            
            # Look for our specific game
            target_game = None
            for game in games:
                if game['id'] == game_id:
                    target_game = game
                    print(f"Found target game: {game_id}")
                    break
                    
            if target_game:
                # Try getting details again
                details = espn_api.get_game_details(game_id, ['plays'])
            
        if details and 'plays' in details:
            plays_data = details['plays']
            print(f"SUCCESS: Found {len(plays_data)} drives")
            
            # Look at the first batter's pitches
            pitch_count = 0
            print("\\n=== FIRST BATTER ANALYSIS ===")
            
            for drive_idx, drive in enumerate(plays_data):
                if pitch_count >= 10:  # Focus on first 10 pitches
                    break
                    
                if 'plays' not in drive:
                    continue
                    
                # Check if this is the first batter (drive 1 usually)
                if drive_idx == 0:  # First drive
                    print(f"Drive {drive_idx + 1}:")
                    
                    for play_idx, play in enumerate(drive['plays']):
                        if pitch_count >= 10:
                            break
                            
                        play_text = play.get('text', '')
                        
                        # Look for pitch-related plays
                        is_pitch = any(keyword in play_text.lower() for keyword in 
                                     ['ball', 'strike', 'foul', 'looking', 'swinging', 'hit by pitch'])
                        
                        if is_pitch:
                            pitch_count += 1
                            print(f"\\n  Pitch {pitch_count}: {play_text}")
                            
                            # Extract pitch details
                            velocity = play.get('pitchVelocity')
                            pitch_type = play.get('pitchType', {})
                            pitch_coord = play.get('pitchCoordinate', {})
                            
                            if velocity:
                                print(f"    Velocity: {velocity} mph")
                                
                            if isinstance(pitch_type, dict) and 'text' in pitch_type:
                                print(f"    Type: {pitch_type['text']}")
                                
                            if pitch_coord and isinstance(pitch_coord, dict):
                                espn_x = pitch_coord.get('x')
                                espn_y = pitch_coord.get('y')
                                
                                if espn_x is not None and espn_y is not None:
                                    print(f"    Raw ESPN: x={espn_x}, y={espn_y}")
                                    
                                    # Test both interpretations
                                    from scores import get_pitch_location
                                    
                                    # Current interpretation (x=horizontal, y=vertical)
                                    location_current = get_pitch_location(espn_x, espn_y)
                                    print(f"    Current logic: ({espn_x}, {espn_y}) = {location_current}")
                                    
                                    # Check if this makes sense for the play type
                                    if 'hit by pitch' in play_text.lower():
                                        print(f"    *** HIT BY PITCH - Should be INSIDE, showing: {location_current}")
                                        if 'outside' in location_current.lower():
                                            print(f"    *** PROBLEM: Hit by pitch shows as outside!")
                            else:
                                print("    No coordinate data")
        else:
            print("No plays data available")
            if details:
                print("Available keys:", list(details.keys()) if isinstance(details, dict) else type(details))
                        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pitch_coordinates()
