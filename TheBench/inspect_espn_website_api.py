#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def inspect_espn_website_api():
    """Reverse engineer the actual API calls ESPN's website makes"""
    print("Analyzing ESPN's actual API calls for full season statistics...")
    
    # These are the patterns ESPN websites typically use
    test_endpoints = [
        # Core API with different paths
        "https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/seasons/2025/athletes",
        "https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/seasons/2025/statistics",
        "https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes",
        
        # Specific statistics endpoints
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics/leaders",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/leaders",
        
        # ESPN's stats page format
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics/_/view/batting",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics/_/view/pitching",
        
        # Try with specific categories
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?category=batting",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?category=pitching", 
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?category=fielding",
        
        # Fantasy API (often has full stats)
        "https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/segments/0/leagues",
        "https://fantasy.espn.com/apis/v3/games/flb/seasons/2025/players",
        
        # Hidden API endpoints
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?limit=50",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?limit=100&qualified=true",
        
        # Try the exact structure from website
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?category=batting&qualified=true",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics?category=pitching&qualified=true",
    ]
    
    for i, url in enumerate(test_endpoints):
        print(f"\n{i+1}. Testing: {url}")
        try:
            response = requests.get(url, timeout=10)
            status = response.status_code
            print(f"   Status: {status}")
            
            if status == 200:
                data = response.json()
                print(f"   Keys: {list(data.keys())}")
                
                # Check for high statistical values that indicate season data
                if check_for_season_stats(data):
                    print(f"   🎯 FOUND SEASON DATA!")
                    save_sample_data(url, data)
                    return url, data
                    
            elif status == 401:
                print(f"   🔐 Requires authentication")
            elif status == 403:
                print(f"   🚫 Forbidden")
            elif status == 404:
                print(f"   ❌ Not found")
            else:
                print(f"   ⚠️ Error: {status}")
                
        except Exception as e:
            print(f"   💥 Exception: {str(e)[:80]}")
    
    return None, None

def check_for_season_stats(data):
    """Check if the data contains season-level statistics"""
    
    # Look for batting average > .300 (website shows .333 leaders)
    # Look for HRs > 30 (website shows 40+ leaders)  
    # Look for RBIs > 80 (website shows 100+ leaders)
    # Look for wins > 10 (website shows 14 leaders)
    
    if 'stats' in data and 'categories' in data['stats']:
        for category in data['stats']['categories']:
            category_name = category.get('name', '').lower()
            leaders = category.get('leaders', [])
            
            if leaders and len(leaders) > 0:
                top_value = leaders[0].get('value', 0)
                
                # Check for season-level indicators
                if category_name == 'battingaverage' and top_value > 0.32:
                    print(f"     Season BA found: {top_value}")
                    return True
                elif category_name == 'homeruns' and top_value > 30:
                    print(f"     Season HRs found: {top_value}")
                    return True
                elif category_name == 'rbi' and top_value > 80:
                    print(f"     Season RBIs found: {top_value}")
                    return True
                elif category_name == 'wins' and top_value > 10:
                    print(f"     Season Wins found: {top_value}")
                    return True
    
    # Check other possible structures
    if 'athletes' in data:
        athletes = data['athletes']
        if isinstance(athletes, list) and len(athletes) > 0:
            # Sample first athlete for season-like stats
            athlete = athletes[0]
            if 'statistics' in athlete:
                stats = athlete['statistics']
                # Look for high values in any stat category
                for stat_group in stats:
                    if isinstance(stat_group, dict):
                        for key, value in stat_group.items():
                            if isinstance(value, (int, float)) and value > 30:
                                print(f"     High value found: {key}={value}")
                                return True
    
    return False

def save_sample_data(url, data):
    """Save successful API response for analysis"""
    filename = "successful_season_api_data.json"
    with open(filename, 'w') as f:
        json.dump({
            'url': url,
            'data': data
        }, f, indent=2)
    print(f"   💾 Saved data to {filename}")

if __name__ == "__main__":
    url, data = inspect_espn_website_api()
    
    if url:
        print(f"\n🎯 SUCCESS! Found season data at: {url}")
        print("Check successful_season_api_data.json for full response")
    else:
        print(f"\n❌ Could not find ESPN API endpoint with full season statistics")
        print("ESPN may be using:")
        print("1. Authentication/API keys")
        print("2. Different API domains")
        print("3. GraphQL endpoints")
        print("4. WebSocket connections")
