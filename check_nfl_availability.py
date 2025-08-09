#!/usr/bin/env python3

import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService
from datetime import datetime, timedelta

def check_nfl_availability():
    """Check what NFL data is available"""
    print("Checking NFL data availability...\n")
    
    try:
        # Check current date
        today = datetime.now()
        print(f"Checking date: {today.strftime('%Y-%m-%d')}")
        
        # Get NFL scores for today
        scores = ApiService.get_scores('NFL', today.date())
        print(f"Found {len(scores)} NFL games for today")
        
        if not scores:
            # Try yesterday and tomorrow
            for days_offset in [-1, 1, -2, 2, -3, 3]:
                check_date = today + timedelta(days=days_offset)
                print(f"Trying {check_date.strftime('%Y-%m-%d')}...")
                scores = ApiService.get_scores('NFL', check_date.date())
                if scores:
                    print(f"Found {len(scores)} NFL games on {check_date.strftime('%Y-%m-%d')}")
                    break
        
        if not scores:
            print("No NFL games found in recent dates")
            return
        
        # Show available games
        print(f"\n=== AVAILABLE NFL GAMES ===")
        for i, game in enumerate(scores[:5], 1):
            print(f"{i}. ID: {game.get('id', 'NO ID')}")
            print(f"   Name: {game.get('name', 'NO NAME')}")
            print(f"   Short Name: {game.get('shortName', 'NO SHORT NAME')}")
            
            # Handle status safely
            status = game.get('status', {})
            if isinstance(status, dict):
                status_type = status.get('type', {})
                if isinstance(status_type, dict):
                    status_desc = status_type.get('description', 'NO STATUS')
                else:
                    status_desc = str(status_type)
            else:
                status_desc = str(status)
            print(f"   Status: {status_desc}")
            
            # Try to get details for this game
            game_id = game.get('id')
            if game_id:
                try:
                    details = ApiService.get_game_details('NFL', game_id)
                    plays = details.get("plays", [])
                    print(f"   Plays available: {len(plays)}")
                    
                    if plays:
                        # Show sample play
                        sample_play = plays[0]
                        print(f"   Sample play: {sample_play.get('text', 'NO TEXT')}")
                        print(f"   Play fields: {list(sample_play.keys())}")
                        break
                except Exception as e:
                    print(f"   Error getting details: {e}")
            print()
    
    except Exception as e:
        print(f"Error checking availability: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_nfl_availability()
