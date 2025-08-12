#!/usr/bin/env python3
"""
Search for the specific pitch coordinates (144, 207) across recent games
"""

import espn_api
from datetime import datetime, timedelta
import json

def search_for_pitch():
    """Search for the pitch with coordinates (144, 207)"""
    
    # Check last few days for MLB games
    for days_back in range(5):
        date = datetime.now() - timedelta(days=days_back)
        date_str = date.strftime('%Y%m%d')
        
        print(f"Checking MLB games on {date_str}...")
        
        try:
            scores = espn_api.get_scores('MLB', date)
            
            for game in scores:
                if 'Brewers' in game['name'] and 'Pirates' in game['name']:
                    game_id = game['id']
                    print(f"Found Brewers vs Pirates: {game['name']} (ID: {game_id})")
                    
                    # Get game details
                    game_details = espn_api.get_game_details('MLB', game_id)
                    
                    # Search through all pitch data
                    pitches_found = 0
                    target_found = False
                    
                    # Check plays
                    if 'plays' in game_details:
                        for play in game_details['plays']:
                            if 'pitchData' in play:
                                for i, pitch in enumerate(play['pitchData']):
                                    pitches_found += 1
                                    coords = pitch.get('coordinates', {})
                                    x, y = coords.get('x'), coords.get('y')
                                    
                                    if x == 144 and y == 207:
                                        print(f"\n🎯 FOUND TARGET PITCH!")
                                        print(f"Play: {play.get('text', '')}")
                                        print(f"Pitch #{i+1} in this at-bat")
                                        print(f"Pitch data:")
                                        print(json.dumps(pitch, indent=2))
                                        
                                        # Also check what our audio system would say
                                        analyze_audio_description(x, y, pitch)
                                        target_found = True
                                        break
                                
                                if target_found:
                                    break
                        
                        if target_found:
                            break
                    
                    # Check atBats if not found in plays
                    if not target_found and 'atBats' in game_details:
                        for at_bat in game_details['atBats']:
                            if 'pitchData' in at_bat:
                                for i, pitch in enumerate(at_bat['pitchData']):
                                    pitches_found += 1
                                    coords = pitch.get('coordinates', {})
                                    x, y = coords.get('x'), coords.get('y')
                                    
                                    if x == 144 and y == 207:
                                        print(f"\n🎯 FOUND TARGET PITCH!")
                                        print(f"At-bat: {at_bat.get('text', '')}")
                                        print(f"Pitch #{i+1} in this at-bat")
                                        print(f"Pitch data:")
                                        print(json.dumps(pitch, indent=2))
                                        
                                        analyze_audio_description(x, y, pitch)
                                        target_found = True
                                        break
                                
                                if target_found:
                                    break
                    
                    print(f"Total pitches found in game: {pitches_found}")
                    
                    if target_found:
                        return
                    else:
                        print("❌ Target pitch (144, 207) not found in this game")
                        
                        # Show some sample coordinates for reference
                        print("Sample coordinates from this game:")
                        sample_count = 0
                        if 'plays' in game_details:
                            for play in game_details['plays']:
                                if 'pitchData' in play and sample_count < 5:
                                    for pitch in play['pitchData']:
                                        coords = pitch.get('coordinates', {})
                                        x, y = coords.get('x'), coords.get('y')
                                        if x is not None and y is not None:
                                            print(f"  ({x}, {y})")
                                            sample_count += 1
                                            if sample_count >= 5:
                                                break
        
        except Exception as e:
            print(f"Error checking {date_str}: {e}")
    
    print("\n❌ Could not find pitch with coordinates (144, 207) in recent games")

def analyze_audio_description(x, y, pitch):
    """Analyze what our audio system would describe for these coordinates"""
    print(f"\n=== COORDINATE ANALYSIS ===")
    print(f"Coordinates: ({x}, {y})")
    
    # Based on our audio system's coordinate interpretation
    # X: horizontal position (left/right from catcher's view)
    # Y: vertical position (high/low)
    
    # Horizontal analysis
    if x < 50:
        horizontal = "Way Inside (Far Left)"
    elif x < 100:
        horizontal = "Inside (Left)"
    elif x <= 155:
        horizontal = "Strike Zone (Center)"
        if x < 120:
            horizontal += " - Left Side"
        elif x > 135:
            horizontal += " - Right Side"
        else:
            horizontal += " - Middle"
    elif x <= 205:
        horizontal = "Outside (Right)"
    else:
        horizontal = "Way Outside (Far Right)"
    
    # Vertical analysis
    if y < 80:
        vertical = "High"
    elif y <= 200:
        vertical = "Strike Zone"
        if y < 140:
            vertical += " - Upper"
        elif y > 160:
            vertical += " - Lower"
        else:
            vertical += " - Middle"
    else:
        vertical = "Low"
    
    print(f"Horizontal (X={x}): {horizontal}")
    print(f"Vertical (Y={y}): {vertical}")
    
    # Check against user's description
    user_description = "Low Far Left"
    print(f"\n=== COMPARISON ===")
    print(f"User reported: '{user_description}'")
    print(f"Coordinates suggest: '{vertical} {horizontal}'")
    
    if x == 144:
        print(f"🤔 POTENTIAL ISSUE: X=144 suggests center of strike zone, not 'far left'")
        print(f"   'Far left' would typically be X < 100")
    
    if y == 207:
        print(f"✅ CONSISTENT: Y=207 suggests 'low' (below strike zone)")
    
    # Pitch details
    pitch_type = pitch.get('pitchType', {}).get('displayName', 'Unknown')
    velocity = pitch.get('velocity', 'Unknown')
    result = pitch.get('result', {}).get('displayName', 'Unknown')
    
    print(f"\nPitch details:")
    print(f"Type: {pitch_type}")
    print(f"Velocity: {velocity}")
    print(f"Result: {result}")

if __name__ == "__main__":
    search_for_pitch()
