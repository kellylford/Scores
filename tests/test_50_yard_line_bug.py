"""
Test to demonstrate the stereo positioning bug when crossing the 50-yard line.
"""

def calculate_field_position_current(yards_to_endzone):
    """Current implementation (buggy)"""
    field_position = 100 - yards_to_endzone
    enhanced_position = (field_position - 50) * 2.0 + 50
    result = max(0, min(100, enhanced_position))
    return result

def calculate_field_position_fixed(yards_to_endzone):
    """Fixed implementation"""
    # yardsToEndzone = distance to opponent's endzone (0-100)
    # We want: 0% = own endzone (left), 50% = midfield (center), 100% = opponent endzone (right)
    
    # Simple mapping: yards_to_endzone directly represents progress down field
    # Lower yardsToEndzone = closer to opponent = more to the right
    field_position = 100 - yards_to_endzone
    
    # No enhancement needed - use raw position
    # The stereo panning will handle the rest
    result = max(0, min(100, field_position))
    return result

print("Testing stereo positioning across field...")
print("\n" + "="*80)
print("Scenario: Drive starting from own 20, moving toward opponent endzone")
print("="*80 + "\n")

test_cases = [
    (80, "Own 20 yard line"),
    (70, "Own 30 yard line"),
    (60, "Own 40 yard line"),
    (50, "MIDFIELD (50 yard line) - CRITICAL"),
    (40, "Opponent 40 yard line"),
    (30, "Opponent 30 yard line"),
    (20, "Opponent 20 yard line (red zone)"),
    (10, "Opponent 10 yard line"),
    (0, "Opponent GOAL LINE - TOUCHDOWN"),
]

print(f"{'Yards to Endzone':<20} {'Field Description':<35} {'Current Bug':<15} {'Fixed':<15} {'Problem?':<10}")
print("-"*95)

for yards_to_endzone, description in test_cases:
    current = calculate_field_position_current(yards_to_endzone)
    fixed = calculate_field_position_fixed(yards_to_endzone)
    
    # Detect issues
    problem = ""
    if yards_to_endzone == 50:  # Midfield
        if abs(current - 50) > 5:
            problem = "❌ NOT CENTER!"
    elif yards_to_endzone > 50:  # Own territory
        if current > 50:
            problem = "❌ WRONG SIDE!"
    elif yards_to_endzone < 50:  # Opponent territory
        if current < 50:
            problem = "❌ WRONG SIDE!"
    
    print(f"{yards_to_endzone:<20} {description:<35} {current:>6.1f}%        {fixed:>6.1f}%        {problem}")

print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)
print("""
The CURRENT implementation has issues with the 2x multiplier:
- The enhanced_position formula: (field_position - 50) * 2.0 + 50
- This exaggerates movement, but can push values beyond valid range
- After clamping, positions near edges get distorted

The FIXED implementation:
- Uses raw field_position without enhancement
- Simpler and more predictable
- Stereo panning in audio_player.py handles the spatial effect
- No unexpected jumps or reversals

Key observations:
1. Midfield (50 yards to endzone) should = 50% (center) ✓
2. Own territory (>50 yards to endzone) should be <50% (left side) ✓
3. Opponent territory (<50 yards to endzone) should be >50% (right side) ✓
""")
