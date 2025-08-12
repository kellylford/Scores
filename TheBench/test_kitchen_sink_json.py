#!/usr/bin/env python3
"""
Test Kitchen Sink with saved JSON data
"""
import sys
import os
import json

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def test_kitchen_sink_with_saved_data():
    """Test Kitchen Sink functionality with saved JSON data"""
    print("=== Testing Kitchen Sink with Saved Data ===\n")
    
    try:
        # Load saved game data
        json_file = "api_exploration/game_details_401696639.json"
        print(f"Loading data from {json_file}...")
        
        with open(json_file, 'r') as f:
            raw_details = json.load(f)
        
        print(f"Loaded data with {len(raw_details)} top-level fields")
        
        # Test Kitchen Sink detection logic
        kitchen_sink_fields = ["rosters", "atBats", "winprobability", "seasonseries", 
                              "videos", "article", "againstTheSpread", "pickcenter"]
        
        print(f"\n1. Kitchen Sink Field Analysis:")
        found_fields = []
        for field in kitchen_sink_fields:
            has_data = bool(raw_details.get(field))
            status = "✅ FOUND" if has_data else "❌ Missing"
            print(f"   {field:15} : {status}")
            if has_data:
                found_fields.append(field)
                # Show sample data structure
                data = raw_details[field]
                if isinstance(data, list):
                    print(f"     └─ List with {len(data)} items")
                elif isinstance(data, dict):
                    keys = list(data.keys())[:3]
                    print(f"     └─ Dict with keys: {keys}...")
                else:
                    print(f"     └─ {type(data).__name__}: {str(data)[:50]}...")
        
        # Also check all available fields to see if we're missing any patterns
        print(f"\n2. All Available Fields ({len(raw_details)}):")
        for field in sorted(raw_details.keys()):
            data = raw_details[field]
            data_type = type(data).__name__
            size = len(data) if isinstance(data, (list, dict)) else "N/A"
            print(f"   {field:20} : {data_type:8} (size: {size})")
        
        # Test our _has_kitchen_sink_data logic
        would_show = len(found_fields) > 0
        print(f"\n3. Kitchen Sink Detection Result:")
        print(f"   Would show Kitchen Sink: {'YES' if would_show else 'NO'}")
        print(f"   Found {len(found_fields)} of {len(kitchen_sink_fields)} target fields")
        
        if found_fields:
            print(f"   Available features: {', '.join(found_fields)}")
            
            # Test the actual dialog creation (simulate)
            print(f"\n4. Testing Dialog Tab Creation:")
            for field in found_fields:
                data = raw_details[field]
                print(f"   Tab: {field}")
                
                if field == "rosters" and isinstance(data, dict):
                    teams = data.get("teams", [])
                    print(f"     -> Teams with rosters: {len(teams)}")
                    
                elif field == "winprobability" and isinstance(data, list):
                    print(f"     -> Win probability data points: {len(data)}")
                    if data:
                        latest = data[-1]
                        home_prob = latest.get("homeWinPercentage", "Unknown")
                        print(f"     -> Latest home win %: {home_prob}")
                
                elif field == "videos" and isinstance(data, list):
                    print(f"     -> Videos available: {len(data)}")
                    for video in data[:2]:  # Show first 2
                        title = video.get("headline", video.get("title", "Unknown"))
                        duration = video.get("duration", "Unknown")
                        print(f"       • {title} ({duration}s)")
                
                elif field == "article" and isinstance(data, dict):
                    headline = data.get("headline", "No headline")
                    print(f"     -> Article: {headline}")
                
                print()
        
        return would_show, found_fields, raw_details
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False, [], None

if __name__ == "__main__":
    would_show, found_fields, raw_data = test_kitchen_sink_with_saved_data()
    
    if would_show:
        print(f"🎉 SUCCESS: Kitchen Sink would be displayed!")
        print(f"Found {len(found_fields)} additional data sources")
    else:
        print(f"⚠️  Kitchen Sink would not be displayed")
        
        # Check if any related fields exist with different names
        if raw_data:
            print(f"\nChecking for related fields with different names...")
            keywords = ["roster", "lineup", "probability", "series", "video", 
                       "article", "spread", "pick", "bet", "odds", "win"]
            
            related_fields = []
            for field_name in raw_data.keys():
                field_lower = field_name.lower()
                for keyword in keywords:
                    if keyword in field_lower:
                        related_fields.append((field_name, keyword))
                        break
            
            if related_fields:
                print(f"Found {len(related_fields)} related fields:")
                for field_name, keyword in related_fields:
                    print(f"  • {field_name} (contains '{keyword}')")
            else:
                print("No related fields found")
