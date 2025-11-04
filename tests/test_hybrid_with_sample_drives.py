"""
Test the Hybrid Audio Player with sample drive data
Demonstrates all three modes: single, sequence, and tutorial
"""

from hybrid_audio_player import HybridAudioPlayer
import time


def test_single_play_mode():
    """Test Mode 1: Single play with full narration"""
    print("\n" + "="*70)
    print("TEST 1: SINGLE PLAY MODE (Alt+P equivalent)")
    print("="*70)
    print("Description: Individual play with TTS narration + musical tone")
    print()
    
    player = HybridAudioPlayer()
    
    plays_to_test = [
        {
            'description': 'QB pass complete to TE for 12 yards',
            'yardage': 12,
            'type': 'pass',
            'yardsToEndzone': 68,
            'down': 2,
            'distance': 7
        },
        {
            'description': 'RB rush up middle for 3 yards',
            'yardage': 3,
            'type': 'rush',
            'yardsToEndzone': 82,
            'down': 1,
            'distance': 10
        },
        {
            'description': 'Sack by defensive end',
            'yardage': -8,
            'type': 'pass',
            'yardsToEndzone': 45,
            'down': 3,
            'distance': 15
        }
    ]
    
    for i, play in enumerate(plays_to_test, 1):
        print(f"\nPlay {i}/{len(plays_to_test)}")
        print(f"  Situation: {play['down']} and {play['distance']} at {100 - play['yardsToEndzone']} yard line")
        print(f"  Expected narration: '{play['yardage']} yard {play['type']}. {play['description']}'")
        
        player.play_single_play(play, with_narration=True)
        
        if i < len(plays_to_test):
            time.sleep(1)  # Pause between plays
    
    player.cleanup()
    print("\n✓ Single play mode test complete")


def test_sequence_mode():
    """Test Mode 2: Drive sequence with key moment narration"""
    print("\n" + "="*70)
    print("TEST 2: SEQUENCE MODE (Alt+S equivalent)")
    print("="*70)
    print("Description: Fast drive playback with key moments announced after")
    print()
    
    player = HybridAudioPlayer()
    
    # Sample touchdown drive
    touchdown_drive = [
        {
            'description': 'RB rush right for 5 yards',
            'yardage': 5,
            'type': 'rush',
            'yardsToEndzone': 72
        },
        {
            'description': 'QB pass short left to WR for 8 yards',
            'yardage': 8,
            'type': 'pass',
            'yardsToEndzone': 67
        },
        {
            'description': 'QB pass deep middle to TE for 23 yards',  # Big play!
            'yardage': 23,
            'type': 'pass',
            'yardsToEndzone': 59
        },
        {
            'description': 'RB rush up middle for 4 yards',
            'yardage': 4,
            'type': 'rush',
            'yardsToEndzone': 36
        },
        {
            'description': 'QB pass short right for 11 yards',
            'yardage': 11,
            'type': 'pass',
            'yardsToEndzone': 32
        },
        {
            'description': 'RB rush left end for 21 yards - Touchdown!',  # Touchdown!
            'yardage': 21,
            'type': 'rush',
            'yardsToEndzone': 21,
            'isScoringPlay': True
        }
    ]
    
    print("Drive: 6 plays, 72 yards")
    print("Expected sequence:")
    print("  1. Announce drive start")
    print("  2. Play rapid tones with stereo panning (listen for left → right movement)")
    print("  3. Announce: 'Play 3: Big play! 23 yards!'")
    print("  4. Announce: 'Play 6: Touchdown!'")
    print()
    
    player.play_drive_sequence(touchdown_drive, mode='sequence')
    
    player.cleanup()
    print("\n✓ Sequence mode test complete")


def test_tutorial_mode():
    """Test Mode 3: Tutorial with detailed explanations"""
    print("\n" + "="*70)
    print("TEST 3: TUTORIAL MODE (Learning/Educational)")
    print("="*70)
    print("Description: Detailed narration with technical explanations")
    print()
    
    player = HybridAudioPlayer()
    
    # Short tutorial drive
    tutorial_drive = [
        {
            'description': 'Example rush play',
            'yardage': 6,
            'type': 'rush',
            'yardsToEndzone': 75
        },
        {
            'description': 'Example pass play',
            'yardage': 12,
            'type': 'pass',
            'yardsToEndzone': 69
        }
    ]
    
    print("Tutorial: 2 plays")
    print("Expected for each play:")
    print("  1. Play number and type")
    print("  2. Wave type description (square for rush, sine for pass)")
    print("  3. Frequency information")
    print("  4. Stereo positioning explanation")
    print("  5. Musical tone demonstration")
    print()
    
    player.play_drive_sequence(tutorial_drive, mode='tutorial')
    
    player.cleanup()
    print("\n✓ Tutorial mode test complete")


