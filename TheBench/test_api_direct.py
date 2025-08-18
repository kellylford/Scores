#!/usr/bin/env python3
"""
Direct API test to verify data structure
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import ApiService

def test_api_directly():
    """Test the API without any GUI"""
    print("=== DIRECT API TEST ===")
    
    try:
        print("Calling ApiService.get_statistics('MLB')...")
        stats_data = ApiService.get_statistics("MLB")
        
        print(f"Returned data type: {type(stats_data)}")
        print(f"Data keys: {list(stats_data.keys()) if isinstance(stats_data, dict) else 'Not a dict'}")
        
        if stats_data:
            player_stats = stats_data.get("player_stats", [])
            print(f"Player stats categories: {len(player_stats)}")
            
            if player_stats:
                first_category = player_stats[0]
                print(f"First category: {first_category.get('category', 'Unknown')}")
                stats_list = first_category.get("stats", [])
                print(f"Stats in first category: {len(stats_list)}")
                
                if stats_list:
                    first_stat = stats_list[0]
                    print(f"First stat keys: {list(first_stat.keys()) if isinstance(first_stat, dict) else 'Not a dict'}")
                    print(f"First stat sample: {first_stat}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_directly()
