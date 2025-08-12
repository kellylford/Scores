#!/usr/bin/env python3
"""
Debug the game data structure to understand where pitch data is stored
"""

import espn_api
import json

def debug_game_structure():
    """Examine the structure of the Brewers vs Pirates game"""
    
    game_id = '401696689'  # August 11 Brewers vs Pirates
    
    print("=== GAME DATA STRUCTURE DEBUG ===")
    print(f"Game ID: {game_id}")
    
    game_details = espn_api.get_game_details('MLB', game_id)
    
    print(f"Top-level keys: {list(game_details.keys())}")
    print()
    
    # Examine each section that might contain pitch data
    sections_to_check = ['plays', 'atBats', 'playByPlay', 'commentary']
    
    for section in sections_to_check:
        if section in game_details:
            data = game_details[section]
            print(f"=== {section.upper()} SECTION ===")
            print(f"Type: {type(data)}")
            print(f"Length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"First item type: {type(data[0])}")
                if isinstance(data[0], dict):
                    print(f"First item keys: {list(data[0].keys())}")
                    
                    # Check if any items have pitch-related data
                    pitch_count = 0
                    for i, item in enumerate(data[:10]):  # Check first 10 items
                        if isinstance(item, dict):
                            for key in item.keys():
                                if 'pitch' in key.lower():
                                    print(f"  Item {i} has pitch-related key: {key}")
                                    if isinstance(item[key], list):
                                        pitch_count += len(item[key])
                                    else:
                                        pitch_count += 1
                    
                    if pitch_count > 0:
                        print(f"  Total pitch-related items found: {pitch_count}")
                    
            elif isinstance(data, dict):
                print(f"Dictionary keys: {list(data.keys())}")
                
            print()
    
    # Let's also check if there's nested pitch data
    print("=== SEARCHING FOR PITCH COORDINATES ===")
    coordinates_found = []
    
    def search_for_coordinates(obj, path=""):
        """Recursively search for coordinate data"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                
                if key == 'coordinates' and isinstance(value, dict):
                    x, y = value.get('x'), value.get('y')
                    if x is not None and y is not None:
                        coordinates_found.append((x, y, new_path))
                
                search_for_coordinates(value, new_path)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                search_for_coordinates(item, new_path)
    
    search_for_coordinates(game_details)
    
    print(f"Found {len(coordinates_found)} coordinate pairs:")
    for x, y, path in coordinates_found[:10]:  # Show first 10
        print(f"  ({x}, {y}) at {path}")
    
    # Look specifically for (144, 207)
    target_coords = [(x, y, path) for x, y, path in coordinates_found if x == 144 and y == 207]
    if target_coords:
        print(f"\n🎯 FOUND TARGET COORDINATES (144, 207):")
        for x, y, path in target_coords:
            print(f"  Path: {path}")
    else:
        print(f"\n❌ Target coordinates (144, 207) not found")
        
        # Show what coordinates ARE available
        if coordinates_found:
            print("Available coordinates (first 20):")
            for x, y, path in coordinates_found[:20]:
                print(f"  ({x}, {y})")

if __name__ == "__main__":
    debug_game_structure()
