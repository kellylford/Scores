#!/usr/bin/env python3
"""
Find the specific pitch with coordinates (144, 207) and analyze the discrepancy
"""

import espn_api
import json

def find_pitch_144_207():
    """Find and analyze the pitch with coordinates (144, 207)"""
    
    game_details = espn_api.get_game_details('MLB', '401696689')
    plays = game_details['plays']
    
    print("=== SEARCHING FOR PITCH (144, 207) ===")
    
    found = False
    total_pitches = 0
    
    for i, play in enumerate(plays):
        if 'pitchCoordinate' in play:
            total_pitches += 1
            coord = play['pitchCoordinate']
            
            if isinstance(coord, dict):
                x, y = coord.get('x'), coord.get('y')
                
                if x == 144 and y == 207:
                    print(f"\n🎯 FOUND TARGET PITCH!")
                    print(f"Play #{i} (Pitch #{total_pitches} in game)")
                    print(f"Play text: {play.get('text', '')}")
                    print(f"Coordinates: ({x}, {y})")
                    
                    # Get additional pitch details
                    pitch_type = play.get('pitchType', {})
                    pitch_velocity = play.get('pitchVelocity', {})
                    team = play.get('team', {})
                    pitch_num = play.get('atBatPitchNumber', '')
                    
                    print(f"Pitch type: {pitch_type}")
                    print(f"Velocity: {pitch_velocity}")
                    print(f"Team: {team}")
                    print(f"At-bat pitch number: {pitch_num}")
                    
                    # Now analyze the coordinate interpretation
                    analyze_coordinate_discrepancy(x, y, play)
                    found = True
                    break
    
    if not found:
        print(f"\n❌ Pitch (144, 207) not found among {total_pitches} total pitches")
        print("\nSample coordinates found:")
        
        sample_count = 0
        for play in plays:
            if 'pitchCoordinate' in play and sample_count < 10:
                coord = play['pitchCoordinate']
                if isinstance(coord, dict):
                    x, y = coord.get('x'), coord.get('y')
                    print(f"  ({x}, {y}) - {play.get('text', '')[:50]}...")
                    sample_count += 1

def analyze_coordinate_discrepancy(x, y, play):
    """Analyze the discrepancy between coordinates and description"""
    
    print(f"\n=== COORDINATE ANALYSIS ===")
    print(f"Coordinates: X={x}, Y={y}")
    
    # Based on our understanding of the coordinate system:
    # X: 50-205 range, strike zone ~100-155
    # Y: 80-200 range, strike zone ~80-200
    
    # Horizontal analysis
    if x < 50:
        x_desc = "Way inside (very far left)"
    elif x < 100:
        x_desc = "Inside (left of strike zone)"
    elif x <= 155:
        x_desc = "Strike zone width"
        if x < 120:
            x_desc += " (left side)"
        elif x > 135:
            x_desc += " (right side)"
        else:
            x_desc += " (center)"
    elif x <= 205:
        x_desc = "Outside (right of strike zone)"
    else:
        x_desc = "Way outside (very far right)"
    
    # Vertical analysis  
    if y < 80:
        y_desc = "High (above strike zone)"
    elif y <= 200:
        y_desc = "Strike zone height"
        if y < 120:
            y_desc += " (upper)"
        elif y > 160:
            y_desc += " (lower)"
        else:
            y_desc += " (middle)"
    else:
        y_desc = "Low (below strike zone)"
    
    print(f"X={x}: {x_desc}")
    print(f"Y={y}: {y_desc}")
    
    # Check the user's claim
    user_claim = "Low Far Left"
    print(f"\n=== DISCREPANCY ANALYSIS ===")
    print(f"User reported: '{user_claim}'")
    print(f"Coordinates suggest: '{y_desc} {x_desc}'")
    
    # Analysis
    print(f"\n=== FINDINGS ===")
    
    if y == 207:
        print(f"✅ Y=207 confirms 'Low' - pitch is below strike zone")
    
    if x == 144:
        print(f"❓ X=144 suggests center-right of strike zone, NOT 'far left'")
        print(f"   'Far left' would typically be X < 100")
        print(f"   X=144 is actually in the strike zone horizontally")
    
    # Possible explanations
    print(f"\n=== POSSIBLE EXPLANATIONS ===")
    print(f"1. Coordinate system interpretation error in display code")
    print(f"2. Data entry error in ESPN's system")
    print(f"3. Different coordinate system than we understand")
    print(f"4. Display logic incorrectly mapping coordinates to descriptions")
    
    # Let's check what our audio system would say
    print(f"\n=== AUDIO SYSTEM INTERPRETATION ===")
    from simple_audio_mapper import SimpleAudioPitchMapper
    
    try:
        mapper = SimpleAudioPitchMapper()
        beep_params = mapper._coordinate_to_beep_params(x, y)
        freq, duration, balance, zone = beep_params
        
        print(f"Audio frequency: {freq} Hz")
        print(f"Stereo balance: {balance} (0.0=left, 0.5=center, 1.0=right)")
        
        if balance < 0.3:
            audio_horizontal = "Left"
        elif balance > 0.7:
            audio_horizontal = "Right"  
        else:
            audio_horizontal = "Center"
            
        print(f"Audio system would place this: {audio_horizontal}")
        
        if x == 144 and balance > 0.5:
            print(f"🤔 INCONSISTENCY: X=144 gives right-leaning audio, but user says 'far left'")
            
    except Exception as e:
        print(f"Could not test audio system: {e}")

if __name__ == "__main__":
    find_pitch_144_207()
