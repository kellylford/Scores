#!/usr/bin/env python3

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import ApiService

def test_simple_kitchen_sink():
    """Simple test to see Kitchen Sink logic"""
    
    print("=== Simple Kitchen Sink Test ===")
    
    # Test with demo data - this should have Kitchen Sink
    demo_file = "api_exploration/game_details_401696636.json"
    
    if os.path.exists(demo_file):
        import json
        with open(demo_file, 'r') as f:
            demo_data = json.load(f)
            
        print(f"Loaded demo data from {demo_file}")
        
        # Test Kitchen Sink logic like in the app
        league = "mlb"  # This should be lowercase like in the app
        
        print(f"League: {league}")
        print(f"League == 'mlb': {league == 'mlb'}")
        
        # Check if Kitchen Sink would be added
        all_available_fields = []
        
        # This is the exact logic from the app
        if league == "mlb":
            all_available_fields.append("kitchensink")
            print("✓ Kitchen Sink would be added!")
        else:
            print("✗ Kitchen Sink would NOT be added")
        
        print(f"Available fields: {all_available_fields}")
        
        # Check demo data for Kitchen Sink fields
        kitchen_sink_fields = ["rosters", "seasonseries", "article", "againstTheSpread", 
                              "pickcenter", "winprobability", "videos"]
        
        found_fields = []
        for field in kitchen_sink_fields:
            if demo_data.get(field):
                found_fields.append(field)
        
        print(f"Demo data has Kitchen Sink fields: {found_fields}")
        
        if found_fields:
            print("✓ Demo data has Kitchen Sink data!")
        else:
            print("✗ Demo data lacks Kitchen Sink data")
    else:
        print(f"Demo file {demo_file} not found")

if __name__ == "__main__":
    test_simple_kitchen_sink()
