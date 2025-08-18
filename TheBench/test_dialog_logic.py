#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import ApiService

def test_stats_dialog_logic():
    """Test the exact logic the statistics dialog uses"""
    print("Testing statistics dialog logic...")
    
    try:
        # Get the actual statistics data
        stats_data = ApiService.get_statistics("MLB")
        
        if not stats_data:
            print("No statistics data available")
            return
        
        # Simulate what the dialog does for team stats
        stat_type = "team"
        category = "Batting Average"  # A common stat to test
        
        print(f"Looking for category: {category}")
        
        if stat_type == "team":
            team_stats = stats_data.get("team_stats", [])
            print(f"Found {len(team_stats)} team stat categories")
            
            for stat_category in team_stats:
                category_name = stat_category.get("category", "")
                teams_in_category = stat_category.get("stats", [])
                
                print(f"Checking category: '{category_name}' with {len(teams_in_category)} teams")
                
                if teams_in_category:
                    # Get the first team's stats to see what's available
                    first_team = teams_in_category[0]
                    team_stats_dict = first_team.get("stats", {})
                    
                    print(f"Available stats in {category_name}: {list(team_stats_dict.keys())[:5]}...")
                    
                    # Look for the exact stat name the user wants
                    best_stat_name = None
                    
                    # Direct match
                    if category in team_stats_dict:
                        best_stat_name = category
                        print(f"Found direct match: {best_stat_name}")
                    else:
                        # Fuzzy matching
                        for stat_name in team_stats_dict.keys():
                            if category.lower() in stat_name.lower():
                                best_stat_name = stat_name
                                print(f"Found fuzzy match: {best_stat_name}")
                                break
                    
                    if best_stat_name:
                        print(f"Using stat: {best_stat_name}")
                        
                        # Collect all teams' data for this stat - simulate the dialog logic
                        teams_data = []
                        for team_info in teams_in_category:
                            team_name = team_info.get("team_name", "Unknown")
                            team_stats_dict = team_info.get("stats", {})
                            
                            if best_stat_name in team_stats_dict:
                                stat_value = team_stats_dict[best_stat_name]
                                print(f"  {team_name}: {stat_value}")
                                
                                # Try to convert to numeric for sorting
                                numeric_value = 0
                                try:
                                    numeric_value = float(stat_value)
                                except (ValueError, TypeError):
                                    pass
                                
                                teams_data.append({
                                    "name": team_name,
                                    "value": numeric_value,
                                    "displayValue": str(stat_value)
                                })
                        
                        if teams_data:
                            print(f"Successfully collected data for {len(teams_data)} teams")
                            
                            # Test the sorting and display logic
                            teams_data.sort(key=lambda x: x["value"], reverse=True)
                            
                            print("Top 5 teams:")
                            for rank, item in enumerate(teams_data[:5], 1):
                                team_name = item.get('name', 'Unknown')
                                display_value = item.get('displayValue', str(item.get('value', '')))
                                list_text = f"{rank} {team_name} {display_value}"
                                print(f"  {list_text}")
                        
                        return  # Found what we're looking for
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stats_dialog_logic()
