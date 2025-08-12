#!/usr/bin/env python3
"""
Analyze what MLB game data is available vs what we display
"""

import sys
sys.path.append('.')

import requests
import json
from espn_api import get_game_details

def analyze_available_vs_displayed():
    """Compare available API data with what we currently display"""
    
    # Get a real game to analyze
    url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    response = requests.get(url)
    scoreboard = response.json()
    
    if not scoreboard.get("events"):
        print("No MLB games found today")
        return
    
    game_id = scoreboard["events"][0]["id"]
    print(f"Analyzing game {game_id}")
    
    # Get full game details
    game_details = get_game_details("MLB", game_id)
    
    print("=== ALL AVAILABLE TOP-LEVEL FIELDS ===")
    all_fields = list(game_details.keys())
    all_fields.sort()
    
    for field in all_fields:
        print(f"  {field}")
    
    print(f"\nTotal available fields: {len(all_fields)}")
    
    # Current implementation details
    print("\n=== WHAT WE CURRENTLY SHOW ===")
    
    # From scores.py DETAIL_FIELDS
    configurable_fields = ["boxscore", "plays", "leaders", "standings", "odds", "injuries", "broadcasts", "news", "gameInfo"]
    print("Configurable detail fields:")
    for field in configurable_fields:
        available = "✅" if field in all_fields else "❌"
        print(f"  {available} {field}")
    
    # Basic game info (from extract_meaningful_game_info)
    basic_info_fields = [
        "header", "competitions", "status", "venue", "weather", 
        "betting_line", "over_under", "broadcast", "injuries"
    ]
    print("\nBasic game info fields:")
    for field in basic_info_fields:
        available = "✅" if field in all_fields else "❌"
        print(f"  {available} {field}")
    
    print("\n=== AVAILABLE BUT NOT SHOWN ===")
    displayed_fields = set(configurable_fields + basic_info_fields)
    missing_fields = set(all_fields) - displayed_fields
    
    for field in sorted(missing_fields):
        data_type = type(game_details[field]).__name__
        data_length = len(game_details[field]) if isinstance(game_details[field], (list, dict)) else "N/A"
        print(f"  📋 {field} ({data_type}, length: {data_length})")
        
        # Show a sample of the data
        if field in ["officials", "situation", "format", "predictor", "winprobability"]:
            print(f"      Sample: {str(game_details[field])[:100]}...")
    
    print(f"\nFields available but not displayed: {len(missing_fields)}")
    
    # Detailed analysis of specific interesting fields
    print("\n=== DETAILED ANALYSIS OF INTERESTING FIELDS ===")
    
    interesting_fields = ["officials", "situation", "format", "predictor", "winprobability", "drives", "commentary"]
    
    for field in interesting_fields:
        if field in game_details:
            print(f"\n📋 {field.upper()}:")
            data = game_details[field]
            print(f"   Type: {type(data).__name__}")
            if isinstance(data, dict):
                print(f"   Keys: {list(data.keys())[:10]}")
            elif isinstance(data, list):
                print(f"   Length: {len(data)}")
                if data:
                    print(f"   First item type: {type(data[0]).__name__}")
                    if isinstance(data[0], dict):
                        print(f"   First item keys: {list(data[0].keys())[:5]}")
            
            # Show actual content (truncated)
            print(f"   Sample data: {str(data)[:200]}...")

if __name__ == "__main__":
    analyze_available_vs_displayed()
