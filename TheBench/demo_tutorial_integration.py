"""
Demo: Hybrid Audio Integration in Football Tutorial
Shows how the new audio system works with different play types and modes
"""

from hybrid_audio_player import HybridAudioPlayer
import time

def demo_play_types():
    """Demonstrate each play type with hybrid audio"""
    print("\n" + "="*70)
    print("DEMO: PLAY TYPE DEMONSTRATIONS")
    print("="*70)
    print("\nThis demo shows how different play types sound in hybrid mode.")
    print("Each play type has a distinct wave pattern and pitch range.\n")
    
    player = HybridAudioPlayer()
    
    play_types = [
        {
            'title': '🏃 Rush Play - Short (3 yards)',
            'description': 'Square wave, low pitch',
            'play': {'description': 'RB rush up middle for 3 yards', 'yardage': 3, 'type': 'rush', 'yardsToEndzone': 50}
        },
        {
            'title': '🏃 Rush Play - Medium (12 yards)',
            'description': 'Square wave, medium pitch',
            'play': {'description': 'RB rush off tackle for 12 yards', 'yardage': 12, 'type': 'rush', 'yardsToEndzone': 50}
        },
        {
            'title': '🏃 Rush Play - Long (35 yards)',
            'description': 'Square wave, high pitch',
            'play': {'description': 'RB breakaway for 35 yards', 'yardage': 35, 'type': 'rush', 'yardsToEndzone': 50}
        },
        {
            'title': '🎯 Pass Play - Short (5 yards)',
            'description': 'Sine wave, low pitch',
            'play': {'description': 'QB pass short for 5 yards', 'yardage': 5, 'type': 'pass', 'yardsToEndzone': 50}
        },
        {
            'title': '🎯 Pass Play - Medium (18 yards)',
            'description': 'Sine wave, medium pitch',
            'play': {'description': 'QB pass for 18 yards', 'yardage': 18, 'type': 'pass', 'yardsToEndzone': 50}
        },
        {
            'title': '🎯 Pass Play - Long (40 yards)',
            'description': 'Sine wave, high pitch',
            'play': {'description': 'QB deep pass for 40 yards', 'yardage': 40, 'type': 'pass', 'yardsToEndzone': 50}
        },
        {
            'title': '⚠️ Sack (7 yard loss)',
            'description': 'Sine wave, lower pitch (negative yardage)',
            'play': {'description': 'QB sacked for 7 yard loss', 'yardage': -7, 'type': 'pass', 'yardsToEndzone': 50}
        },
        {
            'title': '🏈 Field Goal (25 yards)',
            'description': 'Sawtooth wave, scoring',
            'play': {'description': '25-yard field goal GOOD', 'yardage': 0, 'type': 'field_goal', 'yardsToEndzone': 50, 'isScoringPlay': True}
        },
        {
            'title': '🎉 Touchdown Pass (15 yards)',
            'description': 'Sawtooth wave, highest pitch scoring',
            'play': {'description': 'QB pass for 15 yards TOUCHDOWN', 'yardage': 15, 'type': 'pass', 'yardsToEndzone': 50, 'isScoringPlay': True}
        }
    ]
    
    for i, demo in enumerate(play_types, 1):
        print(f"\n{i}. {demo['title']}")
        print(f"   {demo['description']}")
        print(f"   Playing: {demo['play']['description']}")
        
        player.play_single_play(demo['play'], with_narration=True)
        
        if i < len(play_types):
            time.sleep(1)  # Brief pause between demos
    
    player.cleanup()
    print("\n✓ Play type demonstrations complete")