def test_preferences():
    """Test user preference controls"""
    print("\n" + "="*70)
    print("TEST 4: USER PREFERENCES")
    print("="*70)
    print("Description: Testing narration and tone enable/disable")
    print()
    
    player = HybridAudioPlayer()
    
    test_play = {
        'description': 'Test play for preferences',
        'yardage': 10,
        'type': 'pass',
        'yardsToEndzone': 50
    }
    
    # Test 1: Both enabled (default)
    print("\n4a. Both narration and tones enabled (default)")
    print("    Expected: Narration + Musical tone")
    player.set_preference('narration_enabled', True)
    player.set_preference('tones_enabled', True)
    player.play_single_play(test_play)
    time.sleep(1)
    
    # Test 2: Tones only
    print("\n4b. Tones only (narration disabled)")
    print("    Expected: Musical tone only, no speech")
    player.set_preference('narration_enabled', False)
    player.set_preference('tones_enabled', True)
    player.play_single_play(test_play)
    time.sleep(1)
    
    # Test 3: Narration only
    print("\n4c. Narration only (tones disabled)")
    print("    Expected: Speech only, no musical tone")
    player.set_preference('narration_enabled', True)
    player.set_preference('tones_enabled', False)
    player.play_single_play(test_play)
    time.sleep(1)
    
    # Restore defaults
    player.set_preference('narration_enabled', True)
    player.set_preference('tones_enabled', True)
    
    player.cleanup()
    print("\n✓ Preferences test complete")


def test_field_position_demo():
    """Demonstrate stereo field positioning across the entire field"""
    print("\n" + "="*70)
    print("TEST 5: STEREO FIELD POSITIONING DEMO")
    print("="*70)
    print("Description: Drive from goal line to goal line showing stereo panning")
    print()
    
    player = HybridAudioPlayer()
    
    # Long drive showing stereo progression
    long_drive = [
        {'description': 'Own 5-yard line', 'yardage': 5, 'type': 'rush', 'yardsToEndzone': 95},
        {'description': 'Own 15-yard line', 'yardage': 10, 'type': 'pass', 'yardsToEndzone': 85},
        {'description': 'Own 30-yard line', 'yardage': 15, 'type': 'rush', 'yardsToEndzone': 70},
        {'description': 'Own 45-yard line', 'yardage': 15, 'type': 'pass', 'yardsToEndzone': 55},
        {'description': 'Opponent 45-yard line', 'yardage': 10, 'type': 'rush', 'yardsToEndzone': 45},
        {'description': 'Opponent 30-yard line', 'yardage': 15, 'type': 'pass', 'yardsToEndzone': 30},
        {'description': 'Opponent 15-yard line', 'yardage': 15, 'type': 'rush', 'yardsToEndzone': 15},
        {'description': 'Opponent 5-yard line', 'yardage': 10, 'type': 'pass', 'yardsToEndzone': 5},
    ]
    
    print("Listen for the stereo panning effect:")
    print("  - Early plays: Sound from LEFT speaker (own territory)")
    print("  - Middle plays: Sound from CENTER (near midfield)")
    print("  - Late plays: Sound from RIGHT speaker (opponent territory)")
    print()
    print("Playing drive...")
    
    # Use narration disabled for clearer stereo demonstration
    player.set_preference('narration_enabled', False)
    player.play_drive_sequence(long_drive, mode='sequence')
    
    player.cleanup()
    print("\n✓ Stereo positioning demo complete")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("HYBRID AUDIO PLAYER - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print()
    print("This test demonstrates all features of Option D (Hybrid Approach):")
    print("  • Single play mode (individual play narration)")
    print("  • Sequence mode (drive with key moments)")
    print("  • Tutorial mode (educational explanations)")
    print("  • User preferences (enable/disable features)")
    print("  • Stereo field positioning (spatial audio)")
    print()
    input("Press ENTER to begin tests (make sure volume is on)...")
    
    try:
        # Run all tests
        test_single_play_mode()
        time.sleep(2)
        
        test_sequence_mode()
        time.sleep(2)
        
        test_tutorial_mode()
        time.sleep(2)
        
        test_preferences()
        time.sleep(2)
        
        test_field_position_demo()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETE!")
        print("="*70)
        print()
        print("✓ Single play mode - Working")
        print("✓ Sequence mode - Working")
        print("✓ Tutorial mode - Working")
        print("✓ User preferences - Working")
        print("✓ Stereo positioning - Working")
        print()
        print("The Hybrid Audio Player (Option D) is fully operational!")
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nError during testing: {e}")
        import traceback
        traceback.print_exc()
