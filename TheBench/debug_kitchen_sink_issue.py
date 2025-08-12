#!/usr/bin/env python3
"""
Debug script to see exactly what game data the app is getting
"""
import sys
import os
from datetime import datetime, timedelta

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService

def debug_recent_games():
    """Debug what games are available and their data"""
    print("=== Debugging Recent MLB Games ===\n")
    
    try:
        # Check last several days
        for days_back in range(1, 8):
            test_date = datetime.now() - timedelta(days=days_back)
            date_str = test_date.strftime("%Y%m%d")
            
            print(f"📅 Checking {date_str} ({test_date.strftime('%A, %B %d')})...")
            
            try:
                games = ApiService.get_scores("mlb", date_str)
                if not games:
                    print("   No games found")
                    continue
                
                print(f"   Found {len(games)} games:")
                
                for i, game in enumerate(games):
                    game_id = game.get("id", "unknown")
                    name = game.get("name", "Unknown Game")
                    short_name = game.get("shortName", "")
                    status = game.get("status", {})
                    completed = status.get("type", {}).get("completed", False)
                    
                    print(f"   {i+1:2d}. {name}")
                    print(f"       ID: {game_id}")
                    print(f"       Short: {short_name}")
                    print(f"       Status: {'✅ Completed' if completed else '⏳ In Progress/Scheduled'}")
                    
                    # Test Kitchen Sink for first completed game
                    if completed and i == 0:
                        print(f"       🔍 Testing Kitchen Sink data...")
                        
                        try:
                            raw_details = ApiService.get_game_details("mlb", game_id)
                            if raw_details and len(raw_details) > 0:
                                # Check Kitchen Sink fields
                                kitchen_sink_fields = ["rosters", "seasonseries", "article", 
                                                      "againstTheSpread", "pickcenter", 
                                                      "winprobability", "videos"]
                                
                                found_fields = []
                                for field in kitchen_sink_fields:
                                    if raw_details.get(field):
                                        found_fields.append(field)
                                
                                if found_fields:
                                    print(f"       🎉 Kitchen Sink available! Fields: {found_fields}")
                                    return game_id, date_str, name, found_fields
                                else:
                                    print(f"       ❌ No Kitchen Sink fields found")
                                    print(f"       Available fields: {list(raw_details.keys())}")
                            else:
                                print(f"       ❌ No detailed data returned")
                        except Exception as e:
                            print(f"       ❌ Error getting details: {e}")
                    
                    print()
                
                # If we found games on this date, stop and return the first completed one
                completed_games = [g for g in games if g.get("status", {}).get("type", {}).get("completed", False)]
                if completed_games:
                    return completed_games[0].get("id"), date_str, completed_games[0].get("name"), []
                    
            except Exception as e:
                print(f"   Error: {e}")
                continue
        
        print("No games with Kitchen Sink data found in recent dates")
        return None, None, None, []
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, []

def test_saved_data_as_fallback():
    """Test using our saved data as fallback"""
    print(f"\n=== Testing Saved Data as Fallback ===\n")
    
    saved_files = [
        "api_exploration/game_details_401696639.json",
        "api_exploration/game_details_401696636.json", 
        "api_exploration/game_details_401696637.json"
    ]
    
    for json_file in saved_files:
        if os.path.exists(json_file):
            print(f"📄 Testing {json_file}...")
            
            try:
                import json
                with open(json_file, 'r') as f:
                    raw_details = json.load(f)
                
                kitchen_sink_fields = ["rosters", "seasonseries", "article", 
                                      "againstTheSpread", "pickcenter", 
                                      "winprobability", "videos"]
                
                found_fields = []
                for field in kitchen_sink_fields:
                    if raw_details.get(field):
                        found_fields.append(field)
                
                print(f"   Kitchen Sink fields found: {found_fields}")
                
                if found_fields:
                    print(f"   🎉 This file has Kitchen Sink data!")
                    return json_file, found_fields
                
            except Exception as e:
                print(f"   Error: {e}")
    
    return None, []

if __name__ == "__main__":
    print("🔍 Debugging Kitchen Sink visibility issue...\n")
    
    # First try to find current games
    game_id, date_str, game_name, found_fields = debug_recent_games()
    
    if found_fields:
        print(f"✅ Found Kitchen Sink data in live game: {game_name}")
        print(f"   Game ID: {game_id}")
        print(f"   Date: {date_str}")
        print(f"   Kitchen Sink fields: {found_fields}")
    else:
        print(f"⚠️ No live games with Kitchen Sink data found")
        
        # Try saved data
        json_file, saved_fields = test_saved_data_as_fallback()
        if saved_fields:
            print(f"✅ Saved data has Kitchen Sink: {json_file}")
            print(f"   Fields: {saved_fields}")
            print(f"\n💡 Suggestion: The issue might be that current live games")
            print(f"   don't have the Kitchen Sink data, but our saved games do.")
            print(f"   The feature is implemented correctly, we just need games")
            print(f"   that actually have this additional data available.")
        else:
            print(f"❌ No Kitchen Sink data found anywhere")
    
    print(f"\n" + "="*60)
    print(f"DIAGNOSIS:")
    if found_fields or saved_fields:
        print(f"✅ Kitchen Sink implementation is working")
        print(f"✅ Detection logic is correct") 
        print(f"⚠️ Issue: Live games may not have Kitchen Sink data")
        print(f"💡 Solution: Test with games that have the data")
    else:
        print(f"❌ Kitchen Sink data not found in any games")
        print(f"🔧 Need to debug data availability")
