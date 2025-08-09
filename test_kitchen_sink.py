#!/usr/bin/env python3
"""
Test script to verify Kitchen Sink functionality and data detection
"""
import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService

def test_kitchen_sink_detection():
    """Test if Kitchen Sink data is detected correctly"""
    print("=== Testing Kitchen Sink Data Detection ===\n")
    
    try:
        # Use a known game ID from our previous analysis
        league = "mlb"
        game_id = "401696639"  # Game we analyzed earlier
        game_name = "Pirates vs Reds (from analysis)"
        
        print(f"1. Testing with known game: {game_name} (ID: {game_id})")
        
        # Get detailed game data
        print("2. Getting detailed game data...")
        raw_details = ApiService.get_game_details(league, game_id)
        
        # Test Kitchen Sink detection
        kitchen_sink_fields = ["rosters", "atBats", "winprobability", "seasonseries", 
                              "videos", "article", "againstTheSpread", "pickcenter"]
        
        print("\n3. Kitchen Sink Field Analysis:")
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
                    print(f"     └─ Dict with keys: {list(data.keys())[:3]}...")
                else:
                    print(f"     └─ {type(data).__name__}: {str(data)[:50]}...")
        
        print(f"\n4. Kitchen Sink Detection Result:")
        would_show = len(found_fields) > 0
        print(f"   Would show Kitchen Sink option: {'YES' if would_show else 'NO'}")
        print(f"   Found {len(found_fields)} of {len(kitchen_sink_fields)} fields")
        
        if found_fields:
            print(f"   Available features: {', '.join(found_fields)}")
            
            # Test some specific fields in detail
            print(f"\n5. Detailed Field Analysis:")
            for field in found_fields[:3]:  # Test first 3 found fields
                test_specific_field_data(field, raw_details)
        
        return would_show, found_fields
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def test_specific_field_data(field_name, raw_details):
    """Test specific field data structure"""
    data = raw_details.get(field_name)
    if not data:
        print(f"\n❌ No {field_name} data found")
        return
    
    print(f"\n✅ {field_name.upper()} Data Analysis:")
    
    if field_name == "rosters" and isinstance(data, dict):
        teams = data.get("teams", [])
        print(f"   Teams with rosters: {len(teams)}")
        for team in teams:
            team_name = team.get("team", {}).get("displayName", "Unknown")
            roster_size = len(team.get("roster", []))
            print(f"   - {team_name}: {roster_size} players")
    
    elif field_name == "winprobability" and isinstance(data, list):
        print(f"   Total data points: {len(data)}")
        if data:
            latest = data[-1]
            home_prob = latest.get("homeWinPercentage", "Unknown")
            print(f"   Latest home win probability: {home_prob}%")
    
    elif field_name == "seasonseries" and isinstance(data, dict):
        summary = data.get("summary", "No summary")
        events = data.get("events", [])
        print(f"   Series summary: {summary}")
        print(f"   Games in series: {len(events)}")
    
    elif field_name == "videos" and isinstance(data, list):
        print(f"   Available videos: {len(data)}")
        for i, video in enumerate(data[:3]):  # Show first 3
            title = video.get("headline", video.get("title", f"Video {i+1}"))
            duration = video.get("duration", "Unknown")
            print(f"   - {title} ({duration}s)")
    
    elif field_name == "article" and isinstance(data, dict):
        headline = data.get("headline", "No headline")
        article_type = data.get("type", "Unknown")
        word_count = len(data.get("story", "").split()) if data.get("story") else 0
        print(f"   Headline: {headline}")
        print(f"   Type: {article_type}")
        print(f"   Word count: {word_count}")

if __name__ == "__main__":
    print("Kitchen Sink Test Script")
    print("=" * 50)
    
    would_show, found_fields = test_kitchen_sink_detection()
    
    if would_show:
        print(f"\n🎉 SUCCESS: Kitchen Sink would be displayed!")
        print(f"Found {len(found_fields)} additional data sources")
    else:
        print(f"\n⚠️  Kitchen Sink would not be displayed")
        print("No additional MLB data found in this game")
    
    print("\n" + "=" * 50)
    print("Kitchen Sink test completed!")
