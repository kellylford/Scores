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

def investigate_pitch_details():
    """Investigate what additional pitch data ESPN provides"""
    print("Investigating pitch-level details...\n")
    
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
                print(f"Investigating game: {score.get('shortName', 'Unknown')}")
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
        
        # Look for pitch-specific data
        print("\n=== PITCH DETAIL ANALYSIS ===")
        
        pitch_count = 0
        for play in plays[:50]:  # Check first 50 plays
            play_text = play.get("text", "")
            
            # Focus on actual pitch plays
            if "Pitch" in play_text:
                pitch_count += 1
                print(f"\n--- Pitch {pitch_count} ---")
                print(f"Text: {play_text}")
                
                # Show all available fields
                print("Available fields:")
                for key, value in play.items():
                    if key not in ["text", "id", "sequenceNumber"]:
                        print(f"  {key}: {value}")
                
                # Check for detailed pitch information
                if pitch_count >= 5:  # Limit output
                    break
        
        print(f"\n=== COMPREHENSIVE FIELD ANALYSIS ===")
        # Look at different types of plays to see what fields are available
        play_types = {}
        
        for play in plays[:100]:
            play_type = play.get("type", "unknown")
            if play_type not in play_types:
                play_types[play_type] = []
            play_types[play_type].append(play)
        
        print(f"Found {len(play_types)} play types:")
        for play_type, plays_of_type in play_types.items():
            print(f"\n{play_type}: {len(plays_of_type)} plays")
            if plays_of_type:
                sample_play = plays_of_type[0]
                print(f"  Sample text: {sample_play.get('text', 'NO TEXT')}")
                print(f"  Available fields: {list(sample_play.keys())}")
                
                # Look for velocity, pitch type, etc.
                for key, value in sample_play.items():
                    if any(keyword in key.lower() for keyword in 
                           ["velocity", "speed", "mph", "type", "pitch", "ball", "strike"]):
                        print(f"    {key}: {value}")
    
    except Exception as e:
        print(f"Error investigating: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_pitch_details()
