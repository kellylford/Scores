#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import ApiService

def test_all_team_categories():
    """Test all team categories that the dialog shows"""
    print("Testing all team statistics categories...")
    
    # The exact categories the dialog shows for MLB team stats
    categories_to_test = [
        "Batting Average", "Home Runs", "RBIs", "Runs", "Hits", "Doubles", "Triples",
        "ERA", "Wins", "Strikeouts", "WHIP", "Saves", "Innings Pitched",
        "Fielding Percentage", "Errors", "Double Plays"
    ]
    
    try:
        # Get the actual statistics data
        stats_data = ApiService.get_statistics("MLB")
        
        if not stats_data:
            print("No statistics data available")
            return
        
        team_stats = stats_data.get("team_stats", [])
        print(f"Found {len(team_stats)} team stat categories")
        
        for category in categories_to_test:
            print(f"\n=== Testing category: {category} ===")
            found_match = False
            
            for stat_category in team_stats:
                category_name = stat_category.get("category", "")
                teams_in_category = stat_category.get("stats", [])
                
                if teams_in_category:
                    # Get the first team's stats to see what's available
                    first_team = teams_in_category[0]
                    team_stats_dict = first_team.get("stats", {})
                    
                    # Look for the exact stat name the user wants
                    best_stat_name = None
                    
                    # Direct match
                    if category in team_stats_dict:
                        best_stat_name = category
                        print(f"  Found direct match: '{best_stat_name}' in category '{category_name}'")
                    else:
                        # Fuzzy matching
                        for stat_name in team_stats_dict.keys():
                            if category.lower() in stat_name.lower():
                                best_stat_name = stat_name
                                print(f"  Found fuzzy match: '{best_stat_name}' in category '{category_name}'")
                                break
                    
                    if best_stat_name:
                        found_match = True
                        
                        # Test collecting team data
                        teams_data = []
                        for team_info in teams_in_category:
                            team_name = team_info.get("team_name", "Unknown")
                            team_stats_dict = team_info.get("stats", {})
                            
                            if best_stat_name in team_stats_dict:
                                stat_value = team_stats_dict[best_stat_name]
                                teams_data.append({
                                    "name": team_name,
                                    "value": stat_value,
                                    "displayValue": str(stat_value)
                                })
                        
                        print(f"  Collected data for {len(teams_data)} teams")
                        if len(teams_data) >= 3:
                            print(f"  Sample teams: {teams_data[0]['name']}, {teams_data[1]['name']}, {teams_data[2]['name']}")
                        break
            
            if not found_match:
                print(f"  *** NO MATCH FOUND for '{category}' ***")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_team_categories()
