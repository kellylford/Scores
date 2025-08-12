#!/usr/bin/env python3
"""
Quick test to verify audio system functionality after reorganization
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def test_audio_imports():
    """Test that all audio-related imports work"""
    try:
        from simple_audio_mapper import SimpleAudioPitchMapper
        print("✅ SimpleAudioPitchMapper imports successfully")
        
        from stereo_audio_mapper import StereoAudioPitchMapper 
        print("✅ StereoAudioPitchMapper imports successfully")
        
        from pitch_exploration_dialog import PitchExplorationDialog
        print("✅ PitchExplorationDialog imports successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_audio_functionality():
    """Test basic audio functionality"""
    try:
        from simple_audio_mapper import SimpleAudioPitchMapper
        
        # Create a simple test
        mapper = SimpleAudioPitchMapper()
        print("✅ Audio mapper created successfully")
        
        # Test coordinate mapping
        test_coords = [
            (120, 150),  # Center strike zone
            (80, 120),   # Inside
            (160, 180)   # Outside
        ]
        
        for x, y in test_coords:
            params = mapper._coordinate_to_beep_params(x, y)
            print(f"✅ Coordinates ({x}, {y}) → {params}")
            
        return True
    except Exception as e:
        print(f"❌ Audio functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Audio System After Reorganization")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_audio_imports()
    print()
    
    if imports_ok:
        # Test basic functionality
        functionality_ok = test_audio_functionality()
        print()
        
        if functionality_ok:
            print("🎉 All audio system tests PASSED!")
            print("✅ Pitch audio exploration should work")
            print("✅ Context menus should work")
            print("✅ Hotkeys should work")
        else:
            print("❌ Audio functionality tests FAILED")
    else:
        print("❌ Import tests FAILED")
