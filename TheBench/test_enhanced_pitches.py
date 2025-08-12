#!/usr/bin/env python3

import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService
from datetime import datetime

def test_enhanced_pitch_display():
    """Test the enhanced pitch display with velocity and type"""
    print("Testing enhanced pitch display...\n")
    
    try:
        # Get MLB scores for today
        scores = ApiService.get_scores('MLB', datetime.now())
        if not scores:
            print("No MLB games found for today")
            return
        
        # Get the first game with data
        game_id = None
        for score in scores[:3]:
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
        
        # Test enhanced pitch formatting
        print("\n=== ENHANCED PITCH DISPLAY TEST ===")
        
        pitch_count = 0
        for play in plays:
            play_text = play.get("text", "")
            
            if "Pitch" in play_text:
                pitch_count += 1
                
                # Extract additional pitch details
                enhanced_text = play_text
                velocity = play.get("pitchVelocity")
                pitch_type = play.get("pitchType", {})
                pitch_type_text = pitch_type.get("text", "") if isinstance(pitch_type, dict) else ""
                
                # Add velocity and pitch type if available
                if velocity and pitch_type_text:
                    enhanced_text = f"{play_text} ({velocity} mph {pitch_type_text})"
                elif velocity:
                    enhanced_text = f"{play_text} ({velocity} mph)"
                elif pitch_type_text:
                    enhanced_text = f"{play_text} ({pitch_type_text})"
                
                print(f"Original: {play_text}")
                print(f"Enhanced: {enhanced_text}")
                print()
                
                if pitch_count >= 5:  # Show first 5 enhanced pitches
                    break
        
        print(f"Enhanced {pitch_count} pitches with additional details")
    
    except Exception as e:
        print(f"Error testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_pitch_display()
