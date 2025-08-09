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

def investigate_nfl_data():
    """Investigate NFL play-by-play data structure"""
    print("Investigating NFL play-by-play data...\n")
    
    try:
        # Get NFL scores for today
        scores = ApiService.get_scores('NFL', datetime.now())
        if not scores:
            print("No NFL games found for today")
            return
        
        # Get the first game with data
        game_id = None
        for score in scores[:3]:
            if score.get("id"):
                game_id = score.get("id")
                print(f"Investigating game: {score.get('shortName', 'Unknown')}")
                break
        
        if not game_id:
            print("No valid game IDs found")
            return
        
        # Get game details
        details = ApiService.get_game_details('NFL', game_id)
        plays = details.get("plays", [])
        
        if not plays:
            print("No plays data found")
            return
        
        print(f"Found {len(plays)} total plays")
        
        # Analyze NFL play structure
        print("\n=== NFL PLAY STRUCTURE ANALYSIS ===")
        
        # Look at first 20 plays
        for i, play in enumerate(plays[:20], 1):
            print(f"\n--- Play {i} ---")
            print(f"Text: {play.get('text', 'NO TEXT')}")
            
            # Period information
            period = play.get('period', {})
            print(f"Period: {period.get('number', 'N/A')} ({period.get('displayValue', 'N/A')})")
            
            # Down and distance
            print(f"Type: {play.get('type', {}).get('text', 'N/A')}")
            
            # Team
            team = play.get('team', {})
            print(f"Team ID: {team.get('id', 'N/A')}")
            
            # Score
            print(f"Score: {play.get('awayScore', 'N/A')} - {play.get('homeScore', 'N/A')}")
            
            # Look for drive information
            if 'drive' in play:
                drive = play['drive']
                print(f"Drive: {drive}")
            
            # Look for down/distance
            for key in ['down', 'distance', 'yardLine', 'driveNumber']:
                if key in play:
                    print(f"{key}: {play[key]}")
            
            # Show other interesting fields
            for key, value in play.items():
                if key not in ['text', 'period', 'type', 'team', 'awayScore', 'homeScore', 'id', 'sequenceNumber']:
                    print(f"{key}: {value}")
        
        # Analyze by period
        print(f"\n=== PERIOD DISTRIBUTION ===")
        period_counts = {}
        
        for play in plays:
            period = play.get('period', {})
            period_display = period.get('displayValue', 'Unknown')
            period_counts[period_display] = period_counts.get(period_display, 0) + 1
        
        for period, count in sorted(period_counts.items()):
            print(f"{period}: {count} plays")
        
        # Look for drive organization
        print(f"\n=== DRIVE ANALYSIS ===")
        drives = {}
        
        for play in plays:
            drive_num = play.get('driveNumber', 'Unknown')
            if drive_num not in drives:
                drives[drive_num] = []
            drives[drive_num].append(play)
        
        print(f"Found {len(drives)} drives:")
        for drive_num, drive_plays in list(drives.items())[:5]:  # Show first 5 drives
            if drive_plays:
                first_play = drive_plays[0]
                last_play = drive_plays[-1]
                team = first_play.get('team', {}).get('id', 'Unknown')
                print(f"Drive {drive_num} (Team {team}): {len(drive_plays)} plays")
                print(f"  First: {first_play.get('text', 'NO TEXT')}")
                if len(drive_plays) > 1:
                    print(f"  Last: {last_play.get('text', 'NO TEXT')}")
    
    except Exception as e:
        print(f"Error investigating: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_nfl_data()
