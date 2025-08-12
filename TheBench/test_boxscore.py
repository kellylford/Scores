#!/usr/bin/env python3
"""Test script to verify boxscore functionality works correctly"""

import sys
sys.path.append('.')

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from main import GameDetailsView
from accessible_table import BoxscoreTable

# Create mock boxscore data matching the expected structure
mock_boxscore = {
    'teams': [
        {
            'name': 'Test Team A',
            'stats': {
                'hits': '8',
                'runs': '5',
                'errors': '1',
                'atBats': '32',
                'rbi': '5'
            }
        },
        {
            'name': 'Test Team B', 
            'stats': {
                'hits': '6',
                'runs': '3',
                'errors': '0',
                'atBats': '28',
                'rbi': '3'
            }
        }
    ],
    'players': [
        {
            'team': 'Test Team A',
            'players': [
                {'name': 'Player 1', 'position': '1B', 'ab': '4', 'r': '1', 'h': '2', 'rbi': '1'},
                {'name': 'Pitcher 1', 'position': 'P', 'ip': '6.0', 'h': '5', 'r': '2', 'er': '2'}
            ]
        },
        {
            'team': 'Test Team B',
            'players': [
                {'name': 'Player A', 'position': 'OF', 'ab': '3', 'r': '0', 'h': '1', 'rbi': '0'},
                {'name': 'Pitcher A', 'position': 'P', 'ip': '5.0', 'h': '7', 'r': '3', 'er': '3'}
            ]
        }
    ]
}

def test_boxscore_creation():
    app = QApplication([])
    
    # Create a GameDetailsView instance with proper parameters
    view = GameDetailsView()
    view.league = 'test_league'
    view.game_id = 'test_game_id'
    
    # Create a test layout
    layout = QVBoxLayout()
    test_widget = QWidget()
    test_widget.setLayout(layout)
    
    print("Testing boxscore layout creation...")
    print(f"Mock data has {len(mock_boxscore['teams'])} teams and {len(mock_boxscore['players'])} player groups")
    
    # Test the boxscore layout function
    try:
        view._add_boxscore_data_to_layout(layout, mock_boxscore)
        print(f"✅ _add_boxscore_data_to_layout completed successfully")
        print(f"Layout now has {layout.count()} widgets")
        
        # Simple check - if we have widgets, the function worked
        if layout.count() > 0:
            print("✅ SUCCESS: Layout has widgets, indicating tables were created!")
            return True
        else:
            print("❌ FAILURE: No widgets in layout")
            return False
            
    except Exception as e:
        print(f"❌ FAILURE: Exception during layout creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_boxscore_creation()
    sys.exit(0 if success else 1)
