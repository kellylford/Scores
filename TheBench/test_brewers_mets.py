#!/usr/bin/env python3
"""
Test with the specific Brewers vs Mets game to see Kitchen Sink data
"""
import sys
import os
from datetime import datetime, timedelta

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService

def find_brewers_mets_game():
    """Find the Brewers 3-2 win over Mets"""
    print("=== Finding Brewers vs Mets Game ===\n")
    
    try:
        # Go back several days to find games
        for days_back in range(1, 10):
            test_date = datetime.now() - timedelta(days=days_back)
            date_str = test_date.strftime("%Y%m%d")
            
            print(f"Checking {date_str}...")
            try:
                games = ApiService.get_scores("mlb", date_str)
                if games:
                    print(f"  Found {len(games)} games")
                    
                    # Look for Brewers vs Mets
                    for game in games:
                        name = game.get("name", "").lower()
                        short_name = game.get("shortName", "").lower()
                        
                        # Check if this could be Brewers vs Mets
                        if ("brewers" in name or "mil" in name or "milwaukee" in name) and \
                           ("mets" in name or "nym" in name or "new york" in name):
                            
                            game_id = game.get("id")
                            game_name = game.get("name", "Unknown")
                            status = game.get("status", {})
                            completed = status.get("type", {}).get("completed", False)
                            
                            print(f"  🎯 FOUND: {game_name} (ID: {game_id})")
                            print(f"     Status: {'Completed' if completed else 'In Progress/Scheduled'}")
                            
                            # Check the score if available
                            competitions = game.get("competitions", [])
                            if competitions and len(competitions) > 0:
                                comp = competitions[0]
                                competitors = comp.get("competitors", [])
                                score_info = []
                                for competitor in competitors:
                                    team = competitor.get("team", {})
                                    score = competitor.get("score", "0")
                                    abbrev = team.get("abbreviation", "")
                                    score_info.append(f"{abbrev} {score}")
                                
                                if score_info:
                                    print(f"     Score: {' - '.join(score_info)}")
                            
                            return game_id, date_str, game_name
                    
                    # Show other games for reference
                    print(f"  Other games on {date_str}:")
                    for game in games[:5]:  # Show first 5
                        print(f"    • {game.get('name', 'Unknown')}")
                    
            except Exception as e:
                print(f"  Error checking {date_str}: {e}")
                continue
        
        print("No Brewers vs Mets game found in recent dates")
        return None, None, None
        
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

def test_kitchen_sink_for_game(game_id, game_name):
    """Test Kitchen Sink detection for specific game"""
    print(f"\n=== Testing Kitchen Sink for {game_name} ===\n")
    
    try:
        print(f"Getting detailed data for game {game_id}...")
        raw_details = ApiService.get_game_details("mlb", game_id)
        
        if not raw_details or len(raw_details) == 0:
            print("❌ No detailed data returned")
            return False
        
        print(f"✅ Got data with {len(raw_details)} top-level fields")
        
        # Test Kitchen Sink detection logic (same as in app)
        kitchen_sink_fields = ["rosters", "seasonseries", "article", "againstTheSpread", 
                              "pickcenter", "winprobability", "videos"]
        
        print(f"\nKitchen Sink Field Analysis:")
        found_fields = []
        for field in kitchen_sink_fields:
            has_data = bool(raw_details.get(field))
            if has_data:
                data = raw_details[field]
                size = len(data) if isinstance(data, (list, dict)) else "N/A"
                print(f"   ✅ {field:15} : {type(data).__name__} (size: {size})")
                found_fields.append(field)
            else:
                print(f"   ❌ {field:15} : Not found")
        
        has_kitchen_sink = len(found_fields) > 0
        print(f"\nKitchen Sink Detection Result:")
        print(f"   Would show Kitchen Sink: {'YES' if has_kitchen_sink else 'NO'}")
        print(f"   Found {len(found_fields)} of {len(kitchen_sink_fields)} fields")
        
        if has_kitchen_sink:
            print(f"   🎉 Kitchen Sink would appear in game details!")
            print(f"   Available features: {', '.join(found_fields)}")
        else:
            print(f"   ⚠️ Kitchen Sink would NOT appear")
            print(f"   All available fields: {list(raw_details.keys())}")
        
        return has_kitchen_sink
        
    except Exception as e:
        print(f"Error testing game: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Find the game
    game_id, date_str, game_name = find_brewers_mets_game()
    
    if game_id:
        print(f"Found game: {game_name} on {date_str}")
        has_kitchen_sink = test_kitchen_sink_for_game(game_id, game_name)
        
        if has_kitchen_sink:
            print(f"\n✅ SUCCESS: Kitchen Sink should appear for this game!")
        else:
            print(f"\n❌ Kitchen Sink won't appear for this game")
            print(f"This might be why you're not seeing it in the app")
    else:
        print(f"\n❌ Could not find Brewers vs Mets game")
        print(f"Try checking what games are available in the app")
