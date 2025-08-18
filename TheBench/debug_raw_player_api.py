#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

def debug_raw_player_api():
    """Look at the raw ESPN player statistics API to understand the data structure"""
    print("DEBUG: Checking raw ESPN player statistics API...")
    
    try:
        # Get the raw ESPN statistics API data
        url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Look at the structure
            stats = data.get("stats", {})
            categories = stats.get("categories", [])
            
            print(f"Found {len(categories)} categories")
            
            # Look at the first few categories
            for i, category in enumerate(categories[:3]):
                category_name = category.get("displayName", category.get("name", "Unknown"))
                leaders = category.get("leaders", [])
                
                print(f"\n=== Category {i+1}: {category_name} ===")
                print(f"Found {len(leaders)} leaders")
                
                if leaders:
                    # Look at the first few leaders
                    print("First 3 leaders structure:")
                    for j, leader in enumerate(leaders[:3]):
                        print(f"\n  Leader {j+1}:")
                        print(f"    Keys: {list(leader.keys())}")
                        
                        athlete = leader.get("athlete", {})
                        print(f"    Athlete name: {athlete.get('displayName', 'Unknown')}")
                        
                        team = leader.get("team", {})
                        print(f"    Team: {team.get('abbreviation', 'Unknown')}")
                        
                        print(f"    Raw value: {leader.get('value', 'None')}")
                        print(f"    Display value: {leader.get('displayValue', 'None')}")
                        
                        # Check if there are stats breakdown
                        if "statistics" in leader:
                            print(f"    Has statistics breakdown: {list(leader['statistics'].keys())}")
                        
        else:
            print(f"Failed to get data: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_raw_player_api()
