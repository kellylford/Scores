#!/usr/bin/env python3

"""
Test the fixed statistics selection functionality
"""

import sys
import os
sys.path.append('.')

# Set environment to avoid GUI
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from services.api_service import ApiService

def test_find_stat_for_category():
    """Test the _find_stat_for_category logic directly"""
    print("Testing stat finding logic...")
    
    try:
        # Get the data
        stats_data = ApiService.get_statistics("MLB")
        
        # Simulate the team stats matching
        team_stats = stats_data.get("team_stats", [])
        print(f"Available team stat categories: {[cat.get('category') for cat in team_stats]}")
        
        # Test finding batting stats
        category = "Batting"
        for stat_category in team_stats:
            category_name = stat_category.get("category", "")
            teams_in_category = stat_category.get("stats", [])
            
            if category.lower() in category_name.lower():
                print(f"\nFound matching category: {category_name}")
                if teams_in_category:
                    first_team = teams_in_category[0]
                    team_stats_dict = first_team.get("stats", {})
                    print(f"Available stats in this category: {list(team_stats_dict.keys())[:10]}...")  # Show first 10
                    
                    # Show preferred batting stats
                    preferred_batting = ["Batting Average", "Home Runs", "RBIs", "Runs"]
                    available_preferred = [stat for stat in preferred_batting if stat in team_stats_dict]
                    print(f"Available preferred batting stats: {available_preferred}")
                    
                    if available_preferred:
                        best_stat = available_preferred[0]
                        print(f"Would select: {best_stat}")
                        
                        # Show a few team values
                        print("Sample team data:")
                        for i, team_info in enumerate(teams_in_category[:3]):
                            team_name = team_info.get("team_name", "Unknown")
                            stat_value = team_info.get("stats", {}).get(best_stat, "N/A")
                            print(f"  {i+1}. {team_name}: {stat_value}")
                
                break
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_find_stat_for_category()
