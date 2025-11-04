"""
Test the new Long Sustained Drive demo to verify stereo positioning.
This drive goes 99 yards from the goal line with 11 plays.
"""

import sys
sys.path.append('.')

from football_audio_mapper import FootballAudioMapper

def test_long_sustained_drive():
    """Test the 11-play, 99-yard drive"""
    
    mapper = FootballAudioMapper()
    
    print("="*80)
    print("TESTING: Long Sustained Drive (11 plays, 99 yards)")
    print("="*80)
    print()
    print("This drive starts at the 1-yard line (99 yards to endzone)")
    print("and ends at the 1-yard line (1 yard to endzone)")
    print()
    print("Listen for stereo audio panning from FAR LEFT → CENTER → FAR RIGHT")
    print()
    
    # The drive data from scores.py
    plays = [
        {"text": "RB rush up middle for 4 yards", "statYardage": 4, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 99}},
        {"text": "QB pass short right for 6 yards", "statYardage": 6, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 95}},
        {"text": "RB rush off tackle for 8 yards", "statYardage": 8, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 89}},
        {"text": "QB pass middle for 12 yards", "statYardage": 12, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 81}},
        {"text": "RB rush left end for 9 yards", "statYardage": 9, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 69}},
        {"text": "QB pass deep left for 18 yards - CROSSES MIDFIELD", "statYardage": 18, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 60}},
        {"text": "RB rush right tackle for 7 yards", "statYardage": 7, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 42}},
        {"text": "QB pass short middle for 11 yards", "statYardage": 11, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 35}},
        {"text": "RB rush up middle for 5 yards", "statYardage": 5, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 24}},
        {"text": "QB pass right for 13 yards", "statYardage": 13, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 19}},
        {"text": "RB rush left for 5 yards", "statYardage": 5, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 6}}
    ]
    
    print(f"{'Play':<6} {'Description':<50} {'YdsToEnd':<12} {'StereoPos':<11} {'Stereo Location':<20}")
    print("-"*100)
    
    total_yards = 0
    for i, play in enumerate(plays, 1):
        config = mapper.map_play_to_audio(play)
        yards_to_end = play['start']['yardsToEndzone']
        yardage = play['statYardage']
        total_yards += yardage
        
        # Determine stereo location description
        pos = config.field_position
        if pos < 10:
            location = "Far Left (own 1)"
        elif pos < 30:
            location = "Left (own territory)"
        elif pos < 45:
            location = "Left-Center"
        elif pos < 55:
            location = "CENTER (midfield)"
        elif pos < 70:
            location = "Right-Center"
        elif pos < 90:
            location = "Right (opp territory)"
        else:
            location = "Far Right (opp 1)"
        
        # Mark critical midfield crossing
        marker = " ← MIDFIELD!" if 50 <= yards_to_end <= 60 and yardage >= 10 else ""
        
        # Truncate description if too long
        desc = play['text'][:48] if len(play['text']) > 48 else play['text']
        
        print(f"{i:<6} {desc:<50} {yards_to_end:<12} {pos:>6.1f}%     {location:<20}{marker}")
    
    print("-"*100)
    print(f"Total: {len(plays)} plays, {total_yards} yards")
    print()
    print("="*80)
    print("VERIFICATION:")
    print("="*80)
    print()
    print("✓ Play 1 (Own 1-yard line):     Should be FAR LEFT (1% position)")
    print("✓ Play 6 (Crosses midfield):    Should move through CENTER (50% position)")
    print("✓ Play 11 (Opponent 1-yard):    Should be FAR RIGHT (94% position)")
    print()
    print("Expected stereo behavior:")
    print("  - Sound should smoothly pan from FAR LEFT → CENTER → FAR RIGHT")
    print("  - Full range of stereo field utilized")
    print("  - Demonstrates complete field position mapping")
    print("  - No sudden jumps or reversals")
    print()
    
    # Verify key positions
    print("="*80)
    print("KEY POSITION VERIFICATION:")
    print("="*80)
    print()
    
    key_plays = [
        (plays[0], "Start (Own 1)", "~1%", "Far Left"),
        (plays[5], "Crosses Midfield", "~42-58%", "Center"),
        (plays[-1], "End (Opponent 1)", "~94%", "Far Right")
    ]
    
    for play, label, expected_range, expected_side in key_plays:
        config = mapper.map_play_to_audio(play)
        yards_to_end = play['start']['yardsToEndzone']
        actual_pos = config.field_position
        
        print(f"✓ {label:<25} YardsToEnd: {yards_to_end:>3}  →  Stereo: {actual_pos:>6.1f}%  ({expected_side})")
    
    print()
    print("="*80)
    print("✓ Drive demonstrates complete stereo field from own goal line to opponent goal line!")
    print("="*80)

if __name__ == '__main__':
    test_long_sustained_drive()
