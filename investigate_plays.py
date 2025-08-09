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

def investigate_play_data():
    """Investigate the structure of play-by-play data"""
    print("Investigating play-by-play data structure...\n")
    
    try:
        # Get MLB scores for today
        scores = ApiService.get_scores('MLB', datetime.now())
        if not scores:
            print("No MLB games found for today")
            return
        
        # Get the first game with data
        game_id = None
        for score in scores[:3]:  # Check first 3 games
            if score.get("id"):
                game_id = score.get("id")
                print(f"Checking game: {score.get('shortName', 'Unknown')}")
                break
        
        if not game_id:
            print("No valid game IDs found")
            return
        
        # Get game details
        details = ApiService.get_game_details('MLB', game_id)
        plays = details.get("plays", [])
        
        if not plays:
            print("No plays data found")
            return
        
        print(f"Found {len(plays)} total plays\n")
        
        # Analyze a sample of plays to understand the data structure
        print("=== SAMPLE PLAYS ANALYSIS ===")
        
        for i, play in enumerate(plays[:10]):  # First 10 plays
            print(f"\n--- Play {i+1} ---")
            print(f"Text: {play.get('text', 'NO TEXT')}")
            
            # Period information
            period = play.get('period', {})
            print(f"Period Number: {period.get('number', 'NO NUMBER')}")
            print(f"Period Display: {period.get('displayValue', 'NO DISPLAY')}")
            print(f"Period Type: {period.get('type', 'NO TYPE')}")
            
            # Participants
            participants = play.get('participants', [])
            print(f"Participants: {len(participants)}")
            for j, participant in enumerate(participants):
                role = participant.get('role', 'NO ROLE')
                athlete = participant.get('athlete', {})
                name = athlete.get('displayName', 'NO NAME')
                print(f"  {j+1}. Role: {role}, Name: {name}")
            
            # Other fields
            print(f"Scoring Play: {play.get('scoringPlay', False)}")
            print(f"Away Score: {play.get('awayScore', 'N/A')}")
            print(f"Home Score: {play.get('homeScore', 'N/A')}")
            
            # Show all available keys for first play
            if i == 0:
                print(f"\nAll available keys in play data:")
                for key in sorted(play.keys()):
                    print(f"  - {key}")
        
        # Analyze period distribution
        print(f"\n=== PERIOD DISTRIBUTION ===")
        period_counts = {}
        unknown_periods = 0
        
        for play in plays:
            period = play.get('period', {})
            period_type = period.get('type', 'Unknown')
            period_display = period.get('displayValue', 'Unknown')
            
            key = f"{period_display} - {period_type}"
            period_counts[key] = period_counts.get(key, 0) + 1
            
            if period_type == 'Unknown' or period_display == 'Unknown':
                unknown_periods += 1
        
        print(f"Period distribution:")
        for period, count in sorted(period_counts.items()):
            print(f"  {period}: {count} plays")
        
        print(f"\nUnknown periods: {unknown_periods} out of {len(plays)} plays")
        
        # Show a few "unknown" plays
        if unknown_periods > 0:
            print(f"\n=== SAMPLE UNKNOWN PLAYS ===")
            unknown_count = 0
            for play in plays:
                period = play.get('period', {})
                if period.get('type', 'Unknown') == 'Unknown' or period.get('displayValue', 'Unknown') == 'Unknown':
                    print(f"Unknown play: {play.get('text', 'NO TEXT')}")
                    print(f"  Full period data: {period}")
                    unknown_count += 1
                    if unknown_count >= 5:  # Show first 5 unknown plays
                        break
    
    except Exception as e:
        print(f"Error investigating plays: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_play_data()
