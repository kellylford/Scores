#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_mlb_stats_api():
    """Test the official MLB Stats API to understand its structure"""
    print("Testing MLB Stats API...")
    
    # Test different stat categories
    test_categories = [
        # Batting
        ("homeRuns", "hitting", "2024"),
        ("battingAverage", "hitting", "2024"), 
        ("rbi", "hitting", "2024"),
        ("hits", "hitting", "2024"),
        ("runs", "hitting", "2024"),
        ("stolenBases", "hitting", "2024"),
        
        # Pitching
        ("wins", "pitching", "2024"),
        ("era", "pitching", "2024"),
        ("strikeouts", "pitching", "2024"),
        ("saves", "pitching", "2024"),
        ("holds", "pitching", "2024"),
    ]
    
    successful_calls = []
    
    for category, group, season in test_categories:
        url = f"https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories={category}&statGroup={group}&season={season}"
        print(f"\nTesting: {category} ({group})")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if 'leagueLeaders' in data and len(data['leagueLeaders']) > 0:
                    leaders = data['leagueLeaders'][0]
                    if 'leaders' in leaders and len(leaders['leaders']) > 0:
                        top_leader = leaders['leaders'][0]
                        name = top_leader.get('person', {}).get('fullName', 'Unknown')
                        value = top_leader.get('value', 0)
                        
                        print(f"  ✅ Leader: {name} = {value}")
                        successful_calls.append((category, group, season, url, data))
                        
                        # Check if these are season-level values
                        if category == "homeRuns" and float(value) > 30:
                            print(f"  🎯 SEASON DATA: {value} HRs (vs 4 from ESPN)")
                        elif category == "wins" and float(value) > 10:
                            print(f"  🎯 SEASON DATA: {value} wins (vs 4 from ESPN)")
                        elif category == "rbi" and float(value) > 80:
                            print(f"  🎯 SEASON DATA: {value} RBIs (vs 20 from ESPN)")
                            
            else:
                print(f"  ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"  💥 Exception: {str(e)[:60]}")
    
    # Save successful data structure for analysis
    if successful_calls:
        with open("mlb_api_structure.json", "w") as f:
            json.dump({
                'successful_calls': len(successful_calls),
                'sample_data': successful_calls[0][4] if successful_calls else None
            }, f, indent=2)
        print(f"\n💾 Saved sample to mlb_api_structure.json")
        
        return successful_calls
    
    return []

def test_current_season():
    """Test with current season (2025)"""
    print(f"\n=== Testing Current Season (2025) ===")
    
    url = "https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories=homeRuns&statGroup=hitting&season=2025"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if 'leagueLeaders' in data and len(data['leagueLeaders']) > 0:
                leaders = data['leagueLeaders'][0]
                if 'leaders' in leaders and len(leaders['leaders']) > 0:
                    print(f"2025 season data available!")
                    for i, leader in enumerate(leaders['leaders'][:5]):
                        name = leader.get('person', {}).get('fullName', 'Unknown')
                        value = leader.get('value', 0)
                        print(f"  {i+1}. {name}: {value} HRs")
                    return True
            else:
                print(f"No 2025 data yet")
                return False
        else:
            print(f"Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    successful = test_mlb_stats_api()
    
    if successful:
        print(f"\n🎯 SUCCESS! Found {len(successful)} working MLB API endpoints")
        print("These provide REAL season statistics, not recent performance!")
        
        # Test current season
        current_available = test_current_season()
        
        season = "2025" if current_available else "2024"
        print(f"\nRecommendation: Use MLB Stats API with season={season}")
        
    else:
        print(f"\n❌ MLB Stats API failed")
