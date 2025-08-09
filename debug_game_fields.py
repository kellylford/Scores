#!/usr/bin/env python3
"""
Debug script to see what fields are actually available in the raw game data
"""
import sys
import os
import json

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService

def debug_game_data_fields():
    """Debug what fields are actually available"""
    print("=== Debugging Game Data Fields ===\n")
    
    try:
        league = "mlb"
        game_id = "401696639"  # Known game
        
        print(f"Getting raw data for game {game_id}...")
        raw_details = ApiService.get_game_details(league, game_id)
        
        print(f"\nTop-level fields in raw game data:")
        print(f"Total fields: {len(raw_details.keys())}")
        
        for i, key in enumerate(sorted(raw_details.keys()), 1):
            value = raw_details[key]
            value_type = type(value).__name__
            
            if isinstance(value, (list, dict)):
                size_info = f"({len(value)} items)" if value else "(empty)"
            else:
                size_info = f"({str(value)[:30]}...)" if len(str(value)) > 30 else f"({value})"
            
            print(f"  {i:2d}. {key:20} : {value_type:8} {size_info}")
        
        # Look for any fields that might contain our Kitchen Sink data
        print(f"\n=== Searching for Kitchen Sink-like data ===")
        kitchen_sink_keywords = ["roster", "lineup", "probability", "series", "video", 
                               "article", "spread", "pick", "bet", "odds"]
        
        found_matches = []
        for field_name, field_data in raw_details.items():
            field_lower = field_name.lower()
            for keyword in kitchen_sink_keywords:
                if keyword in field_lower:
                    found_matches.append((field_name, keyword, field_data))
                    break
        
        if found_matches:
            print(f"Found {len(found_matches)} potential Kitchen Sink fields:")
            for field_name, keyword, field_data in found_matches:
                data_type = type(field_data).__name__
                size = len(field_data) if isinstance(field_data, (list, dict)) else "N/A"
                print(f"  • {field_name} (matched '{keyword}'): {data_type}, size={size}")
        else:
            print("No obvious Kitchen Sink fields found")
        
        # Check if any nested data might contain what we're looking for
        print(f"\n=== Checking for nested data structures ===")
        for field_name, field_data in raw_details.items():
            if isinstance(field_data, dict) and len(field_data) > 0:
                nested_keys = list(field_data.keys())
                for keyword in kitchen_sink_keywords:
                    matching_nested = [k for k in nested_keys if keyword in k.lower()]
                    if matching_nested:
                        print(f"  {field_name} contains: {matching_nested}")
        
        # Save a sample of the data for manual inspection
        sample_file = "debug_game_data_sample.json"
        sample_data = {}
        for key, value in list(raw_details.items())[:10]:  # First 10 fields
            if isinstance(value, (dict, list, str, int, float, bool)) and key != "plays":
                sample_data[key] = value
        
        with open(sample_file, 'w') as f:
            json.dump(sample_data, f, indent=2)
        print(f"\nSaved sample data to {sample_file} for manual inspection")
        
        return raw_details
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_game_data_fields()
