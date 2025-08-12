#!/usr/bin/env python3
"""
Test the audio pitch mapping system
"""

import sys
import os

# Add the project root to the path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

try:
    from audio_pitch_mapper import AudioPitchMapper
    print("✅ Audio mapper imported successfully")
except ImportError as e:
    print(f"❌ Failed to import audio mapper: {e}")
    sys.exit(1)

def test_audio_mapping():
    """Test the audio mapping with sample pitch data"""
    print("\n🎵 Testing Audio Pitch Mapping System")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Create audio mapper
    mapper = AudioPitchMapper()
    
    # Test with Francisco Lindor's hit-by-pitch
    print("\n🎯 Test 1: Francisco Lindor Hit-by-Pitch")
    print("Coordinates: (28, 199) - Should be Low Way Inside to RHB")
    mapper.generate_pitch_audio(28, 199, 94, "Sinker", "R")
    
    # Test with a center strike
    print("\n🎯 Test 2: Center Strike Zone")
    print("Coordinates: (127, 115) - Should be center")
    mapper.generate_pitch_audio(127, 115, 95, "Four-Seam Fastball", "R")
    
    # Test with outside corner to lefty
    print("\n🎯 Test 3: Outside to Left-handed Batter")
    print("Coordinates: (80, 140) - Should be outside to LHB") 
    mapper.generate_pitch_audio(80, 140, 88, "Slider", "L")
    
    print("\n🎵 Audio tests initiated. Listen for spatial audio...")
    print("   - Inside pitches should be panned left")
    print("   - Outside pitches should be panned right") 
    print("   - High pitches should have higher frequency")
    print("   - Low pitches should have lower frequency")
    
    # Keep app running for audio playback
    QTimer.singleShot(5000, app.quit)  # Quit after 5 seconds
    app.exec()
    
    print("\n✅ Audio test completed!")

if __name__ == "__main__":
    test_audio_mapping()
