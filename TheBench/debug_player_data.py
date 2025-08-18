#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import ApiService

def debug_player_data():
    """Debug player statistics to see if data is scrambled"""
    print("DEBUG: Checking player statistics structure...")
    
    try:
        # Get the actual statistics data
        stats_data = ApiService.get_statistics("MLB")
        
        if not stats_data:
            print("No statistics data available")
            return
        
        player_stats = stats_data.get("player_stats", [])
        print(f"Found {len(player_stats)} player stat categories")
        
        if player_stats:
            # Look at the first few categories
            for i, category in enumerate(player_stats[:3]):  # Check first 3 categories
                category_name = category.get("category", "Unknown")
                stats_list = category.get("stats", [])
                
                print(f"\n=== Category {i+1}: {category_name} ===")
                print(f"Found {len(stats_list)} player stats")
                
                if stats_list:
                    # Look at the first few players
                    print("First 5 players in this category:")
                    for j, stat in enumerate(stats_list[:5]):
                        player_name = stat.get("player_name", "Unknown")
                        team = stat.get("team", "Unknown")
                        value = stat.get("value", "Unknown")
                        stat_name = stat.get("stat_name", "Unknown")
                        
                        print(f"  {j+1}. {player_name} ({team}) - {stat_name}: {value}")
                    
                    # Check if all stats in this category have the same stat_name
                    stat_names = set()
                    for stat in stats_list:
                        stat_names.add(stat.get("stat_name", "Unknown"))
                    
                    print(f"Unique stat names in {category_name}: {list(stat_names)}")
                    
                    if len(stat_names) > 1:
                        print(f"  WARNING: Multiple stat types in same category!")
                        for stat_name in stat_names:
                            count = sum(1 for s in stats_list if s.get("stat_name") == stat_name)
                            print(f"    {stat_name}: {count} players")
                    
                    # Check for data consistency
                    print("Checking data consistency...")
                    for j, stat in enumerate(stats_list[:10]):  # Check first 10
                        player_name = stat.get("player_name", "")
                        team = stat.get("team", "")
                        value = stat.get("value", "")
                        
                        # Look for potential issues
                        issues = []
                        if not player_name or player_name == "Unknown":
                            issues.append("missing player name")
                        if not team or team == "Unknown":
                            issues.append("missing team")
                        if not value or str(value) == "Unknown":
                            issues.append("missing value")
                        
                        if issues:
                            print(f"    Player {j+1} issues: {', '.join(issues)}")
                            print(f"      Data: {stat}")
                        
        else:
            print("No player statistics found")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_player_data()
