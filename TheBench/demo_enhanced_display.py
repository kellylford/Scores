#!/usr/bin/env python3

import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService
from datetime import datetime

def demo_enhanced_display():
    """Demonstrate what enhanced play display could look like"""
    
    print("=" * 80)
    print("ENHANCED PLAY DISPLAY DEMONSTRATION")
    print("=" * 80)
    
    # NFL Enhancement Demo
    print("\n🏈 NFL - CURRENT vs ENHANCED DISPLAY")
    print("-" * 50)
    
    try:
        nfl_scores = ApiService.get_scores('NFL', datetime.now())
        if nfl_scores:
            game_id = nfl_scores[0].get('id')
            details = ApiService.get_game_details('NFL', game_id)
            drives = details.get('drives', {})
            
            if 'previous' in drives and drives['previous']:
                sample_drive = drives['previous'][0]
                plays = sample_drive.get('plays', [])
                
                print("CURRENT DISPLAY:")
                for i, play in enumerate(plays[:3]):
                    if play.get('type', {}).get('text', '').lower() == 'kickoff':
                        continue
                    
                    start = play.get('start', {})
                    down = start.get('down', 0)
                    distance = start.get('distance', 0)
                    possession = start.get('possessionText', '')
                    text = play.get('text', '')
                    clock = play.get('clock', {}).get('displayValue', '')
                    
                    if down > 0:
                        current = f"[{clock}] [{down} & {distance} from {possession}] {text}"
                        print(f"  {current}")
                        break
                
                print("\nENHANCED DISPLAY OPTIONS:")
                for i, play in enumerate(plays[:3]):
                    if play.get('type', {}).get('text', '').lower() == 'kickoff':
                        continue
                    
                    start = play.get('start', {})
                    end = play.get('end', {})
                    down = start.get('down', 0)
                    distance = start.get('distance', 0)
                    possession = start.get('possessionText', '')
                    text = play.get('text', '')
                    clock = play.get('clock', {}).get('displayValue', '')
                    stat_yardage = play.get('statYardage', 0)
                    yards_to_endzone = start.get('yardsToEndzone', 0)
                    play_type = play.get('type', {}).get('text', '')
                    
                    if down > 0:
                        # Option 1: Add yardage result
                        yardage_display = f"(+{stat_yardage})" if stat_yardage > 0 else f"({stat_yardage})" if stat_yardage < 0 else "(no gain)"
                        enhanced1 = f"[{clock}] [{down} & {distance} from {possession}] {yardage_display} {text}"
                        
                        # Option 2: Add play type icon
                        play_icon = "🏃" if "rush" in play_type.lower() or "sack" in text.lower() else "🎯" if "pass" in play_type.lower() else "🦵" if "kick" in play_type.lower() else "🏈"
                        enhanced2 = f"[{clock}] {play_icon} [{down} & {distance} from {possession}] {text}"
                        
                        # Option 3: Add situational context
                        situation = ""
                        if yards_to_endzone <= 20:
                            situation = "🔴 RED ZONE "
                        elif yards_to_endzone <= 5:
                            situation = "🎯 GOAL LINE "
                        elif down == 4:
                            situation = "⚡ 4TH DOWN "
                        
                        enhanced3 = f"[{clock}] {situation}[{down} & {distance} from {possession}] {text}"
                        
                        print(f"  Option 1 (Yardage): {enhanced1}")
                        print(f"  Option 2 (Icons):   {enhanced2}")
                        print(f"  Option 3 (Context): {enhanced3}")
                        break
    
    except Exception as e:
        print(f"NFL demo error: {e}")
    
    # MLB Enhancement Demo
    print(f"\n⚾ MLB - CURRENT vs ENHANCED DISPLAY")
    print("-" * 50)
    
    try:
        mlb_scores = ApiService.get_scores('MLB', datetime.now())
        if mlb_scores:
            game_id = mlb_scores[0].get('id')
            details = ApiService.get_game_details('MLB', game_id)
            plays = details.get('plays', [])
            
            # Find a pitch play
            pitch_play = None
            for play in plays:
                if play.get('summaryType') == 'P' and 'pitchVelocity' in play:
                    pitch_play = play
                    break
            
            if pitch_play:
                print("CURRENT DISPLAY:")
                current_text = pitch_play.get('text', 'Unknown play')
                print(f"  {current_text}")
                
                print("\nENHANCED DISPLAY OPTIONS:")
                
                # Get pitch details
                velocity = pitch_play.get('pitchVelocity', 0)
                pitch_type = pitch_play.get('pitchType', {})
                pitch_name = pitch_type.get('displayName', 'Unknown')
                pitch_count = pitch_play.get('pitchCount', {})
                balls = pitch_count.get('balls', 0)
                strikes = pitch_count.get('strikes', 0)
                outs = pitch_play.get('outs', 0)
                
                # Option 1: Add pitch details
                pitch_icon = "🔥" if "fastball" in pitch_name.lower() else "🌀" if "curve" in pitch_name.lower() else "💫" if "slider" in pitch_name.lower() else "⚾"
                enhanced1 = f"[{balls}-{strikes}] {pitch_icon} {velocity}mph {pitch_name} - {current_text}"
                
                # Option 2: Add situation context
                out_display = f"({outs} out{'s' if outs != 1 else ''})"
                enhanced2 = f"{out_display} [{balls}-{strikes}] {velocity}mph - {current_text}"
                
                # Option 3: Full context
                enhanced3 = f"{out_display} [{balls}-{strikes}] {pitch_icon} {velocity}mph {pitch_name} - {current_text}"
                
                print(f"  Option 1 (Pitch):   {enhanced1}")
                print(f"  Option 2 (Outs):    {enhanced2}")
                print(f"  Option 3 (Full):    {enhanced3}")
    
    except Exception as e:
        print(f"MLB demo error: {e}")
    
    print(f"\n🎯 IMPLEMENTATION RECOMMENDATIONS")
    print("-" * 50)
    print("1. Start with yardage display for NFL (easy win)")
    print("2. Add pitch velocity/count for MLB (fan favorite)")
    print("3. Implement play type icons for visual appeal")
    print("4. Add situational context for high-leverage moments")
    print("\nThese enhancements would significantly improve the user")
    print("experience while maintaining our accessibility focus.")

if __name__ == "__main__":
    demo_enhanced_display()
