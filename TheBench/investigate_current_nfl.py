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

def investigate_current_nfl():
    """Investigate current NFL drive issue"""
    
    # Get NFL scores for today
    scores = ApiService.get_scores('NFL', datetime.now())
    print('NFL Games today:')
    
    game_id = None
    for score in scores[:5]:
        teams = score.get('name', 'Unknown game')
        print(f'- {teams} (ID: {score.get("id", "N/A")})')
        if 'chicago' in teams.lower() and 'miami' in teams.lower():
            print(f'  *** FOUND CHICAGO vs MIAMI GAME: {score.get("id")} ***')
            game_id = score.get('id')
            break
    
    if not game_id and scores:
        # Use first available game if Chicago/Miami not found
        game_id = scores[0].get('id')
        print(f'Using first available game: {game_id}')
    
    if not game_id:
        print('No games found')
        return
    
    print(f'\nGetting details for game {game_id}...')
    details = ApiService.get_game_details('NFL', game_id)
    drives_data = details.get('drives', {})
    
    print(f'Drives data structure:')
    print(f'- Current drive: {"current" in drives_data}')
    print(f'- Previous drives: {len(drives_data.get("previous", []))} drives')
    
    # Look at the first drive
    previous_drives = drives_data.get('previous', [])
    if previous_drives:
        first_drive = previous_drives[0]  # Most recent is first
        print(f'\nFirst drive details:')
        print(f'Team: {first_drive.get("team", {}).get("displayName", "Unknown")}')
        print(f'Description: {first_drive.get("description", "Unknown")}')
        
        plays = first_drive.get('plays', [])
        print(f'Number of plays: {len(plays)}')
        
        print(f'\nFirst 3 plays in detail:')
        for i, play in enumerate(plays[:3]):
            print(f'Play {i+1}:')
            print(f'  Type: {play.get("type", {}).get("text", "Unknown")}')
            print(f'  Text: {play.get("text", "No text")}')
            
            start = play.get('start', {})
            end = play.get('end', {})
            
            # Print start details
            start_down = start.get("down", "?")
            start_distance = start.get("distance", "?")
            start_possession = start.get("possessionText", "?")
            start_yards_to_endzone = start.get("yardsToEndzone", "?")
            start_yard_line = start.get("yardLine", "?")
            
            print(f'  Start: down={start_down}, distance={start_distance}, possessionText="{start_possession}", yardsToEndzone={start_yards_to_endzone}, yardLine={start_yard_line}')
            
            # Print end details
            end_down = end.get("down", "?")
            end_distance = end.get("distance", "?")
            end_possession = end.get("possessionText", "?")
            end_short_down = end.get("shortDownDistanceText", "?")
            end_yards_to_endzone = end.get("yardsToEndzone", "?")
            end_yard_line = end.get("yardLine", "?")
            
            print(f'  End: down={end_down}, distance={end_distance}, possessionText="{end_possession}", shortDownDistanceText="{end_short_down}", yardsToEndzone={end_yards_to_endzone}, yardLine={end_yard_line}')
            print()

if __name__ == "__main__":
    investigate_current_nfl()
