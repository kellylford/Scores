#!/usr/bin/env python3
"""Test script for football enhancement implementation"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from espn_api import extract_football_enhanced_display

def test_football_enhancement():
    """Test the football enhancement with mock data"""
    
    # Create mock game data structure similar to ESPN API
    mock_game_data = {
        'header': {
            'competitions': [{
                'competitors': [
                    {
                        'homeAway': 'home',
                        'team': {
                            'abbreviation': 'KC',
                            'displayName': 'Kansas City Chiefs'
                        },
                        'score': '14'
                    },
                    {
                        'homeAway': 'away', 
                        'team': {
                            'abbreviation': 'BUF',
                            'displayName': 'Buffalo Bills'
                        },
                        'score': '7'
                    }
                ],
                'status': {
                    'displayClock': '8:42',
                    'period': 2
                }
            }]
        },
        'drives': {
            'current': {
                'description': '7 plays, 45 yards, 3:18',
                'team': {
                    'abbreviation': 'KC',
                    'id': '12345'
                },
                'plays': [{
                    'text': 'M.Willis pass incomplete deep left to M.Heath',
                    'start': {
                        'down': 2,
                        'distance': 8,
                        'yardLine': 15,  # In redzone!
                        'team': {'id': '12345'},
                        'shortDownDistanceText': '2nd & 8'
                    }
                }]
            }
        }
    }
    
    print("Testing football enhancement with mock data...")
    print("=" * 50)
    
    # Test the function
    result = extract_football_enhanced_display(mock_game_data)
    
    print("Result:")
    print(result)
    print("=" * 50)
    
    if result:
        lines = result.split('\n')
        print(f"Number of lines: {len(lines)}")
        if len(lines) >= 1:
            print(f"Line 1 (Teams + RZ): {lines[0]}")
        if len(lines) >= 2:
            print(f"Line 2 (Stats): {lines[1]}")
        
        # Check for redzone indicator
        if '(RZ)' in result:
            print("✓ Redzone indicator found!")
        else:
            print("✗ Redzone indicator missing")
            
        # Check for expected components
        if 'Buffalo Bills' in result and 'Kansas City Chiefs' in result:
            print("✓ Team names found")
        if '7' in result and '14' in result:
            print("✓ Scores found")
        if '2nd & 8' in result:
            print("✓ Down and distance found")
        if 'Q2' in result or '8:42' in result:
            print("✓ Clock information found")
        if 'M.Willis pass incomplete' in result:
            print("✓ Last play information found")
            
    else:
        print("✗ Function returned None - something went wrong")

if __name__ == "__main__":
    test_football_enhancement()
