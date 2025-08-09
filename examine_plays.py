#!/usr/bin/env python3
"""
Examine play structure to understand ESPN data format
"""

import sys
import os
from datetime import datetime
import json

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService

def examine_play_structure():
    """Examine the structure of play data"""
    try:
        # Get current MLB games
        scores = ApiService.get_scores('MLB', datetime.now())
        
        if not scores:
            print("No MLB games found for today")
            return
            
        # Test first game with available data
        for game in scores:
            game_id = game.get('id')
            if not game_id:
                continue
                
            print(f"\nExamining game: {game.get('shortName', 'Unknown')}")
            
            # Get game details
            details = ApiService.get_game_details('MLB', game_id)
            plays_data = details.get('plays', [])
            
            if not plays_data:
                print("  No plays data available")
                continue
                
            print(f"  Found {len(plays_data)} plays")
            
            # Examine first few plays in detail
            for i, play in enumerate(plays_data[:5]):
                print(f"\n  Play {i+1}:")
                print(f"    Text: {play.get('text', 'Unknown')}")
                print(f"    Period: {json.dumps(play.get('period', {}), indent=6)}")
                
                participants = play.get('participants', [])
                if participants:
                    print(f"    Participants:")
                    for p in participants[:2]:  # Show first 2
                        role = p.get('role', 'unknown')
                        athlete = p.get('athlete', {})
                        name = athlete.get('displayName', 'Unknown')
                        print(f"      {role}: {name}")
                
                if play.get('scoringPlay', False):
                    print(f"    SCORING PLAY: {play.get('awayScore', 0)}-{play.get('homeScore', 0)}")
            
            # Test with first game only
            break
            
    except Exception as e:
        print(f"Error examining plays: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    examine_play_structure()
