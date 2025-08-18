#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

def check_data_timeframe():
    """Check what time period the ESPN API data covers"""
    print("DEBUG: Checking ESPN API data timeframe...")
    
    try:
        # Get the raw ESPN statistics API data
        url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Look at the season/timeframe info
            print("API Response metadata:")
            print(f"  Status: {data.get('status', 'Unknown')}")
            print(f"  Timestamp: {data.get('timestamp', 'Unknown')}")
            
            season = data.get('season', {})
            print(f"  Season: {season}")
            
            # Look for any date ranges or filters
            if 'query' in data:
                print(f"  Query parameters: {data['query']}")
            
            # Check if there are any period/timeframe indicators
            stats = data.get("stats", {})
            if 'timestamp' in stats:
                print(f"  Stats timestamp: {stats['timestamp']}")
            
            # Look at a specific category to see if there's timeframe info
            categories = stats.get("categories", [])
            if categories:
                wins_category = None
                for cat in categories:
                    if cat.get('name') == 'wins':
                        wins_category = cat
                        break
                
                if wins_category:
                    print(f"\nWins category details:")
                    for key, value in wins_category.items():
                        if key != 'leaders':  # Skip the large leaders array
                            print(f"  {key}: {value}")
                    
                    # Look at first few leaders to see if there's date info
                    leaders = wins_category.get('leaders', [])
                    if leaders:
                        print(f"\nFirst leader details:")
                        first_leader = leaders[0]
                        for key, value in first_leader.items():
                            if key not in ['athlete', 'team', 'statistics']:  # Skip complex objects
                                print(f"  {key}: {value}")
                        
                        # Check if statistics has timeframe info
                        if 'statistics' in first_leader:
                            stats_detail = first_leader['statistics']
                            print(f"  statistics keys: {list(stats_detail.keys())}")
        
        # Also check if there's a season-long endpoint
        print(f"\n=== Checking for full season endpoint ===")
        season_url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?season=2025&seasontype=2"
        response2 = requests.get(season_url)
        print(f"Season-specific URL status: {response2.status_code}")
        
        if response2.status_code == 200:
            season_data = response2.json()
            season_season = season_data.get('season', {})
            print(f"Season endpoint season info: {season_season}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_data_timeframe()
