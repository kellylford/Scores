#!/usr/bin/env python3
"""
Test Strike Zone Left-Right Positioning
=======================================
Test script specifically for strike zone left/right audio positioning
"""

import time
from simple_audio_mapper import SimpleAudioPitchMapper

def test_strike_zone_positioning():
    """Test the left-right positioning in strike zone exploration"""
    print("Strike Zone Left-Right Positioning Test")
    print("=" * 50)
    
    mapper = SimpleAudioPitchMapper()
    if not mapper.enabled:
        print("Audio system not available - install winsound or run on Windows")
        return
    
    print(f"Audio enabled: {mapper.enabled}")
    print(f"Stereo support: {mapper.use_stereo}")
    
    if mapper.use_stereo:
        print("✓ Using true stereo WAV audio - you should hear clear left/right positioning")
    else:
        print("⚠ Using pattern-based positioning - listen for different beep patterns")
    
    print("\n" + "=" * 50)
    print("Testing Left-Center-Right Progression")
    print("=" * 50)
    
    # Test just left-center-right to clearly demonstrate positioning
    horizontal_zones = [
        ('center_left', 'Center Left (X=50) - Should be LEFT audio'),
        ('center_center', 'Center Center (X=127) - Should be CENTER audio'),
        ('center_right', 'Center Right (X=205) - Should be RIGHT audio')
    ]
    
    for zone_id, description in horizontal_zones:
        print(f"\n{description}")
        mapper.generate_strike_zone_audio(zone_id, batter_hand='R')
        time.sleep(2.0)  # Longer pause to clearly distinguish
    
    print("\n" + "=" * 50)
    print("Testing All 9 Strike Zone Positions")
    print("=" * 50)
    
    # Test all 9 positions in logical order
    all_zones = [
        ('high_left', 'High Left'),
        ('high_center', 'High Center'),
        ('high_right', 'High Right'),
        ('center_left', 'Center Left'),
        ('center_center', 'Center Center'),
        ('center_right', 'Center Right'),
        ('low_left', 'Low Left'),
        ('low_center', 'Low Center'),
        ('low_right', 'Low Right')
    ]
    
    for zone_id, zone_name in all_zones:
        print(f"{zone_name}...")
        mapper.generate_strike_zone_audio(zone_id, batter_hand='R')
        time.sleep(1.2)
    
    print("\n" + "=" * 50)
    print("Test Complete!")
    print("=" * 50)
    
    if mapper.use_stereo:
        print("🎵 You should have heard clear left/right stereo positioning!")
        print("   - Left positions: Audio in left speaker/headphone")
        print("   - Center positions: Audio in both speakers equally")
        print("   - Right positions: Audio in right speaker/headphone")
    else:
        print("🔊 You heard pattern-based positioning:")
        print("   - Left positions: Double beeps (two quick beeps)")
        print("   - Center positions: Single beeps")
        print("   - Right positions: Long beeps (extended duration)")
    
    print("\nThe strike zone exploration now uses wider coordinates:")
    print("   - Left zones: X=50 (was X=85)")
    print("   - Right zones: X=205 (was X=170)")
    print("   - This provides much clearer left/right separation!")

if __name__ == "__main__":
    test_strike_zone_positioning()
