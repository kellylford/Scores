"""
Quick demo of Hybrid Audio Player (Option D)
Shows the three main modes in action
"""

from hybrid_audio_player import HybridAudioPlayer

def main():
    print("\n" + "="*60)
    print("HYBRID AUDIO PLAYER - QUICK DEMO")
    print("Option D from AUDIO_ENHANCEMENT_OPTIONS.md")
    print("="*60)
    
    player = HybridAudioPlayer()
    
    # Demo 1: Single play with narration
    print("\n1. SINGLE PLAY MODE")
    print("   → 15 yard pass completion")
    print("   → Listen for: TTS narration + musical tone + stereo position\n")
    
    play = {
        'description': 'QB pass complete to WR for 15 yards',
        'yardage': 15,
        'type': 'pass',
        'yardsToEndzone': 65
    }
    player.play_single_play(play, with_narration=True)
    
    # Demo 2: Touchdown drive
    print("\n2. SEQUENCE MODE (Touchdown Drive)")
    print("   → 3 plays including big play and touchdown")
    print("   → Listen for: Rapid tones → Key moment announcements\n")
    
    drive = [
        {'description': 'RB rush for 8 yards', 'yardage': 8, 'type': 'rush', 'yardsToEndzone': 35},
        {'description': 'QB pass for 22 yards', 'yardage': 22, 'type': 'pass', 'yardsToEndzone': 27},  # Big play
        {'description': 'RB rush for TD', 'yardage': 5, 'type': 'rush', 'yardsToEndzone': 5, 'isScoringPlay': True}
    ]
    player.play_drive_sequence(drive, mode='sequence')
    
    # Demo 3: Tutorial
    print("\n3. TUTORIAL MODE")
    print("   → Educational explanation of a pass play")
    print("   → Listen for: Detailed narration with technical info\n")
    
    tutorial = [
        {'description': 'Example pass play', 'yardage': 10, 'type': 'pass', 'yardsToEndzone': 50}
    ]
    player.play_drive_sequence(tutorial, mode='tutorial')
    
    player.cleanup()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print("\nThe Hybrid Audio Player successfully combines:")
    print("  ✓ TTS narration (informative)")
    print("  ✓ Musical tones (engaging)")
    print("  ✓ Stereo positioning (spatial awareness)")
    print("  ✓ Context-aware modes (right audio for the situation)")
    print("\nOption D is ready for integration! 🎯")

if __name__ == "__main__":
    main()
