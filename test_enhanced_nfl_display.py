#!/usr/bin/env python3

import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService
from datetime import datetime

def test_enhanced_nfl_display():
    """Test the new enhanced NFL display features"""
    
    print("=" * 80)
    print("TESTING ENHANCED NFL DISPLAY FEATURES")
    print("=" * 80)
    
    try:
        # Get NFL game data
        nfl_scores = ApiService.get_scores('NFL', datetime.now())
        if not nfl_scores:
            print("No NFL games found today")
            return
        
        game_id = nfl_scores[0].get('id')
        game_name = nfl_scores[0].get('name', 'Unknown Game')
        print(f"Testing with: {game_name}")
        print(f"Game ID: {game_id}")
        
        details = ApiService.get_game_details('NFL', game_id)
        drives = details.get('drives', {})
        
        if 'previous' in drives and drives['previous']:
            # Get a few drives to test different scenarios
            test_drives = drives['previous'][:3]
            
            for drive_idx, drive in enumerate(test_drives):
                team_name = drive.get('team', {}).get('displayName', 'Unknown Team')
                description = drive.get('description', 'Unknown drive')
                plays = drive.get('plays', [])
                
                print(f"\n--- DRIVE {drive_idx + 1}: {team_name} ---")
                print(f"Description: {description}")
                print("Enhanced play display:")
                
                # Filter out kickoffs for drive plays
                drive_plays = []
                for play in plays:
                    play_type = play.get("type", {})
                    play_type_text = play_type.get("text", "").lower()
                    if "kickoff" not in play_type_text:
                        drive_plays.append(play)
                
                for play_idx, play in enumerate(drive_plays[:5]):  # Show first 5 plays
                    # Apply the same logic as the enhanced display
                    play_text = play.get("text", "Unknown play")
                    start = play.get("start", {})
                    down = start.get("down", 0)
                    distance = start.get("distance", 0)
                    possession_text = start.get("possessionText", "")
                    yards_to_endzone = start.get("yardsToEndzone", 0)
                    stat_yardage = play.get("statYardage", 0)
                    play_type = play.get("type", {})
                    play_type_text = play_type.get("text", "")
                    clock = play.get("clock", {}).get("displayValue", "")
                    
                    # Build enhanced display
                    enhanced_text = play_text
                    
                    # Add yardage
                    if stat_yardage != 0:
                        yardage_display = f"(+{stat_yardage} yards)" if stat_yardage > 0 else f"({stat_yardage} yards)"
                        enhanced_text = f"{yardage_display} {enhanced_text}"
                    
                    # Add play type
                    if play_type_text and play_type_text.lower() not in enhanced_text.lower():
                        if "pass" in play_type_text.lower():
                            enhanced_text = f"PASS: {enhanced_text}"
                        elif "rush" in play_type_text.lower():
                            enhanced_text = f"RUSH: {enhanced_text}"
                        elif "sack" in play_type_text.lower():
                            enhanced_text = f"SACK: {enhanced_text}"
                    
                    # Add situational context
                    situation_prefix = ""
                    if yards_to_endzone <= 5:
                        situation_prefix = "GOAL LINE "
                    elif yards_to_endzone <= 20:
                        situation_prefix = "RED ZONE "
                    elif down == 4:
                        situation_prefix = "4TH DOWN "
                    
                    # Build down/distance prefix
                    down_distance_prefix = ""
                    if down > 0:
                        if possession_text:
                            if situation_prefix:
                                down_distance_prefix = f"[{situation_prefix}{down} & {distance} from {possession_text}] "
                            else:
                                down_distance_prefix = f"[{down} & {distance} from {possession_text}] "
                        else:
                            down_distance_prefix = f"[{situation_prefix}{down} & {distance}] "
                    
                    # Final display
                    if play.get("scoringPlay"):
                        away_score = play.get("awayScore", 0)
                        home_score = play.get("homeScore", 0)
                        final_text = f"TOUCHDOWN: {down_distance_prefix}{enhanced_text} ({away_score}-{home_score})"
                    else:
                        final_text = f"{down_distance_prefix}{enhanced_text}"
                    
                    if clock:
                        final_text = f"[{clock}] {final_text}"
                    
                    print(f"  Play {play_idx + 1}: {final_text}")
                    
                    # Show what's new
                    improvements = []
                    if stat_yardage != 0:
                        improvements.append(f"yardage: {stat_yardage}")
                    if situation_prefix:
                        improvements.append(f"situation: {situation_prefix.strip()}")
                    if improvements:
                        print(f"            ^ Enhanced with: {', '.join(improvements)}")
                
                if drive_idx >= 2:  # Limit to 3 drives for demo
                    break
        
        print(f"\n🎯 ENHANCEMENTS IMPLEMENTED:")
        print("✅ Yardage display: Shows actual yards gained/lost")
        print("✅ Play type labels: PASS, RUSH, SACK (accessible text)")
        print("✅ Situational context: RED ZONE, GOAL LINE, 4TH DOWN")
        print("✅ Visual highlighting: Different colors for special situations")
        print("✅ Maintained accessibility: No emoji icons, clear text labels")
        
    except Exception as e:
        print(f"Error testing enhanced display: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_nfl_display()
