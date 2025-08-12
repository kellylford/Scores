#!/usr/bin/env python3

import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService
from datetime import datetime
import json

def test_drive_display_logic():
    """Test the exact drive display logic that would be used in the app"""
    
    # Get the Chicago vs Miami game
    scores = ApiService.get_scores('NFL', datetime.now())
    game_id = None
    for score in scores[:5]:
        teams = score.get('name', 'Unknown game')
        if 'chicago' in teams.lower() and 'miami' in teams.lower():
            game_id = score.get('id')
            break
    
    if not game_id:
        print("No Chicago vs Miami game found")
        return
    
    print(f'Testing drive logic for game {game_id}')
    details = ApiService.get_game_details('NFL', game_id)
    drives_data = details.get('drives', {})
    
    # Get the first drive (most recent is at index 0, so we want the last one)
    previous_drives = drives_data.get('previous', [])
    if not previous_drives:
        print("No previous drives found")
        return
    
    # The FIRST drive of the game would be the LAST in the previous_drives list
    first_drive = previous_drives[-1]  # Last entry = first drive chronologically
    
    print(f'\nFirst drive of game:')
    print(f'Team: {first_drive.get("team", {}).get("displayName", "Unknown")}')
    print(f'Description: {first_drive.get("description", "Unknown")}')
    
    plays = first_drive.get('plays', [])
    print(f'Total plays: {len(plays)}')
    
    # Separate kickoffs from regular drive plays (same logic as in the app)
    drive_plays = []
    kickoff_plays = []
    
    for play in plays:
        play_type = play.get("type", {})
        play_type_text = play_type.get("text", "").lower()
        
        if "kickoff" in play_type_text:
            kickoff_plays.append(play)
        else:
            drive_plays.append(play)
    
    print(f'\nAfter separation:')
    print(f'Kickoffs: {len(kickoff_plays)}')
    print(f'Drive plays: {len(drive_plays)}')
    
    print(f'\n=== KICKOFF PLAYS ===')
    for i, play in enumerate(kickoff_plays):
        print(f'Kickoff {i+1}: {play.get("text", "No text")}')
    
    print(f'\n=== DRIVE PLAYS (as they would appear in app) ===')
    for i, play in enumerate(drive_plays):
        play_text = play.get("text", "Unknown play")
        
        # Use the EXACT same logic as in the fixed app
        down_distance_prefix = ""
        start = play.get("start", {})
        
        # For display, we want to show the situation at the START of the play
        down = start.get("down", 0)
        distance = start.get("distance", 0)
        possession_text = start.get("possessionText", "")
        
        # Use start data for down/distance display (not end!)
        if down > 0:  # Regular downs
            if possession_text:
                down_distance_prefix = f"[{down} & {distance} from {possession_text}] "
            else:
                down_distance_prefix = f"[{down} & {distance}] "
        
        formatted_play = f"{down_distance_prefix}{play_text}"
        
        print(f'Play {i+1}: {formatted_play}')
        print(f'   Raw start: down={down}, distance={distance}, possession="{possession_text}"')
        print()

if __name__ == "__main__":
    test_drive_display_logic()