def demo_audio_modes():
    """Demonstrate the three audio modes"""
    print("\n" + "="*70)
    print("DEMO: AUDIO MODE COMPARISON")
    print("="*70)
    print("\nThe hybrid audio system supports three modes:\n")
    
    test_play = {
        'description': 'RB rush for 12 yards',
        'yardage': 12,
        'type': 'rush',
        'yardsToEndzone': 65
    }
    
    # Mode 1: Hybrid (default)
    print("1. 🎙️ HYBRID MODE (Narration + Tones)")
    print("   Combines TTS narration with musical tones")
    print("   Best for: Accessibility and full information\n")
    
    player = HybridAudioPlayer()
    player.set_preference('narration_enabled', True)
    player.set_preference('tones_enabled', True)
    player.play_single_play(test_play)
    player.cleanup()
    time.sleep(1)
    
    # Mode 2: Tones Only
    print("\n2. 🎵 TONES ONLY MODE")
    print("   Musical tones with stereo positioning")
    print("   Best for: Fast playback, minimal distraction\n")
    
    player = HybridAudioPlayer()
    player.set_preference('narration_enabled', False)
    player.set_preference('tones_enabled', True)
    player.play_single_play(test_play)
    player.cleanup()
    time.sleep(1)
    
    # Mode 3: Narration Only
    print("\n3. 🗣️ NARRATION ONLY MODE")
    print("   TTS narration without musical tones")
    print("   Best for: Screen reader users who prefer speech only\n")
    
    player = HybridAudioPlayer()
    player.set_preference('narration_enabled', True)
    player.set_preference('tones_enabled', False)
    player.play_single_play(test_play)
    player.cleanup()
    
    print("\n✓ Audio mode comparison complete")


def demo_drive_sequence():
    """Demonstrate a full drive with hybrid audio"""
    print("\n" + "="*70)
    print("DEMO: FULL DRIVE WITH HYBRID AUDIO")
    print("="*70)
    print("\nThis shows a touchdown drive using sequence mode:")
    print("  • Fast musical tones for all plays")
    print("  • Stereo panning shows field progression")
    print("  • Key moments announced after sequence\n")
    
    touchdown_drive = [
        {'description': 'RB rush for 5 yards', 'yardage': 5, 'type': 'rush', 'yardsToEndzone': 75},
        {'description': 'QB pass for 22 yards', 'yardage': 22, 'type': 'pass', 'yardsToEndzone': 70},  # Big play
        {'description': 'RB rush for 8 yards', 'yardage': 8, 'type': 'rush', 'yardsToEndzone': 48},
        {'description': 'QB pass for 15 yards', 'yardage': 15, 'type': 'pass', 'yardsToEndzone': 40},
        {'description': 'RB rush for 25 yards - TOUCHDOWN', 'yardage': 25, 'type': 'rush', 'yardsToEndzone': 25, 'isScoringPlay': True}
    ]
    
    print("Drive: 5 plays, 75 yards for TOUCHDOWN")
    print("Listen for:")
    print("  1. Rapid musical tones (left to right stereo panning)")
    print("  2. Announcement of big play (22 yards)")
    print("  3. Touchdown announcement\n")
    
    player = HybridAudioPlayer()
    player.play_drive_sequence(touchdown_drive, mode='sequence')
    player.cleanup()
    
    print("\n✓ Drive sequence complete")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("HYBRID AUDIO INTEGRATION - COMPREHENSIVE DEMO")
    print("="*70)
    print("\nThis demo shows the new hybrid audio system integrated into")
    print("the Football Audio Tutorial. Make sure your volume is on!\n")
    
    input("Press ENTER to start the demo...")
    
    try:
        # Demo 1: Show each play type
        demo_play_types()
        time.sleep(2)
        
        # Demo 2: Compare audio modes
        demo_audio_modes()
        time.sleep(2)
        
        # Demo 3: Full drive sequence
        demo_drive_sequence()
        
        print("\n" + "="*70)
        print("✅ DEMO COMPLETE!")
        print("="*70)
        print("\nThe Football Audio Tutorial now offers:")
        print("  ✓ 9 individual play type demonstrations")
        print("  ✓ 6 full drive scenarios")
        print("  ✓ 3 audio modes (hybrid, tones, narration)")
        print("  ✓ Clear wave type explanations (square, sine, sawtooth)")
        print("  ✓ Full accessibility with TTS narration")
        print("\nIntegration complete and ready to use! 🎉")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
