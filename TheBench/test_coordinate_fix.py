#!/usr/bin/env python3
"""
Test the corrected coordinate system
"""

import sys
sys.path.append('.')
from scores import get_pitch_location

def test_coordinates():
    """Test the corrected coordinate interpretation"""
    
    print("=== TESTING CORRECTED COORDINATE SYSTEM ===")
    print("Catcher's perspective: Lower X = LEFT, Higher X = RIGHT")
    print("Left edge of strike zone = X=80")
    print()
    
    test_cases = [
        (86, 167, "Pitch 2 - should be lower left (ESPN box 7)"),
        (86, 156, "Pitch 1 - should be left side"),
        (80, 150, "Left edge of strike zone"),
        (144, 207, "Original problem case"),
        (119, 210, "Pitch 3"),
        (80, 168, "Pitch 4 - left edge"),
        (155, 150, "Right edge of strike zone (estimated)"),
        (200, 150, "Right side"),
    ]
    
    for x, y, description in test_cases:
        result = get_pitch_location(x, y)
        print(f"({x:3d}, {y:3d}): {result:20s} - {description}")

if __name__ == "__main__":
    test_coordinates()
