#!/usr/bin/env python3

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json

def test_team_extraction():
    """Test team nickname extraction from demo data"""
    
    print("=== Team Nickname Extraction Test ===")
    
    # Load demo data
    demo_file = "api_exploration/game_details_401696636.json"
    
    if os.path.exists(demo_file):
        with open(demo_file, 'r') as f:
            demo_data = json.load(f)
            
        print(f"Loaded demo data from {demo_file}")
        
        # Check header structure for team info
        if 'header' in demo_data:
            competitors = demo_data['header'].get('competitions', [{}])[0].get('competitors', [])
            print(f"Found {len(competitors)} competitors")
            
            for i, competitor in enumerate(competitors):
                team = competitor.get('team', {})
                home_away = competitor.get('homeAway', 'unknown')
                print(f"  {i}: {home_away} - {team.get('name', 'Unknown')} ({team.get('abbreviation', 'N/A')})")
        
        # Check if plays are available for testing
        plays = demo_data.get('plays', [])
        print(f"Found {len(plays)} plays")
        
        if plays:
            first_play = plays[0]
            print(f"First play: {first_play.get('text', 'No text')}")
            
            # Check for participants
            participants = first_play.get('participants', [])
            print(f"First play participants: {len(participants)}")
            for participant in participants:
                p_type = participant.get('type', 'unknown')
                athlete = participant.get('athlete', {})
                print(f"  - {p_type}: {athlete.get('shortName', 'N/A')}")
    else:
        print(f"Demo file {demo_file} not found")

if __name__ == "__main__":
    test_team_extraction()
