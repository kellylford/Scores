#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from espn_api import ESPNApi

def debug_team_structure():
    """Debug the team statistics structure to understand why teams show as 'Unknown'"""
    print("DEBUG: Checking team statistics structure...")
    
    api = ESPNApi()
    try:
        # Get team statistics
        print("Getting team statistics...")
        team_stats = api.get_team_statistics("MLB")
        
        if team_stats:
            print(f"DEBUG: Got {len(team_stats)} team stat categories")
            
            # Look at the first category
            if len(team_stats) > 0:
                first_category = team_stats[0]
                print(f"DEBUG: First category: {first_category.get('category', 'No category')}")
                
                teams = first_category.get("stats", [])
                print(f"DEBUG: Found {len(teams)} teams")
                
                if teams:
                    # Look at the first team's structure
                    first_team = teams[0]
                    print("DEBUG: First team structure:")
                    print(f"  Keys available: {list(first_team.keys())}")
                    
                    for key, value in first_team.items():
                        if key == "stats":
                            print(f"  {key}: {type(value)} with {len(value) if isinstance(value, dict) else 'N/A'} items")
                            if isinstance(value, dict):
                                print(f"    Stats keys: {list(value.keys())[:5]}...")  # Show first 5 stat keys
                        else:
                            print(f"  {key}: {value}")
                    
                    print("\nDEBUG: Checking other team structures...")
                    for i, team in enumerate(teams[:3]):  # Check first 3 teams
                        team_identifier = None
                        for key in ['team_name', 'name', 'displayName', 'shortDisplayName', 'abbreviation']:
                            if key in team:
                                team_identifier = team[key]
                                print(f"  Team {i+1}: {key} = {team_identifier}")
                                break
                        if not team_identifier:
                            print(f"  Team {i+1}: No recognizable team name field found")
                            print(f"    Available keys: {list(team.keys())}")
        else:
            print("DEBUG: No team statistics returned")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_team_structure()
