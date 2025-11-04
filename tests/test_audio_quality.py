"""
A/B comparison test: Old basic audio vs. Enhanced professional audio

This test plays the same plays twice:
1. First with basic audio (toy-like)
2. Then with enhanced audio (harmonics + ADSR + blending)

Listen to the difference in richness and warmth!
"""

from audio_player import AudioPlayer
from enhanced_audio_player import EnhancedAudioPlayer
from football_audio_mapper import PlayAudioConfig
import time


def test_comparison():
    """Compare basic vs enhanced audio for different play types."""
    
    # Create both players
    basic_player = AudioPlayer()
    enhanced_player = EnhancedAudioPlayer()
    
    print("🎵 Audio Quality Comparison Test")
    print("=" * 60)
    print("\nYou'll hear each play TWICE:")
    print("  1️⃣  BASIC audio (current toy-like sound)")
    print("  2️⃣  ENHANCED audio (professional sound)\n")
    print("Listen for:")
    print("  • Richer, warmer tone quality")
    print("  • More musical harmonics")
    print("  • Smoother attack/release")
    print("  • More weight and presence\n")
    print("=" * 60)
    
    test_plays = [
        {
            'name': '🏃 Rushing Play',
            'config': PlayAudioConfig(
                frequency=400,
                wave_type='square',
                duration=0.4,
                volume=0.3,
                attack=0.01,
                decay=0.05,
                play_type='rush'
            ),
            'field_pos': 30,
            'end_pos': 37
        },
        {
            'name': '🎯 Passing Play',
            'config': PlayAudioConfig(
                frequency=600,
                wave_type='sine',
                duration=0.5,
                volume=0.3,
                attack=0.005,
                decay=0.1,
                play_type='pass'
            ),
            'field_pos': 40,
            'end_pos': 55
        },
        {
            'name': '🏆 Touchdown!',
            'config': PlayAudioConfig(
                frequency=800,
                wave_type='sawtooth',
                duration=0.8,
                volume=0.3,
                attack=0.05,
                decay=0.2,
                play_type='touchdown'
            ),
            'field_pos': 95,
            'end_pos': 100
        },
        {
            'name': '💥 Sack',
            'config': PlayAudioConfig(
                frequency=250,
                wave_type='square',
                duration=0.3,
                volume=0.35,
                attack=0.02,
                decay=0.08,
                play_type='sack'
            ),
            'field_pos': 65,
            'end_pos': 55
        },
    ]
    
    for play in test_plays:
        print(f"\n{play['name']}")
        print("-" * 40)
        
        # Play with BASIC audio
        print("  1️⃣  BASIC (toy-like)...", end='', flush=True)
        basic_player.play_single_play(
            play['config'], 
            play['field_pos'], 
            play['end_pos']
        )
        print(" ✓")
        time.sleep(0.3)  # Brief pause
        
        # Play with ENHANCED audio
        print("  2️⃣  ENHANCED (professional)...", end='', flush=True)
        enhanced_player.play_single_play(
            play['config'],
            play['field_pos'],
            play['end_pos']
        )
        print(" ✓")
        time.sleep(0.5)  # Pause before next comparison
    
    print("\n" + "=" * 60)
    print("🎧 Comparison complete!")
    print("\nKey improvements in ENHANCED audio:")
    print("  ✓ Harmonic layering adds richness (octave + fifth)")
    print("  ✓ Waveform blending creates warmer tones")
    print("  ✓ Proper ADSR envelope sounds more musical")
    print("  ✓ Sub-bass adds weight to touchdowns")
    print("  ✓ Overall: Professional vs. toy-like")
    print("=" * 60)
    
    # Cleanup
    basic_player.cleanup()
    enhanced_player.cleanup()


if __name__ == "__main__":
    test_comparison()
