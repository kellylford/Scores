"""
Interactive audio test for the fixed stereo positioning.
Play this to HEAR the difference - sound should smoothly pan across the stereo field.
"""

import sys
sys.path.append('.')

from football_audio_mapper import FootballAudioMapper
from audio_player import AudioPlayer

def play_crossing_drive():
    """Play a drive that crosses the 50-yard line with audio"""
    
    mapper = FootballAudioMapper()
    player = AudioPlayer()
    
    print("="*80)
    print("AUDIO TEST: Stereo Positioning Across Midfield")
    print("="*80)
    print()
    print("Put on headphones to hear the stereo effect!")
    print()
    print("You should hear:")
    print("  - Play 1-3: Sound in LEFT speaker (own territory)")
    print("  - Play 4:   Sound CENTERED (midfield)")
    print("  - Play 5-6: Sound in RIGHT speaker (opponent territory)")
    print()
    print("The sound should SMOOTHLY PAN from left → center → right")
    print("NO sudden jumps or reversals!")
    print()
    input("Press ENTER to play the drive audio...")
    print()
    
    # Simulate a scoring drive
    plays = [
        {
            'statYardage': 5,
            'type': {'text': 'Rush'},
            'start': {'yardsToEndzone': 75},  # Own 25
            'text': 'Own 25: 5 yard rush'
        },
        {
            'statYardage': 12,
            'type': {'text': 'Pass Reception'},
            'start': {'yardsToEndzone': 70},  # Own 30
            'text': 'Own 30: 12 yard pass'
        },
        {
            'statYardage': 8,
            'type': {'text': 'Rush'},
            'start': {'yardsToEndzone': 58},  # Own 42
            'text': 'Own 42: 8 yard rush'
        },
        {
            'statYardage': 25,
            'type': {'text': 'Pass Reception'},
            'start': {'yardsToEndzone': 50},  # MIDFIELD
            'text': '*** MIDFIELD: 25 yard pass - CROSSES 50! ***'
        },
        {
            'statYardage': 15,
            'type': {'text': 'Pass Reception'},
            'start': {'yardsToEndzone': 25},  # Opponent 25
            'text': 'Opponent 25: 15 yard pass'
        },
        {
            'statYardage': 10,
            'type': {'text': 'Rush'},
            'start': {'yardsToEndzone': 10},  # Opponent 10
            'text': 'Opponent 10: 10 yard TOUCHDOWN!',
            'scoringPlay': True,
            'scoreValue': 6
        }
    ]
    
    # Map to audio configs
    configs = []
    positions = []
    
    for play in plays:
        config = mapper.map_play_to_audio(play)
        configs.append(config)
        positions.append(config.field_position)
        print(f"Playing: {play['text']:<50} Stereo: {config.field_position:>6.1f}%")
    
    print()
    print("Playing audio sequence...")
    player.play_audio_sequence(configs, silence_between=0.5, field_positions=positions)
    
    print()
    print("="*80)
    print("Did you hear the sound pan smoothly from left → center → right?")
    print("="*80)
    print()
    print("Test variations:")
    print()
    
    # Test 1: Just midfield
    print("1. Testing MIDFIELD positioning (should be perfectly centered)...")
    midfield_play = {
        'statYardage': 10,
        'type': {'text': 'Pass Reception'},
        'start': {'yardsToEndzone': 50},
        'text': 'Midfield play'
    }
    config = mapper.map_play_to_audio(midfield_play)
    player.play_audio_sequence([config], silence_between=0, field_positions=[config.field_position])
    print(f"   Position: {config.field_position}% (should be 50%)")
    print()
    
    # Test 2: Own territory
    print("2. Testing OWN territory (should be in LEFT speaker)...")
    own_play = {
        'statYardage': 5,
        'type': {'text': 'Rush'},
        'start': {'yardsToEndzone': 80},
        'text': 'Own 20 yard line'
    }
    config = mapper.map_play_to_audio(own_play)
    player.play_audio_sequence([config], silence_between=0, field_positions=[config.field_position])
    print(f"   Position: {config.field_position}% (should be ~20%)")
    print()
    
    # Test 3: Opponent territory
    print("3. Testing OPPONENT territory (should be in RIGHT speaker)...")
    opp_play = {
        'statYardage': 5,
        'type': {'text': 'Rush'},
        'start': {'yardsToEndzone': 20},
        'text': 'Opponent 20 yard line'
    }
    config = mapper.map_play_to_audio(opp_play)
    player.play_audio_sequence([config], silence_between=0, field_positions=[config.field_position])
    print(f"   Position: {config.field_position}% (should be ~80%)")
    print()
    
    print("="*80)
    print("✓ Stereo positioning test complete!")
    print("="*80)

if __name__ == '__main__':
    play_crossing_drive()
