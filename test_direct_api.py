#!/usr/bin/env python3
"""
Test the API call directly to see what's happening
"""
import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import espn_api

def test_direct_api():
    """Test the ESPN API directly"""
    print("=== Testing ESPN API Directly ===\n")
    
    try:
        league = "mlb"
        game_id = "401696639"
        
        print(f"1. Testing direct espn_api.get_game_details...")
        raw_data = espn_api.get_game_details(league, game_id)
        
        print(f"2. Raw data type: {type(raw_data)}")
        
        if isinstance(raw_data, dict):
            print(f"3. Raw data keys ({len(raw_data)}): {list(raw_data.keys())}")
            
            # Look for the fields we're interested in
            target_fields = ["rosters", "atBats", "winprobability", "seasonseries", 
                           "videos", "article", "againstTheSpread", "pickcenter"]
            
            print(f"\n4. Checking for target fields:")
            for field in target_fields:
                if field in raw_data:
                    data = raw_data[field]
                    print(f"   ✅ {field}: {type(data)} - {len(data) if isinstance(data, (list, dict)) else str(data)[:50]}")
                else:
                    print(f"   ❌ {field}: Not found")
        else:
            print(f"3. Raw data: {raw_data}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_current_games():
    """Test getting current games to find valid IDs"""
    print("\n=== Testing Current Games ===\n")
    
    try:
        from datetime import datetime, timedelta
        
        # Try today and last few days
        for days_back in range(7):
            test_date = datetime.now() - timedelta(days=days_back)
            date_str = test_date.strftime("%Y%m%d")
            
            print(f"Trying date {date_str}...")
            try:
                games = espn_api.get_scores("mlb", date_str)
                if games:
                    print(f"  Found {len(games)} games on {date_str}")
                    # Test first game
                    game = games[0]
                    game_id = game.get("id")
                    game_name = game.get("name", "Unknown")
                    print(f"  Testing game: {game_name} ({game_id})")
                    
                    # Get details for this game
                    details = espn_api.get_game_details("mlb", game_id)
                    print(f"  Game details keys: {list(details.keys()) if isinstance(details, dict) else type(details)}")
                    
                    return game_id, details
            except Exception as e:
                print(f"  Error with {date_str}: {e}")
                continue
        
        print("No valid games found in recent dates")
        return None, None
        
    except Exception as e:
        print(f"Error testing current games: {e}")
        return None, None

if __name__ == "__main__":
    test_direct_api()
    
    # If that fails, try with current games
    game_id, details = test_current_games()
    
    if details and isinstance(details, dict):
        print(f"\n=== Analysis of Working Game ===")
        print(f"Game ID: {game_id}")
        print(f"Total fields: {len(details)}")
        print(f"Fields: {list(details.keys())}")
