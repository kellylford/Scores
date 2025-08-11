#!/usr/bin/env python3

import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import json

def test_drive_formatting():
    """Test the new drive formatting logic with sample data"""
    
    # Sample data simulating the structure from the API
    sample_drive = {
        "id": "test_drive",
        "description": "5 plays, 22 yards, 2:30",
        "team": {
            "displayName": "Los Angeles Chargers"
        },
        "plays": [
            {
                "type": {"text": "Kickoff"},
                "text": "B.Grupe kicks 62 yards from NO 35 to LAC 3. N.Miller-Hines to LAC 36 for 33 yards (U.Amadi).",
                "clock": {"displayValue": "15:00"},
                "period": {"number": 1},
                "start": {"down": 0, "distance": 0},
                "end": {"down": 1, "distance": 10, "shortDownDistanceText": "1st & 10", "possessionText": "LAC 36"}
            },
            {
                "type": {"text": "Rush"},
                "text": "K.Vidal right tackle to LAC 39 for 3 yards (B.Bresee; K.Saunders).",
                "clock": {"displayValue": "14:54"},
                "period": {"number": 1},
                "start": {"down": 2, "distance": 7, "possessionText": "LAC 36"},
                "end": {"down": 2, "distance": 2, "shortDownDistanceText": "2nd & 2", "possessionText": "LAC 39"}
            },
            {
                "type": {"text": "Pass"},
                "text": "T.Heinicke pass incomplete deep right to T.Conklin.PENALTY on NO-C.Rumph, Defensive Offside, 5 yards, enforced at LAC 39 - No Play.",
                "clock": {"displayValue": "14:20"},
                "period": {"number": 1},
                "start": {"down": 2, "distance": 2, "possessionText": "LAC 39"},
                "end": {"down": 1, "distance": 10, "shortDownDistanceText": "1st & 10", "possessionText": "LAC 44"}
            }
        ]
    }
    
    print("=== TESTING NEW DRIVE FORMATTING ===")
    print("\nOriginal Drive:")
    print(f"Team: {sample_drive['team']['displayName']}")
    print(f"Description: {sample_drive['description']}")
    print(f"Total plays: {len(sample_drive['plays'])}")
    
    # Simulate the new separation logic
    drive_plays = []
    kickoff_plays = []
    
    for play in sample_drive["plays"]:
        play_type = play.get("type", {})
        play_type_text = play_type.get("text", "").lower()
        
        if "kickoff" in play_type_text:
            kickoff_plays.append(play)
        else:
            drive_plays.append(play)
    
    print(f"\nAfter separation:")
    print(f"Kickoff plays: {len(kickoff_plays)}")
    print(f"Drive plays: {len(drive_plays)}")
    
    print(f"\n=== KICKOFF PLAYS ===")
    for play in kickoff_plays:
        play_text = play.get("text", "Unknown play")
        clock = play.get("clock", {})
        if clock:
            clock_display = clock.get("displayValue", "")
            if clock_display:
                play_text = f"[{clock_display}] {play_text}"
        
        print(f"⚡ KICKOFF: {play_text}")
    
    print(f"\n=== DRIVE PLAYS ===")
    for play in drive_plays:
        play_text = play.get("text", "Unknown play")
        
        # Add down and distance information
        start = play.get("start", {})
        down = start.get("down", 0)
        distance = start.get("distance", 0)
        possession_text = start.get("possessionText", "")
        
        # Use pre-formatted down/distance text if available
        end = play.get("end", {})
        short_down_text = end.get("shortDownDistanceText", "")
        
        down_distance_prefix = ""
        if short_down_text:
            # Add field position context
            if possession_text:
                down_distance_prefix = f"[{short_down_text} from {possession_text}] "
            else:
                down_distance_prefix = f"[{short_down_text}] "
        elif down > 0:  # Regular downs
            if possession_text:
                down_distance_prefix = f"[{down} & {distance} from {possession_text}] "
            else:
                down_distance_prefix = f"[{down} & {distance}] "
        
        formatted_text = f"{down_distance_prefix}{play_text}"
        
        # Add clock context
        clock = play.get("clock", {})
        if clock:
            clock_display = clock.get("displayValue", "")
            if clock_display:
                formatted_text = f"[{clock_display}] {formatted_text}"
        
        print(formatted_text)
    
    print(f"\n=== EXPECTED OUTPUT STRUCTURE ===")
    print("Quarter 1")
    print("  ⚡ Kickoff")
    print("    [15:00] B.Grupe kicks 62 yards from NO 35 to LAC 3. N.Miller-Hines to LAC 36 for 33 yards (U.Amadi).")
    print("  Los Angeles Chargers: 4 plays, 22 yards, 2:30")  # Note: would be adjusted without kickoff
    print("    [14:54] [2nd & 7 from LAC 36] K.Vidal right tackle to LAC 39 for 3 yards (B.Bresee; K.Saunders).")
    print("    [14:20] [2nd & 2 from LAC 39] T.Heinicke pass incomplete deep right to T.Conklin.PENALTY on NO-C.Rumph, Defensive Offside, 5 yards, enforced at LAC 39 - No Play.")

if __name__ == "__main__":
    test_drive_formatting()
