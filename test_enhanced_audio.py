#!/usr/bin/env python3
"""
Test Enhanced Audio Features
============================
Test script for the improved spatial audio pitch mapping system
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Import our audio mapper
from simple_audio_mapper import SimpleAudioPitchMapper

def test_stereo_balance():
    """Test stereo balance feature"""
    print("Testing stereo balance...")
    
    mapper = SimpleAudioPitchMapper()
    if not mapper.enabled:
        print("Audio system not available - skipping balance test")
        return
    
    # Test pitches across the plate (left to right)
    test_pitches = [
        (50, 127, "Far Left"),      # Far left side
        (85, 127, "Left"),          # Left side  
        (127, 127, "Center"),       # Dead center
        (170, 127, "Right"),        # Right side
        (205, 127, "Far Right")     # Far right side
    ]
    
    for x, y, desc in test_pitches:
        print(f"\nTesting {desc} pitch at ({x}, {y})")
        mapper.generate_pitch_audio(x, y, velocity=90, pitch_type="Test", batter_hand='R')
        time.sleep(1.0)

def test_strike_zone_exploration():
    """Test strike zone exploration feature"""
    print("\nTesting strike zone exploration...")
    
    mapper = SimpleAudioPitchMapper()
    if not mapper.enabled:
        print("Audio system not available - skipping zone test")
        return
    
    # Test all 9 zone positions
    zones = [
        "high_left", "high_center", "high_right",
        "center_left", "center_center", "center_right", 
        "low_left", "low_center", "low_right"
    ]
    
    for zone in zones:
        print(f"Playing {zone.replace('_', ' ').title()} strike zone...")
        mapper.generate_strike_zone_audio(zone, batter_hand='R')
        time.sleep(0.9)

def test_sequence_timing():
    """Test faster pitch sequence timing"""
    print("\nTesting faster sequence timing...")
    
    mapper = SimpleAudioPitchMapper()
    if not mapper.enabled:
        print("Audio system not available - skipping sequence test")
        return
    
    # Simulate a 4-pitch at-bat
    pitches = [
        (100, 120, 93, "Fastball"),    # Ball outside
        (140, 140, 89, "Slider"),      # Strike inside
        (120, 100, 91, "Fastball"),    # Foul high
        (130, 160, 85, "Changeup")     # Strike low
    ]
    
    print("Playing 4-pitch sequence with 0.8s delays...")
    for i, (x, y, velo, ptype) in enumerate(pitches):
        print(f"  Pitch {i+1}: {ptype} {velo}mph at ({x},{y})")
        mapper.generate_pitch_audio(x, y, velocity=velo, pitch_type=ptype, batter_hand='R')
        if i < len(pitches) - 1:  # Don't delay after last pitch
            time.sleep(0.8)  # Reduced timing to match our update

def main():
    """Run all enhanced audio tests"""
    print("Enhanced Audio Feature Test")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    try:
        # Test 1: Stereo balance
        test_stereo_balance()
        
        # Test 2: Strike zone exploration  
        test_strike_zone_exploration()
        
        # Test 3: Faster sequence timing
        test_sequence_timing()
        
        print("\n" + "=" * 40)
        print("All audio tests completed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
    
    # Keep app running briefly then exit
    QTimer.singleShot(2000, app.quit)
    app.exec()

if __name__ == "__main__":
    main()
