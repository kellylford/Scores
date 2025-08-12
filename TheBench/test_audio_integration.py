#!/usr/bin/env python3
"""
Test Audio Integration with Game Details
========================================
"""

from simple_audio_mapper import SimpleAudioPitchMapper
from PyQt6.QtWidgets import QApplication
import sys

def test_lindor_pitch_audio():
    """Test audio for the Francisco Lindor hit-by-pitch"""
    
    app = QApplication(sys.argv)
    
    print("Testing Lindor Hit-by-Pitch Audio...")
    print("=" * 40)
    
    # Create audio mapper
    mapper = SimpleAudioPitchMapper()
    
    # Lindor's hit-by-pitch data
    x, y = 28, 199  # Low way inside 
    velocity = 94
    pitch_type = "Sinker"
    batter_hand = "R"  # Right-handed
    
    print(f"Pitch: {pitch_type} {velocity}mph to {batter_hand}HB")
    print(f"Coordinates: ({x}, {y})")
    print(f"Expected: Low way inside (should be inside to hit batter)")
    print()
    
    # Generate audio
    mapper.generate_pitch_audio(x, y, velocity, pitch_type, batter_hand)
    
    print("Audio played! You should have heard a beep representing the pitch location.")
    print("Lower frequency = lower pitch, Duration related to velocity")
    
    # Test a few more pitches for comparison
    print("\nTesting comparison pitches...")
    
    test_pitches = [
        (127, 115, 95, "Fastball", "R", "Center strike"),
        (200, 60, 88, "Slider", "R", "High inside"),
        (50, 180, 85, "Changeup", "L", "Low outside to lefty"),
    ]
    
    import time
    for x, y, velo, ptype, hand, desc in test_pitches:
        time.sleep(1)  # Pause between pitches
        print(f"\n{desc}: {ptype} ({x},{y})")
        mapper.generate_pitch_audio(x, y, velo, ptype, hand)
    
    print("\nAudio test complete!")

if __name__ == "__main__":
    test_lindor_pitch_audio()
