#!/usr/bin/env python3
"""Test script to verify pitch location mapping is working correctly."""

import json
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scores import get_pitch_location

def test_pitch_locations():
    """Test the pitch location mapping with known coordinate values."""
    
    print("Testing Pitch Location Mapping")
    print("=" * 40)
    
    # Test cases with known coordinates from our analysis
    test_cases = [
        # Center strike zone
        (118, 180, "Expected: Strike Zone - Center"),
        # Outside corner
        (180, 180, "Expected: Outside"),
        # Inside corner  
        (80, 180, "Expected: Inside"),
        # High
        (118, 120, "Expected: High"),
        # Low
        (118, 240, "Expected: Low"),
        # Far outside
        (200, 180, "Expected: Way Outside"),
        # Far inside
        (40, 180, "Expected: Way Inside"),
    ]
    
    print("Testing coordinate mappings:")
    for x, y, expected in test_cases:
        location = get_pitch_location(x, y)
        print(f"  ({x:3d}, {y:3d}) -> {location:20s} | {expected}")
    
    print("\nTesting with actual game data...")
    
    # Load a sample game file to test with real data
    game_files = [
        "api_exploration/game_details_401696636.json",
        "api_exploration/game_details_401696637.json",
    ]
    
    for game_file in game_files:
        if os.path.exists(game_file):
            print(f"\nTesting with {game_file}:")
            test_real_game_data(game_file)
            break
    else:
        print("\nNo game files found for real data testing")

def test_real_game_data(game_file):
    """Test with actual game data to see the enhancement in action."""
    
    try:
        with open(game_file, 'r') as f:
            game_data = json.load(f)
        
        # Find plays with pitch data
        plays_data = game_data.get('drives', [])
        pitch_count = 0
        location_count = 0
        
        for drive in plays_data:
            for play in drive.get('plays', []):
                if play.get('type', {}).get('text') == 'Pitch':
                    pitch_count += 1
                    
                    # Check for coordinate data
                    coordinate = play.get('coordinate')
                    if coordinate:
                        x = coordinate.get('x')
                        y = coordinate.get('y')
                        if x is not None and y is not None:
                            location = get_pitch_location(x, y)
                            location_count += 1
                            
                            # Show the enhanced display
                            play_text = play.get('text', 'Pitch')
                            print(f"    {play_text} - {location}")
                            
                            if location_count >= 5:  # Just show first 5 examples
                                break
            if location_count >= 5:
                break
        
        print(f"  Found {pitch_count} pitches, {location_count} with coordinates")
        
    except Exception as e:
        print(f"  Error testing real data: {e}")

if __name__ == "__main__":
    test_pitch_locations()
