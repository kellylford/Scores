#!/usr/bin/env python3
"""
Detailed analysis of pitch coordinate data to understand the relationship
between ESPN API coordinates and the official MLB strike zone.
"""

import json
import os

def analyze_pitch_data_structure():
    """Examine the structure of pitch data to understand what we're working with."""
    
    print("=== Detailed Pitch Data Structure Analysis ===")
    print()
    
    game_file = "api_exploration/game_details_401696636.json"
    if not os.path.exists(game_file):
        print(f"Game file not found: {game_file}")
        return
    
    with open(game_file, 'r') as f:
        data = json.load(f)
    
    # Find all plays with pitch data
    plays = data.get('plays', [])
    if not plays:
        # Check drives format
        drives = data.get('drives', [])
        all_plays = []
        for drive in drives:
            all_plays.extend(drive.get('plays', []))
        plays = all_plays
    
    print(f"Total plays found: {len(plays)}")
    
    # Let's look at several different examples
    pitch_examples = []
    for i, play in enumerate(plays):
        coord = play.get('pitchCoordinate') or play.get('coordinate')
        if coord and len(pitch_examples) < 10:
            pitch_examples.append((i, play))
    
    print(f"\n=== Sample Pitch Data Examples ===")
    for i, (play_idx, play) in enumerate(pitch_examples):
        print(f"\nExample {i+1} (Play #{play_idx}):")
        print(f"  Text: {play.get('text', 'N/A')}")
        print(f"  Type: {play.get('type', {}).get('text', 'N/A')}")
        print(f"  Summary Type: {play.get('summaryType', 'N/A')}")
        print(f"  Pitch Type: {play.get('pitchType', {}).get('text', 'N/A')}")
        print(f"  Velocity: {play.get('pitchVelocity', 'N/A')}")
        
        coord = play.get('pitchCoordinate') or play.get('coordinate')
        if coord:
            print(f"  Coordinates: X={coord.get('x')}, Y={coord.get('y')}")
        
        # Look for ball/strike information
        pitch_count = play.get('pitchCount', {})
        if pitch_count:
            print(f"  Count: {pitch_count.get('balls', '?')}-{pitch_count.get('strikes', '?')}")
        
        # Check for additional fields
        print(f"  All available fields: {list(play.keys())}")
    
    # Analyze the relationship between called strikes and balls
    print(f"\n=== Strike vs Ball Analysis ===")
    
    called_strikes = []
    called_balls = []
    
    for play in plays:
        coord = play.get('pitchCoordinate') or play.get('coordinate')
        if not coord:
            continue
            
        summary = play.get('summaryType', '').lower()
        type_text = play.get('type', {}).get('text', '').lower()
        text = play.get('text', '').lower()
        
        # Try to identify called strikes (looking strikes)
        if ('strike' in summary and 'looking' in type_text) or ('strike looking' in text):
            called_strikes.append({
                'x': coord.get('x'),
                'y': coord.get('y'),
                'text': play.get('text'),
                'summary': summary,
                'type': type_text
            })
        
        # Try to identify called balls
        elif 'ball' in summary and 'ball' in type_text:
            called_balls.append({
                'x': coord.get('x'),
                'y': coord.get('y'),
                'text': play.get('text'),
                'summary': summary,
                'type': type_text
            })
    
    print(f"Found {len(called_strikes)} called strikes with coordinates")
    print(f"Found {len(called_balls)} called balls with coordinates")
    
    if called_strikes:
        print(f"\n=== Called Strikes Sample ===")
        for i, strike in enumerate(called_strikes[:5]):
            print(f"  Strike {i+1}: ({strike['x']}, {strike['y']}) - {strike['text']}")
    
    if called_balls:
        print(f"\n=== Called Balls Sample ===")
        for i, ball in enumerate(called_balls[:5]):
            print(f"  Ball {i+1}: ({ball['x']}, {ball['y']}) - {ball['text']}")
    
    # Calculate coordinate ranges for strikes vs balls
    if called_strikes and called_balls:
        print(f"\n=== Coordinate Range Analysis ===")
        
        strike_x = [s['x'] for s in called_strikes if s['x'] is not None]
        strike_y = [s['y'] for s in called_strikes if s['y'] is not None]
        ball_x = [b['x'] for b in called_balls if b['x'] is not None]
        ball_y = [b['y'] for b in called_balls if b['y'] is not None]
        
        if strike_x:
            print(f"Called Strikes - X range: {min(strike_x)} to {max(strike_x)}")
            print(f"Called Strikes - Y range: {min(strike_y)} to {max(strike_y)}")
        
        if ball_x:
            print(f"Called Balls - X range: {min(ball_x)} to {max(ball_x)}")
            print(f"Called Balls - Y range: {min(ball_y)} to {max(ball_y)}")
    
    print(f"\n=== ASSESSMENT ===")
    if not called_strikes and not called_balls:
        print("⚠️  Unable to find clear called strikes vs balls in the data")
        print("   This suggests the data format may be different than expected")
        print("   or the coordinate system may not directly correspond to strike zone")
    else:
        print("✅ Found called strikes and balls - coordinate analysis possible")
    
    return called_strikes, called_balls

if __name__ == "__main__":
    analyze_pitch_data_structure()
