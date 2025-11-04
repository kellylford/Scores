"""
Test animated stereo panning - audio moves left to right during play
This demonstrates the new feature where audio pans from start to end position
"""

from football_audio_mapper import FootballAudioMapper
from audio_player import AudioPlayer

def test_animated_panning():
    print("\n" + "="*70)
    print("TESTING: Animated Stereo Panning")
    print("="*70)
    print("\nThis test demonstrates audio moving left→right during each play")
    print("based on the actual yardage gained.\n")
    
    mapper = FootballAudioMapper()
    player = AudioPlayer()
    
    # Test plays with different yardage amounts
    test_plays = [
        {
            'title': '3 yard run',
            'play': {
                'text': 'RB rush for 3 yards',
                'statYardage': 3,
                'type': {'text': 'Rush'},
                'start': {'yardsToEndzone': 75}  # Own 25-yard line
            }
        },
        {
            'title': '12 yard pass (medium gain)',
            'play': {
                'text': 'QB pass for 12 yards',
                'statYardage': 12,
                'type': {'text': 'Pass Reception'},
                'start': {'yardsToEndzone': 72}
            }
        },
        {
            'title': '35 yard pass (big play)',
            'play': {
                'text': 'QB deep pass for 35 yards',
                'statYardage': 35,
                'type': {'text': 'Pass Reception'},
                'start': {'yardsToEndzone': 60}
            }
        },
        {
            'title': '7 yard sack (moves backward)',
            'play': {
                'text': 'QB sacked for 7 yards',
                'statYardage': -7,
                'type': {'text': 'Sack'},
                'start': {'yardsToEndzone': 25}
            }
        }
    ]
    
    for i, test in enumerate(test_plays, 1):
        print(f"\n{i}. {test['title']}")
        
        # Generate audio config
        config = mapper.map_play_to_audio(test['play'])
        
        print(f"   Start position: {config.field_position:.1f}% (stereo field)")
        print(f"   End position:   {config.end_field_position:.1f}% (stereo field)")
        
        if config.field_position < config.end_field_position:
            print(f"   → Audio will pan LEFT to RIGHT (advancing down field)")
        elif config.field_position > config.end_field_position:
            print(f"   ← Audio will pan RIGHT to LEFT (loss of yardage)")
        else:
            print(f"   ○ Audio stays at same position (no gain)")
        
        # Play the audio
        print(f"   Playing...")
        player.play_single_play(config, field_position=int(config.field_position),
                               end_field_position=int(config.end_field_position))
    
    player.cleanup()
    
    print("\n" + "="*70)
    print("✅ Test complete!")
    print("="*70)
    print("\nKey feature: Audio now MOVES during each play to show")
    print("the distance gained/lost, not just the starting position!")
    print("\nShort plays: Subtle stereo movement")
    print("Big plays: Dramatic left→right sweep")
    print("Losses: Audio moves backward (right→left)")

if __name__ == "__main__":
    test_animated_panning()
