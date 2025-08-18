#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from scores import StatisticsViewDialog

def test_mlb_player_stats_ui():
    """Test the MLB player statistics in the UI"""
    
    print("=== TESTING MLB PLAYER STATS UI ===\n")
    
    app = QApplication(sys.argv)
    
    try:
        # Create the dialog as it would be in the real app
        dialog = StatisticsViewDialog("MLB", "player")
        
        # Test the _get_available_statistics function
        available_stats = dialog._get_available_statistics()
        
        print(f"Available stats count: {len(available_stats)}")
        
        if available_stats:
            print(f"First few stats:")
            for i, stat in enumerate(available_stats[:5]):
                print(f"  {i+1}. {stat.get('name', 'Unknown')}")
                data = stat.get('data', [])
                print(f"     Data count: {len(data)}")
                if data:
                    first_player = data[0]
                    print(f"     Sample: {first_player}")
        else:
            print("❌ NO STATS AVAILABLE!")
            
        app.quit()
        
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        app.quit()

if __name__ == "__main__":
    test_mlb_player_stats_ui()
