#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

def test_core_api_statistics():
    """Test the core API that showed promise"""
    url = "https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/statistics"
    
    print(f"Testing core API: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Keys: {list(data.keys())}")
            print(f"Count: {data.get('count', 'N/A')}")
            
            if 'items' in data:
                print(f"\nFirst few items:")
                for i, item in enumerate(data['items'][:5]):
                    print(f"  {i+1}. {item}")
                    
                    # Try to fetch the first item to see its structure
                    if i == 0:
                        print(f"\nFetching details for first item...")
                        try:
                            item_response = requests.get(item, timeout=10)
                            if item_response.status_code == 200:
                                item_data = item_response.json()
                                print(f"Item keys: {list(item_data.keys())}")
                                
                                # Look for athletes or statistics
                                if 'athletes' in item_data:
                                    print(f"Has athletes data")
                                if 'leaders' in item_data:
                                    print(f"Has leaders data")
                                if 'statistics' in item_data:
                                    print(f"Has statistics data")
                                
                        except Exception as e:
                            print(f"Error fetching item: {e}")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Exception: {e}")

def test_season_parameters():
    """Test different season parameters to get full season data"""
    base_url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics"
    
    # Try different season-related parameters
    params_to_test = [
        # Try 2024 season (completed)
        {"season": "2024"},
        {"season": "2024", "seasontype": "2"},  # Regular season
        {"season": "2024", "seasontype": "1"},  # Preseason
        {"season": "2024", "seasontype": "3"},  # Postseason
        
        # Try different time ranges
        {"season": "2024", "split": "0"},      # Full season split
        {"season": "2024", "period": "0"},     # Full period
        
        # Try qualified players (might get season stats)
        {"season": "2024", "qualified": "true"},
        {"season": "2024", "qualified": "true", "seasontype": "2"},
        
        # Try cumulative stats
        {"season": "2024", "cumulative": "true"},
        {"season": "2024", "aggregate": "true"},
        
        # Try different views
        {"season": "2024", "view": "full"},
        {"season": "2024", "view": "complete"},
        {"season": "2024", "view": "totals"},
        
        # Try 2023 (definitely completed)
        {"season": "2023", "seasontype": "2"},
        {"season": "2023", "qualified": "true"},
    ]
    
    print("Testing different parameters for full season data...")
    
    for i, params in enumerate(params_to_test):
        print(f"\n{i+1}. Testing params: {params}")
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check wins leader value to see if it's season-like
                if 'stats' in data and 'categories' in data['stats']:
                    for cat in data['stats']['categories']:
                        if cat.get('name') == 'wins':
                            leaders = cat.get('leaders', [])
                            if leaders:
                                top_value = leaders[0].get('value', 0)
                                print(f"   Wins leader: {top_value}")
                                if top_value > 10:
                                    print(f"   🎯 POTENTIAL SEASON DATA!")
                                    return params, data
                            break
            else:
                print(f"   Error: {response.status_code}")
                
        except Exception as e:
            print(f"   Exception: {str(e)[:50]}")
    
    return None, None

if __name__ == "__main__":
    print("=== Testing Core API ===")
    test_core_api_statistics()
    
    print("\n=== Testing Season Parameters ===")
    success_params, success_data = test_season_parameters()
    
    if success_params:
        print(f"\n🎯 SUCCESS! Found season data with params: {success_params}")
    else:
        print(f"\n❌ No full season data found with any parameter combination")
