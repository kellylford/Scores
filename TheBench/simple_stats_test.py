#!/usr/bin/env python3
"""
Simple direct test of StatisticsViewDialog functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from scores import StatisticsViewDialog

# Test without GUI to see debug output
print("Testing StatisticsViewDialog creation...")

app = QApplication(sys.argv)
dialog = StatisticsViewDialog("MLB", "player", None)

print("Dialog created successfully.")
print(f"Dialog has results_table: {hasattr(dialog, 'results_table')}")
print(f"Dialog has stats_list: {hasattr(dialog, 'stats_list')}")

if hasattr(dialog, 'stats_list'):
    print(f"Stats list count: {dialog.stats_list.count()}")
    
    if dialog.stats_list.count() > 0:
        print("Testing stat selection...")
        first_item = dialog.stats_list.item(0)
        print(f"First item: {first_item.text()}")
        
        # Simulate selection
        print("Calling _on_stat_selected...")
        dialog._on_stat_selected(first_item)
        
        print("Selection completed.")

print("Test finished.")
