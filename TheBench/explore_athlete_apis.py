#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def explore_core_api_athletes():
    """Explore the core API athletes endpoint that returned data"""
    url = "https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/seasons/2025/athletes"
    
    print(f"Exploring: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Count: {data.get('count', 0)}")
            print(f"Page info: {data.get('pageIndex', 0)}/{data.get('pageCount', 0)}")
            
            if 'items' in data and len(data['items']) > 0:
                print(f"\nFound {len(data['items'])} athlete URLs")
                
                # Test first few athlete URLs to see if they have statistics
                for i, athlete_url in enumerate(data['items'][:3]):
                    print(f"\n{i+1}. Testing athlete: {athlete_url}")
                    
                    try:
                        athlete_response = requests.get(athlete_url, timeout=10)
                        if athlete_response.status_code == 200:
                            athlete_data = athlete_response.json()
                            print(f"   Keys: {list(athlete_data.keys())}")
                            
                            # Check if athlete has statistics URL
                            if 'statistics' in athlete_data:
                                stats_url = athlete_data['statistics']['$ref'] if isinstance(athlete_data['statistics'], dict) else None
                                if stats_url:
                                    print(f"   📊 Has statistics URL: {stats_url}")
                                    
                                    # Test the statistics URL
                                    stats_response = requests.get(stats_url, timeout=10)
                                    if stats_response.status_code == 200:
                                        stats_data = stats_response.json()
                                        print(f"   Stats keys: {list(stats_data.keys())}")
                                        
                                        # Look for season totals
                                        if check_athlete_season_stats(stats_data):
                                            print(f"   🎯 FOUND SEASON STATS!")
                                            save_athlete_stats(athlete_url, stats_url, stats_data)
                                            return stats_url, stats_data
                                else:
                                    print(f"   📊 Has statistics data directly")
                                    if check_athlete_season_stats(athlete_data['statistics']):
                                        print(f"   🎯 FOUND SEASON STATS!")
                                        return athlete_url, athlete_data
                                        
                    except Exception as e:
                        print(f"   Error: {str(e)[:50]}")
                        
    except Exception as e:
        print(f"Error: {e}")
    
    return None, None

def check_athlete_season_stats(stats_data):
    """Check if athlete data contains season statistics"""
    
    if isinstance(stats_data, dict):
        # Look for splits or categories
        if 'splits' in stats_data:
            for split in stats_data['splits']:
                if 'stats' in split:
                    stats = split['stats']
                    # Look for high values indicating season totals
                    for key, value in stats.items():
                        if isinstance(value, (int, float)):
                            # Season-level indicators
                            if key.lower() in ['homeruns', 'hr'] and value > 20:
                                print(f"     Season HRs: {value}")
                                return True
                            elif key.lower() in ['rbi', 'rbis'] and value > 50:
                                print(f"     Season RBIs: {value}")
                                return True
                            elif key.lower() in ['wins', 'w'] and value > 8:
                                print(f"     Season Wins: {value}")
                                return True
                            elif key.lower() in ['hits', 'h'] and value > 100:
                                print(f"     Season Hits: {value}")
                                return True
        
        # Direct stats check
        if 'stats' in stats_data:
            stats = stats_data['stats']
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    if key.lower() in ['homeruns', 'hr'] and value > 20:
                        print(f"     Season HRs: {value}")
                        return True
                    elif key.lower() in ['rbi', 'rbis'] and value > 50:
                        print(f"     Season RBIs: {value}")
                        return True
    
    return False

def save_athlete_stats(athlete_url, stats_url, stats_data):
    """Save successful athlete statistics for analysis"""
    filename = "athlete_season_stats.json"
    with open(filename, 'w') as f:
        json.dump({
            'athlete_url': athlete_url,
            'stats_url': stats_url,
            'stats_data': stats_data
        }, f, indent=2)
    print(f"   💾 Saved to {filename}")

def try_alternative_apis():
    """Try some alternative baseball stats APIs"""
    print("\n=== Trying Alternative APIs ===")
    
    alternatives = [
        # MLB Stats API (official MLB)
        "https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=homeRuns&statGroup=hitting&season=2024",
        "https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=wins&statGroup=pitching&season=2024",
        
        # Sports Reference style
        "https://www.baseball-reference.com/data/leaders/leaders_batting.json",
        "https://www.baseball-reference.com/data/leaders/leaders_pitching.json",
    ]
    
    for url in alternatives:
        print(f"\nTesting alternative: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'List data'}")
                print(f"🎯 SUCCESS! Alternative API found")
                return url, data
                
        except Exception as e:
            print(f"Error: {str(e)[:50]}")
    
    return None, None

if __name__ == "__main__":
    print("=== Exploring Core API Athletes ===")
    stats_url, stats_data = explore_core_api_athletes()
    
    if not stats_url:
        alt_url, alt_data = try_alternative_apis()
        if alt_url:
            print(f"\n🎯 Found alternative API: {alt_url}")
        else:
            print(f"\n❌ No season statistics found in any API")
    else:
        print(f"\n🎯 Found season stats at: {stats_url}")
