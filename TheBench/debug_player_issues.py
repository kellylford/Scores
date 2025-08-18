#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import ApiService

def debug_player_issues():
    """Debug the specific player statistics issues"""
    print("DEBUG: Investigating player statistics issues...")
    
    try:
        # Get the actual statistics data
        stats_data = ApiService.get_statistics("MLB")
        
        if not stats_data:
            print("No statistics data available")
            return
        
        player_stats = stats_data.get("player_stats", [])
        print(f"Found {len(player_stats)} player stat categories")
        
        # Look specifically at pitching wins
        for category in player_stats:
            category_name = category.get("category", "Unknown")
            if "wins" in category_name.lower() or category_name.lower() == "wins":
                stats_list = category.get("stats", [])
                print(f"\n=== {category_name} Category ===")
                print(f"Found {len(stats_list)} player stats")
                
                # Check the actual values
                print("Top 10 players in this category:")
                for i, stat in enumerate(stats_list[:10]):
                    player_name = stat.get("player_name", "Unknown")
                    team = stat.get("team", "Unknown")
                    value = stat.get("value", "Unknown")
                    stat_name = stat.get("stat_name", "Unknown")
                    
                    print(f"  {i+1}. {player_name} ({team}) - {stat_name}: {value}")
                
                # Look for wins-related stats by checking all stat names
                stat_names = set()
                for stat in stats_list:
                    stat_names.add(stat.get("stat_name", "Unknown"))
                
                print(f"All stat names in {category_name}: {list(stat_names)}")
                break
        
        # Now look at how player stats get processed in the dialog
        print("\n=== Testing Player Stats Processing ===")
        
        # Look for a player stat that should have high values
        for category in player_stats:
            category_name = category.get("category", "Unknown")
            stats_list = category.get("stats", [])
            
            if stats_list:
                # Group by stat types to see the structure
                stat_types = {}
                for stat in stats_list:
                    stat_name = stat.get("stat_name", "Unknown")
                    if stat_name not in stat_types:
                        stat_types[stat_name] = []
                    stat_types[stat_name].append(stat)
                
                print(f"\nCategory: {category_name}")
                for stat_name, players in stat_types.items():
                    print(f"  {stat_name}: {len(players)} players")
                    if len(players) > 0:
                        top_player = players[0]
                        print(f"    Top: {top_player.get('player_name')} - {top_player.get('value')}")
                
                # Show how the dialog would format this
                if "wins" in category_name.lower():
                    print(f"\n  Dialog would show as:")
                    for stat_name, players in stat_types.items():
                        dialog_name = f"{stat_name} ({category_name})"
                        print(f"    '{dialog_name}'")
                        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_player_issues()
