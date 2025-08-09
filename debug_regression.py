#!/usr/bin/env python3
"""
Debug what's happening with the game details - compare before and after changes
"""
import sys
import os
from datetime import datetime, timedelta

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService

def debug_game_details_regression():
    """Debug why we lost game details"""
    print("=== Debugging Game Details Regression ===\n")
    
    # Constants from the app
    DETAIL_FIELDS = ["boxscore", "plays", "leaders", "standings", "odds", "injuries", "broadcasts", "news", "gameInfo"]
    
    # Test with demo data first
    print("1. Testing Demo Game Logic...")
    
    # Simulate demo game detection
    league = "mlb"
    game_id = "DEMO_KITCHEN_SINK"
    
    if game_id == "DEMO_KITCHEN_SINK" and league == "mlb":
        print("   ✅ Demo game detected")
        
        # Try to load demo data
        import json
        json_file = os.path.join(ROOT_DIR, "api_exploration", "game_details_401696639.json")
        
        if os.path.exists(json_file):
            print(f"   ✅ Loading demo data from {json_file}")
            with open(json_file, 'r') as f:
                raw_details = json.load(f)
            
            print(f"   ✅ Raw details loaded: {len(raw_details)} fields")
            print(f"   Top-level fields: {list(raw_details.keys())}")
            
        else:
            print(f"   ❌ Demo file not found: {json_file}")
            raw_details = {}
    else:
        print("   ❌ Demo game not detected")
        raw_details = {}
    
    # Test the new logic
    print(f"\n2. Testing New _add_configurable_details Logic...")
    
    all_available_fields = []
    
    # Check all possible detail fields and add them if they have data
    for field in DETAIL_FIELDS:
        value = raw_details.get(field)
        has_data = False
        
        # Replicate the _check_field_has_data logic
        if field == "standings" and isinstance(value, (list, dict)):
            has_data = len(value) > 0 if isinstance(value, list) else bool(value.get("entries"))
        elif field == "leaders" and isinstance(value, dict):
            has_data = len(value) > 0
        elif field == "boxscore" and isinstance(value, dict):
            has_data = bool(value.get("teams") or value.get("players"))
        elif field == "plays" and isinstance(value, list):
            has_data = len(value) > 0
        elif field == "injuries" and isinstance(value, list):
            has_data = len(value) > 0
        elif field == "news" and isinstance(value, (list, dict)):
            has_data = len(value) > 0 if isinstance(value, list) else bool(value.get("articles"))
        else:
            has_data = bool(value)  # Generic check
        
        if has_data:
            all_available_fields.append(field)
            print(f"   ✅ {field}: Has data ({type(value).__name__})")
        else:
            print(f"   ❌ {field}: No data or empty")
    
    # Always add Kitchen Sink for ALL MLB games
    if league == "mlb":
        all_available_fields.append("kitchensink")
        print(f"   ✅ kitchensink: Forced for MLB")
    
    # Always include plays if available (even if empty)
    if raw_details.get("plays") and "plays" not in all_available_fields:
        all_available_fields.append("plays")
        print(f"   ✅ plays: Added even if empty")
    
    print(f"\n3. Results:")
    print(f"   Total fields that would show: {len(all_available_fields)}")
    print(f"   Fields: {all_available_fields}")
    
    # Find a real game to test
    print(f"\n4. Looking for Real Brewers vs Mets Game...")
    
    for days_back in range(1, 10):
        test_date = datetime.now() - timedelta(days=days_back)
        date_str = test_date.strftime("%Y%m%d")
        
        try:
            games = ApiService.get_scores("mlb", date_str)
            if games:
                for game in games:
                    name = game.get("name", "").lower()
                    if ("brewers" in name or "mil" in name) and ("mets" in name or "nym" in name):
                        game_id = game.get("id")
                        print(f"   🎯 Found: {game.get('name')} (ID: {game_id}) on {date_str}")
                        
                        # Test this game
                        try:
                            real_details = ApiService.get_game_details("mlb", game_id)
                            print(f"   Raw details for real game: {len(real_details)} fields")
                            print(f"   Real game fields: {list(real_details.keys())}")
                            
                            return raw_details, real_details, all_available_fields
                        except Exception as e:
                            print(f"   Error getting real game details: {e}")
                        
                        break
        except:
            continue
    
    print("   ❌ No real Brewers vs Mets game found")
    return raw_details, {}, all_available_fields

if __name__ == "__main__":
    demo_data, real_data, expected_fields = debug_game_details_regression()
    
    print(f"\n" + "="*60)
    print(f"DIAGNOSIS:")
    print(f"Expected fields to show: {len(expected_fields)}")
    print(f"Fields: {expected_fields}")
    
    if "kitchensink" in expected_fields:
        print(f"✅ Kitchen Sink should appear")
    else:
        print(f"❌ Kitchen Sink missing from fields")
    
    if len(expected_fields) < 16:
        print(f"⚠️  Field count is low - might have lost some fields")
        print(f"Check the _check_field_has_data logic")
    
    print(f"\nSuggested fixes:")
    print(f"1. Make sure all existing fields still show")
    print(f"2. Ensure Kitchen Sink is always added for MLB")
    print(f"3. Don't break existing functionality")
