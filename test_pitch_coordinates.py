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
        # Get game details with plays
        details = espn_api.get_game_details(game_id, ['plays'])
        
        if not details or 'plays' not in details:
            print("No plays data found")
            return
            
        plays_data = details['plays']
        print(f"Found {len(plays_data)} drives")
        
        pitch_count = 0
        
        # Examine first few drives
        for drive_idx, drive in enumerate(plays_data):
            if pitch_count >= 10:  # Limit to first 10 pitches
                break
                
            print(f"\n--- Drive {drive_idx + 1} ---")
            
            if 'plays' not in drive:
                continue
                
            for play_idx, play in enumerate(drive['plays']):
                if pitch_count >= 10:
                    break
                    
                play_text = play.get('text', '')
                
                # Look for pitch-related plays
                is_pitch = any(keyword in play_text.lower() for keyword in 
                             ['ball', 'strike', 'foul', 'looking', 'swinging'])
                
                if is_pitch:
                    pitch_count += 1
                    print(f"\nPitch #{pitch_count}: {play_text}")
                    
                    # Extract pitch details
                    velocity = play.get('pitchVelocity')
                    pitch_type = play.get('pitchType', {})
                    pitch_coord = play.get('pitchCoordinate', {})
                    
                    if velocity:
                        print(f"  Velocity: {velocity} mph")
                        
                    if isinstance(pitch_type, dict) and 'text' in pitch_type:
                        print(f"  Type: {pitch_type['text']}")
                        
                    if pitch_coord and isinstance(pitch_coord, dict):
                        espn_x = pitch_coord.get('x')
                        espn_y = pitch_coord.get('y')
                        
                        if espn_x is not None and espn_y is not None:
                            print(f"  Raw ESPN data: x={espn_x}, y={espn_y}")
                            print(f"  ESPN interpretation: x=vertical({espn_x}), y=horizontal({espn_y})")
                            print(f"  Our display format: ({espn_y}, {espn_x}) = (horizontal, vertical)")
                            
                            # Apply our location logic
                            from scores import get_pitch_location
                            location = get_pitch_location(espn_y, espn_x)  # horizontal, vertical
                            print(f"  Location: {location}")
                            
                            # Analyze the coordinate meaning
                            if espn_x < 150:
                                height_desc = "LOW"
                            elif espn_x > 200:
                                height_desc = "HIGH" 
                            else:
                                height_desc = "MIDDLE"
                                
                            if espn_y < 80:
                                horiz_desc = "INSIDE"
                            elif espn_y > 140:
                                horiz_desc = "OUTSIDE"
                            else:
                                horiz_desc = "STRIKE_ZONE"
                                
                            print(f"  Analysis: {height_desc} and {horiz_desc}")
                    else:
                        print("  No coordinate data")
                        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pitch_coordinates()
