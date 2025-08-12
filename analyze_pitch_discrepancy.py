#!/usr/bin/env python3
"""
Analyze the specific pitch coordinates (144, 207) from Brewers vs Pirates game
to understand if there's an issue with the coordinate interpretation.
"""

import espn_api
import json

def analyze_pitch_coordinates():
    """Analyze the coordinates (144, 207) in context"""
    
    # Get the game data
    game_details = espn_api.get_game_details('MLB', '401696689')
    
    print("=== PITCH COORDINATE ANALYSIS ===")
    print("Game: Pittsburgh Pirates at Milwaukee Brewers")
    print("Analyzing coordinates (144, 207)")
    print()
    
    # Check both plays and atBats for pitch data
    all_pitches = []
    
    # Collect from plays
    if 'plays' in game_details:
        for play in game_details['plays']:
            if 'pitchData' in play:
                for pitch in play['pitchData']:
                    all_pitches.append({
                        'source': 'plays',
                        'play_text': play.get('text', ''),
                        'pitch': pitch
                    })
    
    # Collect from atBats
    if 'atBats' in game_details:
        for at_bat in game_details['atBats']:
            if 'pitchData' in at_bat:
                for pitch in at_bat['pitchData']:
                    all_pitches.append({
                        'source': 'atBats',
                        'play_text': at_bat.get('text', ''),
                        'pitch': pitch
                    })
    
    print(f"Total pitches found: {len(all_pitches)}")
    
    # Find the specific pitch with coordinates (144, 207)
    target_pitch = None
    for pitch_data in all_pitches:
        pitch = pitch_data['pitch']
        coords = pitch.get('coordinates', {})
        if coords.get('x') == 144 and coords.get('y') == 207:
            target_pitch = pitch_data
            break
    
    if target_pitch:
        print("\n=== FOUND TARGET PITCH ===")
        print(f"Source: {target_pitch['source']}")
        print(f"Play: {target_pitch['play_text']}")
        print(f"Pitch details:")
        print(json.dumps(target_pitch['pitch'], indent=2))
        
        # Analyze the coordinates
        analyze_coordinates(target_pitch['pitch'])
    else:
        print("\n❌ Could not find pitch with coordinates (144, 207)")
        
        # Show some sample coordinates for context
        print("\nSample coordinates found:")
        for i, pitch_data in enumerate(all_pitches[:10]):
            coords = pitch_data['pitch'].get('coordinates', {})
            x, y = coords.get('x'), coords.get('y')
            if x is not None and y is not None:
                print(f"  Pitch {i+1}: ({x}, {y})")

def analyze_coordinates(pitch):
    """Analyze what the coordinates mean"""
    coords = pitch.get('coordinates', {})
    x, y = coords.get('x'), coords.get('y')
    
    print(f"\n=== COORDINATE ANALYSIS ===")
    print(f"X: {x}, Y: {y}")
    
    # Based on previous analysis, typical ranges are:
    # X: 50-205 (left to right from catcher's perspective)
    # Y: 80-200 (top to bottom)
    # Strike zone typically: X: 100-155, Y: 80-200
    
    print(f"\nCoordinate interpretation:")
    
    # X-axis analysis (horizontal)
    if x < 50:
        x_desc = "Way inside (very far left)"
    elif x < 100:
        x_desc = "Inside (left side)"
    elif x <= 155:
        x_desc = "Strike zone width"
    elif x <= 205:
        x_desc = "Outside (right side)"
    else:
        x_desc = "Way outside (very far right)"
    
    print(f"X = {x}: {x_desc}")
    
    # Y-axis analysis (vertical)
    if y < 80:
        y_desc = "High (above strike zone)"
    elif y <= 200:
        y_desc = "Strike zone height"
    else:
        y_desc = "Low (below strike zone)"
    
    print(f"Y = {y}: {y_desc}")
    
    # Overall assessment
    in_strike_zone_x = 100 <= x <= 155
    in_strike_zone_y = 80 <= y <= 200
    
    print(f"\nStrike zone assessment:")
    print(f"In horizontal strike zone: {in_strike_zone_x}")
    print(f"In vertical strike zone: {in_strike_zone_y}")
    print(f"Overall in strike zone: {in_strike_zone_x and in_strike_zone_y}")
    
    # The user said this was called "Low Far Left" but coordinates show (144, 207)
    # Let's analyze this discrepancy
    print(f"\n=== USER REPORT VS COORDINATES ===")
    print(f"User reported: 'Low Far Left'")
    print(f"Coordinates show: X=144 (center/right of strike zone), Y=207 (low)")
    
    if x == 144:
        print(f"❓ DISCREPANCY: X=144 is in the center-right of strike zone, not 'far left'")
        print(f"   Expected 'far left' would be X < 100")
    
    if y == 207:
        print(f"✅ CONSISTENT: Y=207 is below strike zone (low), matches 'low' description")

if __name__ == "__main__":
    analyze_pitch_coordinates()
