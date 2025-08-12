#!/usr/bin/env python3
"""
Test Complete Stereo Audio Integration
======================================
Test the full stereo audio system integrated into the main application
"""

import time
from simple_audio_mapper import SimpleAudioPitchMapper

def test_stereo_integration():
    """Test the complete stereo audio integration"""
    print("Complete Stereo Audio Integration Test")
    print("=" * 50)
    
    # Initialize the main audio mapper (should auto-detect stereo support)
    mapper = SimpleAudioPitchMapper()
    
    print(f"Audio enabled: {mapper.enabled}")
    print(f"Stereo support: {mapper.use_stereo}")
    if mapper.use_stereo:
        print("✓ Using true stereo WAV audio with left/right balance")
    else:
        print("⚠ Using simple beeps with pattern-based positioning")
    
    print("\n" + "=" * 50)
    print("Testing Pitch Audio (Left to Right)")
    print("=" * 50)
    
    # Test pitch positions across the plate
    pitches = [
        (25, 100, 95, "Far Left High"),
        (85, 127, 92, "Left Center"),  
        (127, 127, 89, "Dead Center"),
        (170, 127, 91, "Right Center"),
        (230, 150, 88, "Far Right Low")
    ]
    
    for x, y, velo, desc in pitches:
        print(f"\n{desc}: ({x}, {y}) at {velo}mph")
        mapper.generate_pitch_audio(x, y, velocity=velo, pitch_type="Fastball", batter_hand='R')
        time.sleep(1.5)
    
    print("\n" + "=" * 50)
    print("Testing Strike Zone Exploration")
    print("=" * 50)
    
    # Test strike zone positions
    zones = [
        ("high_left", "High Left"),
        ("high_center", "High Center"),
        ("high_right", "High Right"),
        ("center_left", "Center Left"),
        ("center_center", "Center Center"),
        ("center_right", "Center Right"),
        ("low_left", "Low Left"),
        ("low_center", "Low Center"),
        ("low_right", "Low Right")
    ]
    
    for zone_id, zone_name in zones:
        print(f"{zone_name}...")
        mapper.generate_strike_zone_audio(zone_id, batter_hand='R')
        time.sleep(0.8)
    
    print("\n" + "=" * 50)
    print("Integration Test Complete!")
    print("=" * 50)
    
    if mapper.use_stereo:
        print("🎵 You should have heard clear left/right stereo positioning!")
        print("   The audio pans from left speaker to right speaker based on pitch location.")
    else:
        print("🔊 You heard pattern-based positioning (double beeps, long beeps, etc.)")
        print("   For true stereo, ensure wave module is available.")
    
    print("\nThis is the same audio system used in the main application.")
    print("Try: python main.py → Game Details → Right-click pitch → Explore Strike Zone")

if __name__ == "__main__":
    test_stereo_integration()
