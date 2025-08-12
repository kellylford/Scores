#!/usr/bin/env python3
"""
Test Left-Right Audio Patterns
==============================
Test script specifically for left-right audio positioning
"""

import time
from simple_audio_mapper import SimpleAudioPitchMapper

def test_left_right_patterns():
    """Test the left-right audio patterns with clear feedback"""
    print("Testing Left-Right Audio Patterns")
    print("=" * 40)
    
    mapper = SimpleAudioPitchMapper()
    if not mapper.enabled:
        print("Audio system not available - install winsound or run on Windows")
        return
    
    # Test extreme positions with clear labels
    test_positions = [
        (25, 127, "Far Left (x=25)"),      # Should be balance ~0.1 - double beep
        (85, 127, "Left (x=85)"),          # Should be balance ~0.33 - single beep  
        (127, 127, "Center (x=127)"),      # Should be balance ~0.5 - single beep
        (170, 127, "Right (x=170)"),       # Should be balance ~0.67 - single beep
        (230, 127, "Far Right (x=230)")    # Should be balance ~0.9 - long beep
    ]
    
    for x, y, label in test_positions:
        print(f"\nTesting: {label}")
        
        # Get the calculated parameters
        freq, dur, balance, desc = mapper._coordinate_to_beep_params(x, y, 90, "Test", 'R')
        balance_desc = mapper._get_balance_description(balance)
        
        print(f"  Balance: {balance:.3f}")
        print(f"  Expected: {balance_desc}")
        print("  Playing audio...")
        
        # Play the audio
        mapper.generate_pitch_audio(x, y, velocity=90, pitch_type="Test", batter_hand='R')
        
        # Wait before next test
        time.sleep(2.0)
    
    print("\n" + "=" * 40)
    print("Test complete!")
    print("You should have heard:")
    print("1. Far Left: Double beep (two quick beeps)")
    print("2. Left: Single beep")
    print("3. Center: Single beep") 
    print("4. Right: Single beep")
    print("5. Far Right: Long beep (extended duration)")

if __name__ == "__main__":
    test_left_right_patterns()
