#!/usr/bin/env python3
"""Test the focus and performance fixes for statistics dialog"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from scores import StatisticsViewDialog
import time

def test_statistics_performance():
    """Test the performance of statistics loading"""
    
    print("=== TESTING STATISTICS PERFORMANCE ===\n")
    
    app = QApplication(sys.argv)
    
    try:
        print("Testing MLB Player Statistics...")
        start_time = time.time()
        
        # Create the dialog as it would be in the real app
        dialog = StatisticsViewDialog("MLB", "player")
        
        end_time = time.time()
        load_time = end_time - start_time
        
        print(f"✅ Dialog creation time: {load_time:.3f} seconds")
        
        # Test that we have stats available
        if hasattr(dialog, 'statistics_data') and dialog.statistics_data:
            player_stats = dialog.statistics_data.get('player_stats', [])
            print(f"✅ Found {len(player_stats)} statistical categories")
            
            # Test available stats processing
            start_time = time.time()
            available_stats = dialog._get_available_statistics()
            end_time = time.time()
            process_time = end_time - start_time
            
            print(f"✅ Available stats processing time: {process_time:.3f} seconds")
            print(f"✅ Available stats count: {len(available_stats)}")
            
            if available_stats:
                print(f"✅ Sample stat: {available_stats[0].get('name', 'Unknown')}")
            
            # Test focus elements exist
            if hasattr(dialog, 'stats_list') and hasattr(dialog, 'results_list'):
                print("✅ Focus elements (stats_list, results_list) created successfully")
            else:
                print("❌ Focus elements missing")
        else:
            print("❌ No statistics data loaded")
        
        app.quit()
        
        if load_time < 1.0:
            print(f"\n🎉 PERFORMANCE: Excellent load time ({load_time:.3f}s)")
        elif load_time < 2.0:
            print(f"\n⚠️ PERFORMANCE: Acceptable load time ({load_time:.3f}s)")
        else:
            print(f"\n❌ PERFORMANCE: Slow load time ({load_time:.3f}s)")
            
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        app.quit()

if __name__ == "__main__":
    test_statistics_performance()
