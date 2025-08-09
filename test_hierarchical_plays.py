#!/usr/bin/env python3
"""
Test script to verify hierarchical play-by-play structure
"""

import sys
import os
from datetime import datetime

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService

def test_plays_structure():
    """Test the hierarchical organization of plays data"""
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
                
            print(f"\nTesting game: {game.get('shortName', 'Unknown')}")
            
            # Get game details
            details = ApiService.get_game_details('MLB', game_id)
            plays_data = details.get('plays', [])
            
            if not plays_data:
                print("  No plays data available")
                continue
                
            print(f"  Found {len(plays_data)} plays")
            
            # Analyze structure for hierarchical organization
            inning_groups = {}
            for play in plays_data:
                period_info = play.get("period", {})
                period_number = period_info.get("number", 0)
                period_display = period_info.get("displayValue", f"Period {period_number}")
                
                if period_display not in inning_groups:
                    inning_groups[period_display] = {"top": [], "bottom": []}
                
                inning_half = "bottom" if period_info.get("type") == "2" else "top"
                inning_groups[period_display][inning_half].append(play)
            
            print(f"  Organized into {len(inning_groups)} periods/innings:")
            for period, data in sorted(inning_groups.items()):
                top_count = len(data["top"])
                bottom_count = len(data["bottom"])
                print(f"    {period}: {top_count} top, {bottom_count} bottom")
                
                # Show sample plays from first inning
                if period == sorted(inning_groups.keys())[0]:
                    print("    Sample plays:")
                    for i, play in enumerate(data["top"][:3]):
                        print(f"      Top {i+1}: {play.get('text', 'Unknown')[:60]}...")
                    for i, play in enumerate(data["bottom"][:3]):
                        print(f"      Bottom {i+1}: {play.get('text', 'Unknown')[:60]}...")
            
            # Test with first game only
            break
            
    except Exception as e:
        print(f"Error testing plays structure: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_plays_structure()
