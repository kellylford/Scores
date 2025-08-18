#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

def find_full_season_endpoints():
    """Investigate ESPN's API structure to find full season player statistics"""
    print("DEBUG: Searching for full season player statistics endpoints...")
    
    # URLs to test based on ESPN's actual website structure
    endpoints_to_test = [
        # Team-based statistics (often more comprehensive)
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/statistics",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/statistics?season=2025",
        
        # Players endpoints
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/athletes/statistics",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/athletes/statistics?season=2025",
        
        # Different statistics structure
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics/players",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics/players?season=2025",
        
        # Scorecard/season endpoints
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard/statistics",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/seasons/2025/statistics",
        
        # Try with different filters
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?seasontype=2&season=2025",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?qualified=true",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?qualified=true&season=2025",
        
        # ESPN Core API patterns
        "https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/statistics",
        "https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/seasons/2025/statistics",
        
        # Try the way ESPN website might call it
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?view=season",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?type=season",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?scope=season",
    ]
    
    successful_endpoints = []
    
    for i, url in enumerate(endpoints_to_test):
        print(f"\n{i+1}. Testing: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS - Keys: {list(data.keys())}")
                
                # Look for player statistics with higher values
                found_high_values = False
                
                # Check different possible structures
                if 'stats' in data:
                    stats = data['stats']
                    if 'categories' in stats:
                        for cat in stats.get('categories', []):
                            if cat.get('name') == 'wins':
                                leaders = cat.get('leaders', [])
                                if leaders:
                                    top_value = leaders[0].get('value', 0)
                                    print(f"   Wins leader: {top_value}")
                                    if top_value > 10:  # Season-like value
                                        found_high_values = True
                                        print(f"   🎯 FOUND SEASON DATA!")
                                break
                
                if 'athletes' in data:
                    print(f"   Has athletes data")
                    
                if 'teams' in data:
                    print(f"   Has teams data")
                
                if found_high_values:
                    successful_endpoints.append(url)
                    
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            else:
                print(f"   ⚠️  Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)[:100]}")
    
    print(f"\n=== RESULTS ===")
    if successful_endpoints:
        print(f"Found {len(successful_endpoints)} endpoints with potential season data:")
        for url in successful_endpoints:
            print(f"  ✅ {url}")
    else:
        print("❌ No endpoints found with full season data")
    
    return successful_endpoints

if __name__ == "__main__":
    find_full_season_endpoints()
