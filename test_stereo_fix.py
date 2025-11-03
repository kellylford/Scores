"""
Test the fixed stereo positioning for football drives crossing the 50-yard line.
This simulates a realistic drive and verifies stereo positioning is correct.
"""

import sys
sys.path.append('.')

from football_audio_mapper import FootballAudioMapper

def test_drive_across_field():
    """Test a drive that crosses the 50-yard line"""
    
    mapper = FootballAudioMapper()
    
    print("="*80)
    print("TESTING: Drive from Own 25 to Touchdown")
    print("="*80)
    print()
    
    # Simulate a scoring drive
    plays = [
        {
            'statYardage': 5,
            'type': {'text': 'Rush'},
            'start': {'yardsToEndzone': 75},  # Own 25
            'text': '5 yard rush'
        },
        {
            'statYardage': 12,
            'type': {'text': 'Pass Reception'},
            'start': {'yardsToEndzone': 70},  # Own 30
            'text': '12 yard pass'
        },
        {
            'statYardage': 8,
            'type': {'text': 'Rush'},
            'start': {'yardsToEndzone': 58},  # Own 42
            'text': '8 yard rush'
        },
        {
            'statYardage': 25,
            'type': {'text': 'Pass Reception'},
            'start': {'yardsToEndzone': 50},  # MIDFIELD - CRITICAL TEST
            'text': '25 yard pass - CROSSES 50!'
        },
        {
            'statYardage': 15,
            'type': {'text': 'Pass Reception'},
            'start': {'yardsToEndzone': 25},  # Opponent 25
            'text': '15 yard pass'
        },
        {
            'statYardage': 10,
            'type': {'text': 'Rush'},
            'start': {'yardsToEndzone': 10},  # Opponent 10 (red zone)
            'text': '10 yard TD run',
            'scoringPlay': True,
            'scoreValue': 6
        }
    ]
    
    print(f"{'Play':<6} {'Description':<30} {'YardsToEnd':<12} {'StereoPos':<11} {'Stereo Location':<20}")
    print("-"*90)
    
    for i, play in enumerate(plays, 1):
        config = mapper.map_play_to_audio(play)
        yards_to_end = play['start']['yardsToEndzone']
        
        # Determine stereo location description
        pos = config.field_position
        if pos < 20:
            location = "Far Left (own end)"
        elif pos < 40:
            location = "Left (own territory)"
        elif pos < 60:
            location = "Center (midfield)"
        elif pos < 80:
            location = "Right (opp territory)"
        else:
            location = "Far Right (opp end)"
        
        # Mark critical midfield play
        marker = " ← MIDFIELD!" if yards_to_end == 50 else ""
        
        print(f"{i:<6} {play['text']:<30} {yards_to_end:<12} {pos:>6.1f}%     {location:<20}{marker}")
    
    print()
    print("="*80)
    print("VERIFICATION:")
    print("="*80)
    print()
    print("✓ Play 1 (Own 25):        Should be LEFT side (25% position)")
    print("✓ Play 4 (Midfield):      Should be CENTER (50% position) - CRITICAL")  
    print("✓ Play 6 (Opponent 10):   Should be RIGHT side (90% position)")
    print()
    print("Expected behavior:")
    print("  - Sound should smoothly pan from LEFT → CENTER → RIGHT")
    print("  - No sudden jumps or reversals")
    print("  - Midfield play should be perfectly centered")
    print()
    
    # Verify specific expectations
    print("="*80)
    print("SPECIFIC TESTS:")
    print("="*80)
    print()
    
    test_positions = [
        (100, "Own Endzone", 0, "Left"),
        (75, "Own 25", 25, "Left-Center"),
        (50, "Midfield", 50, "Center"),
        (25, "Opponent 25", 75, "Right-Center"),
        (0, "Opponent Endzone", 100, "Right"),
    ]
    
    all_passed = True
    for yards_to_end, description, expected_pos, expected_side in test_positions:
        play = {'start': {'yardsToEndzone': yards_to_end}, 'type': {'text': 'Test'}}
        config = mapper.map_play_to_audio(play)
        actual_pos = config.field_position
        
        # Allow 1% tolerance
        passed = abs(actual_pos - expected_pos) <= 1
        status = "✓ PASS" if passed else "✗ FAIL"
        
        if not passed:
            all_passed = False
        
        print(f"{status} {description:<20} Expected: {expected_pos:>3}%  Actual: {actual_pos:>6.1f}%  ({expected_side})")
    
    print()
    if all_passed:
        print("="*80)
        print("✓✓✓ ALL TESTS PASSED! Stereo positioning is working correctly. ✓✓✓")
        print("="*80)
    else:
        print("="*80)
        print("✗✗✗ SOME TESTS FAILED! Check the positioning logic. ✗✗✗")
        print("="*80)

if __name__ == '__main__':
    test_drive_across_field()
