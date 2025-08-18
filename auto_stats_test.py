#!/usr/bin/env python3
"""
Automated test for statistics display issue
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from scores import StatisticsViewDialog

def auto_test_stats():
    """Automatically test the statistics view dialog"""
    app = QApplication(sys.argv)
    
    print("Creating StatisticsViewDialog for MLB player stats...")
    dialog = StatisticsViewDialog("MLB", "player", None)
    
    def auto_select_stat():
        """Auto-select the first statistic after a short delay"""
        print("Auto-selecting first statistic...")
        if hasattr(dialog, 'stats_list') and dialog.stats_list.count() > 0:
            first_item = dialog.stats_list.item(0)
            if first_item:
                print(f"Selecting: {first_item.text()}")
                dialog.stats_list.setCurrentItem(first_item)
                dialog._on_stat_selected(first_item)
                
                # Check table state after selection
                print(f"After selection - Table visible: {dialog.results_table.isVisible()}")
                print(f"Table row count: {dialog.results_table.rowCount()}")
                print(f"Table column count: {dialog.results_table.columnCount()}")
                
                # Try to make the table visible
                print("Forcing table visibility...")
                dialog.results_table.setVisible(True)
                dialog.results_table.show()
                dialog.results_table.raise_()
                dialog.results_table.activateWindow()
                
                print(f"Final table state: {dialog.results_table.isVisible()}")
        else:
            print("No stats list found or no items in list")
    
    # Show dialog
    dialog.show()
    
    # Auto-select after 1 second
    QTimer.singleShot(1000, auto_select_stat)
    
    # Exit after 5 seconds
    QTimer.singleShot(5000, app.quit)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    auto_test_stats()
