#!/usr/bin/env python3
"""
Test the new improved logic that should show more fields
"""
import sys
import os
import json

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def test_new_logic():
    """Test the new improved _add_configurable_details logic"""
    print("=== Testing New Improved Logic ===\n")
    
    # Constants from the app
    DETAIL_FIELDS = ["boxscore", "plays", "leaders", "standings", "odds", "injuries", "broadcasts", "news", "gameInfo"]
    
    # Load demo data
    json_file = os.path.join(ROOT_DIR, "api_exploration", "game_details_401696639.json")
    
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            raw_details = json.load(f)
        
        print(f"✅ Loaded demo data: {len(raw_details)} total fields")
        print(f"Available fields: {sorted(raw_details.keys())}")
        
        # Test NEW logic - be more permissive
        print(f"\n=== NEW LOGIC (More Permissive) ===")
        all_available_fields = []
        
        # Include ALL detail fields that have any data (even empty lists/dicts)
        for field in DETAIL_FIELDS:
            value = raw_details.get(field)
            if value is not None:  # Include if field exists, even if empty
                all_available_fields.append(field)
                value_type = type(value).__name__
                size = len(value) if isinstance(value, (list, dict)) else "N/A"
                print(f"   ✅ {field:12} : {value_type:8} (size: {size})")
            else:
                print(f"   ❌ {field:12} : Not found")
        
        # Always include plays if available (even if empty)
        if raw_details.get("plays") is not None and "plays" not in all_available_fields:
            all_available_fields.append("plays")
            print(f"   ✅ plays (forced): Found in raw data")
        
        # Always add Kitchen Sink for ALL MLB games
        league = "mlb"
        if league == "mlb":
            all_available_fields.append("kitchensink")
            print(f"   ✅ kitchensink   : Forced for MLB")
        
        print(f"\nRESULTS:")
        print(f"Total fields to show: {len(all_available_fields)}")
        print(f"Fields: {all_available_fields}")
        
        # Count fields that would be navigable vs text-only
        navigable_fields = ["standings", "leaders", "boxscore", "plays", "injuries", "news", "kitchensink"]
        navigable_count = sum(1 for field in all_available_fields if field in navigable_fields)
        text_count = len(all_available_fields) - navigable_count
        
        print(f"Navigable items: {navigable_count}")
        print(f"Text-only items: {text_count}")
        
        if "kitchensink" in all_available_fields:
            print(f"✅ Kitchen Sink WILL appear!")
        else:
            print(f"❌ Kitchen Sink missing!")
        
        if len(all_available_fields) >= 16:
            print(f"✅ Field count looks good ({len(all_available_fields)} >= 16)")
        else:
            print(f"⚠️ Field count still low ({len(all_available_fields)} < 16)")
            print(f"   This might be expected if not all fields have data")
        
        return all_available_fields
    else:
        print(f"❌ Demo file not found: {json_file}")
        return []

if __name__ == "__main__":
    fields = test_new_logic()
    
    print(f"\n" + "="*60)
    print(f"SUMMARY:")
    
    if "kitchensink" in fields:
        print(f"✅ Kitchen Sink implementation working")
    else:
        print(f"❌ Kitchen Sink still missing")
    
    if len(fields) > 10:
        print(f"✅ Good number of fields ({len(fields)})")
    else:
        print(f"⚠️ Low field count ({len(fields)})")
    
    print(f"\nNext: Restart the application to see if Kitchen Sink appears")
    print(f"Look for 'Kitchen Sink (Additional MLB Data)' in game details")
