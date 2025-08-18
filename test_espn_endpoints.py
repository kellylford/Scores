#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

def test_different_espn_endpoints():
    """Test different ESPN endpoints to find full season statistics"""
    print("DEBUG: Testing different ESPN endpoints for full season data...")
    
    endpoints_to_try = [
        # Current endpoint
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics",
        
        # Try with explicit season parameters
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?season=2025",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?season=2025&seasontype=2",
        
        # Try leaders endpoint
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/leaders",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/leaders?season=2025",
        
        # Try athletes endpoint
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/athletes",
        
        # Try specific stat categories
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics/categories",
        
        # Try with different params
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?limit=100",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?period=season",
    ]
    
    for i, url in enumerate(endpoints_to_try):
        print(f"\n{i+1}. Testing: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for wins data specifically
                if 'stats' in data and 'categories' in data['stats']:
                    categories = data['stats']['categories']
                    wins_cat = None
                    for cat in categories:
                        if cat.get('name') == 'wins':
                            wins_cat = cat
                            break
                    
                    if wins_cat:
                        leaders = wins_cat.get('leaders', [])
                        if leaders:
                            top_wins = leaders[0].get('value', 0)
                            player_name = leaders[0].get('athlete', {}).get('displayName', 'Unknown')
                            print(f"   Top wins: {player_name} with {top_wins}")
                        else:
                            print(f"   No leaders in wins category")
                    else:
                        print(f"   No wins category found")
                        # Show available categories
                        cat_names = [cat.get('name', 'Unknown') for cat in categories[:5]]
                        print(f"   Available categories: {cat_names}...")
                else:
                    print(f"   No stats/categories structure")
                    print(f"   Keys: {list(data.keys())}")
            
            elif response.status_code == 404:
                print(f"   Not found")
            else:
                print(f"   Error: {response.status_code}")
                
        except Exception as e:
            print(f"   Exception: {e}")

if __name__ == "__main__":
    test_different_espn_endpoints()
