#!/usr/bin/env python3
"""
Cross-validation script to test our strike zone assumptions across multiple games.
This will help us verify if our coordinate mapping is consistent across different games.
"""

import json
import os
from collections import defaultdict

def analyze_game_coordinates(filename):
    """Analyze pitch coordinates for a single game."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Try both possible data structures
        plays = data.get('plays', [])
        if not plays:
            # Check if it's in drives format
            drives = data.get('drives', [])
            all_plays = []
            for drive in drives:
                all_plays.extend(drive.get('plays', []))
            plays = all_plays
        
        pitch_data = []
        for play in plays:
            # Check for pitch coordinate data
            coord = play.get('pitchCoordinate') or play.get('coordinate')
            if coord and play.get('pitchVelocity'):
                pitch_data.append({
                    'text': play.get('text', ''),
                    'pitch_type': play.get('pitchType', {}).get('text', 'Unknown'),
                    'velocity': play.get('pitchVelocity'),
                    'x': coord.get('x'),
                    'y': coord.get('y'),
                    'result': play.get('type', {}).get('text', 'Unknown'),
                    'summary': play.get('summaryType', ''),
                })
        
        return pitch_data
    except Exception as e:
        print(f"Error analyzing {filename}: {e}")
        return []

def get_pitch_location_test(x, y):
    """Our current strike zone mapping function for testing."""
    if x is None or y is None:
        return "Unknown"
    
    if 80 <= x <= 140:  # Strike zone width
        if y > 200:
            return "High Strike Zone"
        elif y < 150:
            return "Low Strike Zone"
        else:
            return "Strike Zone Center"
    elif x < 80:
        if x < 50:
            return "Way Inside"
        else:
            return "Inside"
    else:  # x > 140
        if x > 170:
            return "Way Outside" 
        else:
            return "Outside"

def validate_strike_zone_assumptions():
    """Validate our strike zone mapping across multiple games."""
    
    print("=== Cross-Game Strike Zone Validation ===")
    print()
    
    game_files = [
        "api_exploration/game_details_401696636.json",
        "api_exploration/game_details_401696637.json", 
        "api_exploration/game_details_401696639.json",
        "api_exploration/game_details_401696640.json",
        "api_exploration/game_details_401696642.json"
    ]
    
    all_pitch_data = []
    games_analyzed = 0
    
    for game_file in game_files:
        if os.path.exists(game_file):
            print(f"Analyzing {game_file}...")
            pitch_data = analyze_game_coordinates(game_file)
            if pitch_data:
                all_pitch_data.extend(pitch_data)
                games_analyzed += 1
                print(f"  Found {len(pitch_data)} pitches with coordinates")
            else:
                print(f"  No pitch coordinate data found")
        else:
            print(f"  File not found: {game_file}")
    
    if not all_pitch_data:
        print("No pitch coordinate data found across any games!")
        return
    
    print(f"\n=== CROSS-GAME ANALYSIS ===")
    print(f"Total Games Analyzed: {games_analyzed}")
    print(f"Total Pitches with Coordinates: {len(all_pitch_data)}")
    
    # Coordinate range analysis
    x_values = [p['x'] for p in all_pitch_data if p['x'] is not None]
    y_values = [p['y'] for p in all_pitch_data if p['y'] is not None]
    
    print(f"\nCoordinate Ranges Across All Games:")
    print(f"X: {min(x_values)} to {max(x_values)} (range: {max(x_values)-min(x_values)})")
    print(f"Y: {min(y_values)} to {max(y_values)} (range: {max(y_values)-min(y_values)})")
    
    # Test our strike zone assumptions by looking at called strikes vs balls
    print(f"\n=== STRIKE ZONE VALIDATION ===")
    
    # Group by our location categories and see what percentage are strikes vs balls
    location_results = defaultdict(lambda: {'strikes': 0, 'balls': 0, 'fouls': 0, 'other': 0})
    
    for pitch in all_pitch_data:
        location = get_pitch_location_test(pitch['x'], pitch['y'])
        summary = pitch['summary'].lower() if pitch['summary'] else ''
        result = pitch['result'].lower() if pitch['result'] else ''
        
        if 'strike' in summary and 'looking' in result:
            location_results[location]['strikes'] += 1
        elif 'ball' in summary:
            location_results[location]['balls'] += 1
        elif 'foul' in summary or 'foul' in result:
            location_results[location]['fouls'] += 1
        else:
            location_results[location]['other'] += 1
    
    print("\nStrike Zone Validation (Called Strikes vs Balls by Location):")
    print("Location                | Strikes | Balls | Fouls | Other | Strike%")
    print("-" * 70)
    
    for location, counts in sorted(location_results.items()):
        total_calls = counts['strikes'] + counts['balls']
        if total_calls > 0:
            strike_pct = (counts['strikes'] / total_calls) * 100
        else:
            strike_pct = 0
        
        print(f"{location:22s} | {counts['strikes']:7d} | {counts['balls']:5d} | {counts['fouls']:5d} | {counts['other']:5d} | {strike_pct:6.1f}%")
    
    # Show some sample pitches from each location
    print(f"\n=== SAMPLE PITCHES BY LOCATION ===")
    location_samples = defaultdict(list)
    
    for pitch in all_pitch_data:
        location = get_pitch_location_test(pitch['x'], pitch['y'])
        if len(location_samples[location]) < 3:  # Keep first 3 samples per location
            location_samples[location].append(pitch)
    
    for location, samples in sorted(location_samples.items()):
        print(f"\n{location}:")
        for i, pitch in enumerate(samples, 1):
            print(f"  {i}. {pitch['pitch_type']} ({pitch['velocity']} mph) - {pitch['result']}")
            print(f"     Coordinates: ({pitch['x']}, {pitch['y']})")
    
    print(f"\n=== RECOMMENDATIONS ===")
    
    # Check if our strike zone assumptions make sense
    center_data = location_results.get('Strike Zone Center', {})
    outside_data = location_results.get('Outside', {})
    inside_data = location_results.get('Inside', {})
    
    center_calls = center_data['strikes'] + center_data['balls']
    if center_calls > 0:
        center_strike_rate = (center_data['strikes'] / center_calls) * 100
        print(f"Strike Zone Center: {center_strike_rate:.1f}% called strikes (Expected: >80%)")
        
        if center_strike_rate > 70:
            print("✅ Strike zone center mapping appears accurate")
        else:
            print("⚠️ Strike zone center may need adjustment")
    
    outside_calls = outside_data['strikes'] + outside_data['balls']  
    if outside_calls > 0:
        outside_strike_rate = (outside_data['strikes'] / outside_calls) * 100
        print(f"Outside Zone: {outside_strike_rate:.1f}% called strikes (Expected: <30%)")
        
        if outside_strike_rate < 40:
            print("✅ Outside zone mapping appears accurate")
        else:
            print("⚠️ Outside zone boundaries may need adjustment")

if __name__ == "__main__":
    validate_strike_zone_assumptions()
