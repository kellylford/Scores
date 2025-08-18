#!/usr/bin/env python3

"""
Test the stat finding logic with actual category names
"""

import sys
import os
sys.path.append('.')

# Set environment to avoid GUI
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from services.api_service import ApiService

def test_batting_average_lookup():
    """Test that 'Batting Average' can be found in team stats"""
    print("Testing Batting Average lookup...")
    
    try:
        # Get the data
        stats_data = ApiService.get_statistics("MLB")
        team_stats = stats_data.get("team_stats", [])
        
        print(f"Available team stat categories: {[cat.get('category') for cat in team_stats]}")
        
        # Test finding "Batting Average" 
        category = "Batting Average"
        found = False
        
        for stat_category in team_stats:
            category_name = stat_category.get("category", "")
            teams_in_category = stat_category.get("stats", [])
            
            if teams_in_category:
                first_team = teams_in_category[0]
                team_stats_dict = first_team.get("stats", {})
                
                # Look for Batting Average
                if category in team_stats_dict:
                    found = True
                    print(f"\n✅ Found '{category}' in category '{category_name}'")
                    
                    # Show sample data
                    print("Sample team data for Batting Average:")
                    for i, team_info in enumerate(teams_in_category[:5]):
                        team_name = team_info.get("team_name", "Unknown")
                        stat_value = team_info.get("stats", {}).get(category, "N/A")
                        print(f"  {i+1}. {team_name}: {stat_value}")
                    break
                    
                # Also check fuzzy matches
                for stat_name in team_stats_dict.keys():
                    if "batting" in stat_name.lower() and "average" in stat_name.lower():
                        found = True
                        print(f"\n✅ Found similar stat '{stat_name}' in category '{category_name}'")
                        break
        
        if not found:
            print(f"\n❌ Could not find '{category}' in any team stats")
            
            # Show what is available
            print("\nAvailable stats in first category:")
            if team_stats and team_stats[0].get("stats"):
                first_team = team_stats[0]["stats"][0]
                available_stats = list(first_team.get("stats", {}).keys())
                for stat in available_stats[:10]:  # Show first 10
                    print(f"  - {stat}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_batting_average_lookup()
