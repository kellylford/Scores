#!/usr/bin/env python3

"""
Quick test to verify stat selection works after the fix
"""

import sys
import os
sys.path.append('.')

# Set environment to avoid GUI
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from services.api_service import ApiService

def test_stat_selection():
    print("Testing stat selection fix...")
    
    # Get MLB statistics data
    print("Fetching MLB statistics...")
    try:
        stats_data = ApiService.get_statistics("MLB")
        print(f"Got data with {len(stats_data.get('player_stats', []))} player categories and {len(stats_data.get('team_stats', []))} team categories")
        
        # Test team stats structure
        team_stats = stats_data.get('team_stats', [])
        if team_stats:
            print(f"\nFirst team stats category: {team_stats[0].get('category', 'Unknown')}")
            first_category_stats = team_stats[0].get('stats', [])
            if first_category_stats:
                first_team = first_category_stats[0]
                print(f"First team: {first_team.get('team_name', 'Unknown')}")
                print(f"First team stats keys: {list(first_team.get('stats', {}).keys())}")
                
                # Test a few more teams
                print("\nFirst 3 teams in this category:")
                for i, team in enumerate(first_category_stats[:3]):
                    team_name = team.get('team_name', 'Unknown')
                    stats_dict = team.get('stats', {})
                    print(f"  {i+1}. {team_name}: {stats_dict}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stat_selection()
