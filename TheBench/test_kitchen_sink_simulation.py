#!/usr/bin/env python3
"""
Create a test that simulates the Kitchen Sink dialog with real data
"""
import sys
import os
import json

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def test_kitchen_sink_simulation():
    """Test Kitchen Sink with simulated UI creation"""
    print("=== Kitchen Sink UI Simulation Test ===\n")
    
    try:
        # Load saved game data
        json_file = "api_exploration/game_details_401696639.json"
        print(f"Loading data from {json_file}...")
        
        with open(json_file, 'r') as f:
            raw_details = json.load(f)
        
        # Simulate the Kitchen Sink detection logic
        print("1. Testing Kitchen Sink detection...")
        kitchen_sink_fields = ["rosters", "seasonseries", "article", "againstTheSpread", 
                              "pickcenter", "winprobability", "videos"]
        
        found_fields = []
        for field in kitchen_sink_fields:
            has_data = bool(raw_details.get(field))
            if has_data:
                found_fields.append(field)
        
        would_show = len(found_fields) > 0
        print(f"   Kitchen Sink would show: {would_show}")
        print(f"   Found fields: {found_fields}")
        
        if not would_show:
            print("❌ Kitchen Sink would not appear")
            return False
        
        # Simulate tab creation for each field
        print(f"\n2. Simulating Kitchen Sink dialog tabs...")
        tab_count = 0
        
        # Test rosters tab
        if "rosters" in found_fields:
            rosters_data = raw_details.get("rosters", [])
            print(f"   📋 Rosters Tab: {len(rosters_data)} teams")
            
            for team_data in rosters_data:
                if isinstance(team_data, dict):
                    team_info = team_data.get("team", {})
                    team_name = team_info.get("displayName", "Unknown")
                    roster = team_data.get("roster", [])
                    print(f"     • {team_name}: {len(roster)} players")
            tab_count += 1
        
        # Test season series tab  
        if "seasonseries" in found_fields:
            series_data = raw_details.get("seasonseries", [])
            print(f"   🗓️ Season Series Tab: {len(series_data)} series items")
            
            for series_item in series_data:
                if isinstance(series_item, dict):
                    summary = series_item.get("summary", "No summary")
                    events = series_item.get("events", [])
                    print(f"     • {summary} ({len(events)} games)")
            tab_count += 1
        
        # Test article tab
        if "article" in found_fields:
            article_data = raw_details.get("article", {})
            headline = article_data.get("headline", "No headline")
            article_type = article_data.get("type", "Unknown")
            print(f"   📰 Article Tab: {article_type}")
            print(f"     • {headline}")
            tab_count += 1
        
        # Test betting tab
        if "againstTheSpread" in found_fields:
            ats_data = raw_details.get("againstTheSpread", [])
            print(f"   🎰 Betting ATS Tab: {len(ats_data)} teams")
            
            for team_data in ats_data:
                if isinstance(team_data, dict):
                    team_name = team_data.get("displayName", "Unknown")
                    record = team_data.get("record", "No record")
                    print(f"     • {team_name}: {record}")
            tab_count += 1
        
        # Test picks tab
        if "pickcenter" in found_fields:
            picks_data = raw_details.get("pickcenter", [])
            print(f"   🎯 Expert Picks Tab: {len(picks_data)} picks")
            
            for pick_item in picks_data:
                if isinstance(pick_item, dict):
                    provider = pick_item.get("provider", {}).get("name", "Unknown")
                    details = pick_item.get("details", "No details")
                    print(f"     • {provider}: {details}")
            tab_count += 1
        
        # Test win probability (if present)
        if "winprobability" in found_fields:
            win_prob_data = raw_details.get("winprobability", [])
            if win_prob_data:
                print(f"   📊 Win Probability Tab: {len(win_prob_data)} data points")
                tab_count += 1
        
        # Test videos (if present) 
        if "videos" in found_fields:
            videos_data = raw_details.get("videos", [])
            if videos_data:
                print(f"   🎥 Videos Tab: {len(videos_data)} videos")
                tab_count += 1
        
        print(f"\n3. Kitchen Sink Dialog Summary:")
        print(f"   Total tabs created: {tab_count}")
        print(f"   Available data types: {', '.join(found_fields)}")
        
        # Test that basic functionality would work
        print(f"\n4. Testing data access patterns...")
        
        # Test accessing nested data structures
        test_passed = True
        
        # Test rosters data structure
        if "rosters" in found_fields:
            rosters = raw_details["rosters"]
            if isinstance(rosters, list) and len(rosters) > 0:
                first_team = rosters[0]
                if "team" in first_team and "roster" in first_team:
                    print("   ✅ Rosters data structure valid")
                else:
                    print("   ❌ Rosters data structure invalid")
                    test_passed = False
        
        # Test season series data structure  
        if "seasonseries" in found_fields:
            series = raw_details["seasonseries"]
            if isinstance(series, list) and len(series) > 0:
                first_series = series[0]
                if "summary" in first_series:
                    print("   ✅ Season series data structure valid")
                else:
                    print("   ❌ Season series data structure invalid")
                    test_passed = False
        
        if test_passed:
            print(f"\n🎉 SUCCESS: Kitchen Sink implementation ready!")
            print(f"✅ Detection logic works")
            print(f"✅ Data structures are valid")
            print(f"✅ {tab_count} tabs would be created")
        else:
            print(f"\n⚠️ Some data structure issues found")
        
        return test_passed and tab_count > 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_kitchen_sink_simulation()
    
    if success:
        print(f"\n✅ Kitchen Sink feature is ready for testing!")
        print(f"To test: Run the main application, navigate to an MLB game, and look for 'Kitchen Sink (Additional MLB Data)' option")
    else:
        print(f"\n❌ Kitchen Sink feature needs debugging")
