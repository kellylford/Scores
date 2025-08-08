#!/usr/bin/env python3
"""
Debug script to check what boxscore data ESPN actually provides for games
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService

def check_game_boxscore(league, game_id):
    """Check what boxscore data is available for a specific game"""
    print(f"\n=== Checking Game {game_id} in {league.upper()} ===")
    
    try:
        # Get raw game details
        raw_details = ApiService.get_game_details(league, game_id)
        
        if not raw_details:
            print("❌ No raw details returned from API")
            return
        
        print(f"✅ Raw details keys: {list(raw_details.keys())}")
        
        # Check if boxscore exists in raw data
        if 'boxscore' in raw_details:
            boxscore_raw = raw_details['boxscore']
            print(f"✅ Found 'boxscore' key in raw data")
            print(f"   Type: {type(boxscore_raw)}")
            
            if isinstance(boxscore_raw, dict):
                print(f"   Boxscore keys: {list(boxscore_raw.keys())}")
                
                # Check for teams data
                if 'teams' in boxscore_raw:
                    teams = boxscore_raw['teams']
                    print(f"   Teams data: {len(teams)} teams found")
                    for i, team in enumerate(teams):
                        if isinstance(team, dict):
                            print(f"     Team {i} keys: {list(team.keys())}")
                            if 'team' in team:
                                team_info = team['team']
                                team_name = team_info.get('displayName', 'Unknown')
                                print(f"     Team {i} name: {team_name}")
                            if 'statistics' in team:
                                stats = team['statistics']
                                print(f"     Team {i} has {len(stats)} stat categories")
                
                # Check for players data
                if 'players' in boxscore_raw:
                    players = boxscore_raw['players']
                    print(f"   Players data: {len(players)} player groups found")
                    for i, player_group in enumerate(players):
                        if isinstance(player_group, dict):
                            print(f"     Player group {i} keys: {list(player_group.keys())}")
                            if 'team' in player_group:
                                team_info = player_group['team']
                                team_name = team_info.get('displayName', 'Unknown')
                                print(f"     Player group {i} team: {team_name}")
                            if 'statistics' in player_group:
                                stats = player_group['statistics']
                                print(f"     Player group {i} has {len(stats)} stat groups")
                
                # Check other potential data locations
                other_keys = [k for k in boxscore_raw.keys() if k not in ['teams', 'players']]
                if other_keys:
                    print(f"   Other boxscore keys: {other_keys}")
            
            elif isinstance(boxscore_raw, list):
                print(f"   Boxscore is a list with {len(boxscore_raw)} items")
                if boxscore_raw:
                    print(f"   First item keys: {list(boxscore_raw[0].keys()) if isinstance(boxscore_raw[0], dict) else 'not a dict'}")
            
            else:
                print(f"   Boxscore data: {boxscore_raw}")
        
        else:
            print("❌ No 'boxscore' key found in raw data")
            print(f"   Available keys: {list(raw_details.keys())}")
            
            # Check for alternative keys that might contain stats
            potential_keys = ['statistics', 'stats', 'gameStats', 'summary']
            for key in potential_keys:
                if key in raw_details:
                    print(f"   Found potential stats key: '{key}'")
                    data = raw_details[key]
                    print(f"     Type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"     Keys: {list(data.keys())}")
                    elif isinstance(data, list) and data:
                        print(f"     List length: {len(data)}")
                        if isinstance(data[0], dict):
                            print(f"     First item keys: {list(data[0].keys())}")
        
        # Test the parsed output
        print(f"\n--- Testing Parsed Output ---")
        processed_details = ApiService.extract_meaningful_game_info(raw_details)
        
        if 'boxscore' in processed_details:
            parsed_boxscore = processed_details['boxscore']
            if parsed_boxscore:
                print(f"✅ Parsed boxscore successfully")
                print(f"   Teams: {len(parsed_boxscore.get('teams', []))}")
                print(f"   Player groups: {len(parsed_boxscore.get('players', []))}")
            else:
                print("❌ Parsed boxscore is None/empty")
        else:
            print("❌ No boxscore in processed details")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def check_recent_games():
    """Check recent games to find ones with boxscore data"""
    print("=== Checking Recent MLB Games ===")
    
    try:
        # Get recent games using get_scores
        from datetime import datetime
        today = datetime.now()
        games = ApiService.get_scores("mlb", today)
        print(f"Found {len(games)} recent games")
        
        for i, game in enumerate(games[:3]):  # Check first 3 games
            if isinstance(game, dict) and 'id' in game:
                game_id = game['id']
                game_status = game.get('status', 'Unknown')
                teams = game.get('shortDetail', 'Unknown teams')
                print(f"\nGame {i+1}: {teams} (Status: {game_status})")
                check_game_boxscore("mlb", game_id)
                
                if i < 2:  # Add separator between games
                    print("-" * 50)
    
    except Exception as e:
        print(f"Error getting recent games: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("ESPN Boxscore Data Diagnostic Tool")
    print("=" * 40)
    
    # Check recent games first
    check_recent_games()
    
    # Allow manual game ID checking
    if len(sys.argv) > 2:
        league = sys.argv[1]
        game_id = sys.argv[2]
        check_game_boxscore(league, game_id)
    else:
        print(f"\nUsage: python {sys.argv[0]} <league> <game_id>")
        print("Example: python debug_boxscore.py mlb 401581976")
