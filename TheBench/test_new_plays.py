#!/usr/bin/env python3

import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService
from datetime import datetime

def test_new_play_organization():
    """Test the new play organization structure"""
    print("Testing new play-by-play organization...\n")
    
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
                print(f"Testing with game: {score.get('shortName', 'Unknown')}")
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
        
        print(f"Found {len(plays)} total plays")
        
        # Simulate the new organization logic
        print("\n=== NEW ORGANIZATION STRUCTURE ===")
        
        # Filter plays for one inning to show structure
        inning_plays = []
        for play in plays:
            period = play.get('period', {})
            if (period.get('number') == 1 and 
                period.get('type', '').lower() == 'top'):
                inning_plays.append(play)
        
        print(f"\nTop 1st Inning plays ({len(inning_plays)} plays):")
        
        # Group by at-bat
        at_bats = []
        current_at_bat = None
        
        for play in inning_plays:
            play_text = play.get("text", "")
            
            # Skip empty or transition plays
            if not play_text.strip():
                continue
            
            print(f"  Processing: {play_text}")
            
            # Check if this is a batter announcement
            if " pitches to " in play_text:
                if current_at_bat:
                    at_bats.append(current_at_bat)
                    print(f"    -> Ended previous at-bat")
                
                parts = play_text.split(" pitches to ")
                if len(parts) >= 2:
                    batter_name = parts[1].strip()
                    current_at_bat = {
                        "batter": batter_name,
                        "plays": [],
                        "result": None
                    }
                    print(f"    -> Started new at-bat for {batter_name}")
                continue
            
            # Add to current at-bat
            if current_at_bat:
                current_at_bat["plays"].append(play)
                print(f"    -> Added to {current_at_bat['batter']}'s at-bat")
                
                # Check for result
                if any(outcome in play_text.lower() for outcome in 
                       ["struck out", "grounded out", "flied out", "singled", "walked"]):
                    current_at_bat["result"] = play_text
                    at_bats.append(current_at_bat)
                    print(f"    -> Result found: {play_text}")
                    current_at_bat = None
                else:
                    # Check name matching
                    batter_name = current_at_bat["batter"]
                    name_words = batter_name.split()
                    name_found_in_play = any(name_part.lower() in play_text.lower() 
                                           for name_part in name_words if len(name_part) > 2)
                    if name_found_in_play:
                        current_at_bat["result"] = play_text
                        at_bats.append(current_at_bat)
                        print(f"    -> Result found by name match: {play_text}")
                        current_at_bat = None
        
        # Add remaining at-bat
        if current_at_bat:
            if current_at_bat["plays"] and not current_at_bat["result"]:
                current_at_bat["result"] = current_at_bat["plays"][-1].get("text", "In progress")
            at_bats.append(current_at_bat)
        
        print(f"\n=== FINAL STRUCTURE ({len(at_bats)} at-bats) ===")
        for i, at_bat in enumerate(at_bats, 1):
            if at_bat["batter"] and at_bat["result"]:
                print(f"{i}. {at_bat['batter']}: {at_bat['result']}")
                print(f"   Pitch details: ({len(at_bat['plays'])} plays)")
                for j, play in enumerate(at_bat["plays"][:3], 1):  # Show first 3
                    play_text = play.get("text", "")
                    if play_text != at_bat["result"]:
                        print(f"     {j}. {play_text}")
                if len(at_bat["plays"]) > 3:
                    print(f"     ... and {len(at_bat['plays']) - 3} more")
                print()
    
    except Exception as e:
        print(f"Error testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_play_organization()
