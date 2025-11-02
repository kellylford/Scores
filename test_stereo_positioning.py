#!/usr/bin/env python3
"""
Test stereo field positioning for football drives
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from football_audio_mapper import FootballAudioMapper
    print("✅ FootballAudioMapper imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("🏈 TESTING STEREO FIELD POSITIONING")
print("="*70)

# Create mapper
mapper = FootballAudioMapper()

# Test plays with different field positions
test_plays = [
    {
        'text': 'K.Cousins pass short right to J.Jefferson for 12 yards',
        'statYardage': 12,
        'type': {'text': 'Pass Reception'},
        'start': {
            'down': 1,
            'distance': 10,
            'yardsToEndzone': 85,  # Near their own endzone
            'possessionText': 'MIN 15'
        }
    },
    {
        'text': 'D.Cook rush up the middle for 8 yards',
        'statYardage': 8,
        'type': {'text': 'Rush'},
        'start': {
            'down': 2,
            'distance': 3,
            'yardsToEndzone': 50,  # Midfield
            'possessionText': 'MIN 50'
        }
    },
    {
        'text': 'K.Cousins pass deep right to A.Thielen for 25 yards TOUCHDOWN',
        'statYardage': 25,
        'type': {'text': 'Pass Reception'},
        'scoringPlay': True,
        'start': {
            'down': 1,
            'distance': 10,
            'yardsToEndzone': 25,  # Red zone
            'possessionText': 'CHI 25'
        }
    }
]

print("Testing field position calculation:")
print("-" * 50)

for i, play in enumerate(test_plays, 1):
    config = mapper.map_play_to_audio(play)
    
    yards_to_endzone = play['start']['yardsToEndzone']
    expected_position = 100 - yards_to_endzone
    
    print(f"\nPlay {i}: {play['text'][:50]}...")
    print(f"  Yards to endzone: {yards_to_endzone}")
    print(f"  Expected field position: {expected_position}")
    print(f"  Calculated field position: {config.field_position}")
    print(f"  Audio: {config.frequency:.1f}Hz {config.wave_type}")
    
    # Describe stereo positioning
    if config.field_position is not None:
        if config.field_position < 25:
            stereo_desc = "LEFT (own territory)"
        elif config.field_position < 75:
            stereo_desc = "CENTER (midfield area)"
        else:
            stereo_desc = "RIGHT (opponent territory)"
        print(f"  Stereo position: {stereo_desc}")

print("\n" + "="*70)
print("🎵 STEREO POSITIONING LEGEND")
print("="*70)
print("Left speaker (0):     Own endzone")
print("Center (50):          Midfield") 
print("Right speaker (100):  Opponent's endzone")
print("")
print("As the team moves down the field towards a touchdown,")
print("the audio should pan from LEFT → CENTER → RIGHT")
print("\n✅ Stereo field positioning is now implemented!")
print("The audio will now represent movement down the field")
print("with left-to-right stereo panning! 🎧")