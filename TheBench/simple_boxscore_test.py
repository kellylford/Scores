#!/usr/bin/env python3
"""
Simple test to check boxscore data parsing
"""

import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService

def test_boxscore_with_game_id(game_id="401581976"):
    """Test boxscore parsing with a specific game ID"""
    print(f"Testing game ID: {game_id}")
    
    try:
        # Get raw game details
        print("1. Getting raw game details...")
        raw_details = ApiService.get_game_details("mlb", game_id)
        
        if not raw_details:
            print("❌ No data returned from API")
            return
        
        print(f"✅ Got raw details with keys: {list(raw_details.keys())}")
        
        # Check if boxscore exists
        if 'boxscore' in raw_details:
            print("✅ Found 'boxscore' key")
            boxscore_data = raw_details['boxscore']
            print(f"   Boxscore type: {type(boxscore_data)}")
            
            if isinstance(boxscore_data, dict):
                print(f"   Boxscore keys: {list(boxscore_data.keys())}")
            elif isinstance(boxscore_data, list):
                print(f"   Boxscore list length: {len(boxscore_data)}")
            else:
                print(f"   Boxscore value: {boxscore_data}")
        else:
            print("❌ No 'boxscore' key found")
            print("   Looking for alternative keys...")
            alt_keys = ['statistics', 'stats', 'gameStats', 'summary', 'playByPlay']
            for key in alt_keys:
                if key in raw_details:
                    print(f"   Found: {key}")
        
        # Test the parsing
        print("\n2. Testing parsed output...")
        processed = ApiService.extract_meaningful_game_info(raw_details)
        
        if 'boxscore' in processed:
            parsed_boxscore = processed['boxscore']
            if parsed_boxscore:
                print("✅ Successfully parsed boxscore")
                teams = parsed_boxscore.get('teams', [])
                players = parsed_boxscore.get('players', [])
                print(f"   Found {len(teams)} teams")
                print(f"   Found {len(players)} player groups")
                
                # Show some sample data
                if teams:
                    print(f"   Sample team: {teams[0].get('name', 'Unknown')}")
                    stats = teams[0].get('stats', {})
                    print(f"   Team stats: {len(stats)} statistics")
                    if stats:
                        sample_stats = list(stats.items())[:3]
                        print(f"   Sample stats: {sample_stats}")
                
                if players:
                    print(f"   Sample player group: {players[0].get('team', 'Unknown')}")
                    player_list = players[0].get('players', [])
                    print(f"   Players in group: {len(player_list)}")
                    if player_list:
                        sample_player = player_list[0]
                        print(f"   Sample player: {sample_player.get('name', 'Unknown')}")
            else:
                print("❌ Parsed boxscore is None/empty")
        else:
            print("❌ No 'boxscore' in processed data")
            print(f"   Processed keys: {list(processed.keys())}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        game_id = sys.argv[1]
    else:
        # Use a default game ID for testing
        game_id = "401581976"
    
    test_boxscore_with_game_id(game_id)
