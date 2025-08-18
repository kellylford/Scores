#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import ApiService

def debug_team_stats_structure():
    """Debug the actual team statistics structure to see why teams show as Unknown"""
    print("DEBUG: Getting team statistics structure...")
    
    try:
        # Get the actual statistics data that the dialog uses
        stats_data = ApiService.get_statistics("MLB")
        
        if stats_data:
            print(f"DEBUG: Got statistics data with keys: {list(stats_data.keys())}")
            
            team_stats = stats_data.get("team_stats", [])
            print(f"DEBUG: Found {len(team_stats)} team stat categories")
            
            if team_stats:
                # Look at the first category
                first_category = team_stats[0]
                print(f"DEBUG: First category: {first_category.get('category', 'No category')}")
                
                teams = first_category.get("stats", [])
                print(f"DEBUG: Found {len(teams)} teams in first category")
                
                if teams:
                    # Look at the first team's structure
                    first_team = teams[0]
                    print("DEBUG: First team structure:")
                    for key, value in first_team.items():
                        if key == "stats":
                            print(f"  {key}: {type(value)} with {len(value) if isinstance(value, dict) else 'N/A'} items")
                            if isinstance(value, dict) and len(value) > 0:
                                sample_stats = dict(list(value.items())[:3])  # Show first 3 stats
                                print(f"    Sample stats: {sample_stats}")
                        else:
                            print(f"  {key}: {value}")
                    
                    print("\nDEBUG: Checking all teams in first category...")
                    for i, team in enumerate(teams[:5]):  # Check first 5 teams
                        team_name = team.get("team_name", "MISSING")
                        print(f"  Team {i+1}: team_name = '{team_name}'")
                        if team_name == "MISSING":
                            print(f"    Available keys: {list(team.keys())}")
        else:
            print("DEBUG: No statistics data returned")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_team_stats_structure()
