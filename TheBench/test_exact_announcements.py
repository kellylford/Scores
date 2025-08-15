#!/usr/bin/env python3
"""
Detailed test showing exact smart navigation announcements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QTableWidgetItem
from accessible_table_explorer import SmartNavigationTable, AccessibilityTestResults, AccessibilityControlPanel

def test_exact_announcements():
    """Test and show exact smart navigation announcements"""
    print("=== EXACT SMART NAVIGATION ANNOUNCEMENTS TEST ===")
    
    app = QApplication([])
    
    # Create test components
    results = AccessibilityTestResults()
    control_panel = AccessibilityControlPanel(results)
    
    # Create smart navigation table
    table = SmartNavigationTable()
    table.set_control_panel(control_panel)
    
    # Set up test data matching your example
    headers = ["Player", "Pos", "AB", "H", "RBI", "BA"]
    data = [
        ["TJ Friedl", "CF", "4", "1", "0", ".251"],
        ["Jonathan India", "2B", "3", "2", "1", ".267"],
        ["Tyler Stephenson", "C", "4", "0", "0", ".189"],
        ["Spencer Steer", "3B", "4", "1", "2", ".233"],
        ["Jake Meyers", "RF", "3", "0", "0", ".245"]
    ]
    
    table.setRowCount(len(data))
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    
    for row, row_data in enumerate(data):
        for col, value in enumerate(row_data):
            item = QTableWidgetItem(str(value))
            table.setItem(row, col, item)
    
    # Register table and set smart navigation mode
    control_panel.register_table(table)
    control_panel.nav_mode.setCurrentText("Smart Navigation (Column header on row move, Row header on column move)")
    
    print("\nTesting exact announcements based on your scenario:")
    print("Starting with Spencer Steer row...")
    
    # Start at Spencer Steer, Pos column (row 3, col 1)
    table.setCurrentCell(3, 1)  # Spencer Steer, Pos = "3B"
    print(f"1. Initial position: Spencer Steer, Pos = '3B'")
    
    # Move horizontally to AB column (COLUMN navigation - should announce row context)
    table.setCurrentCell(3, 2)  # Spencer Steer, AB = "4"
    expected = "Spencer Steer: 4"
    print(f"2. HORIZONTAL move to AB column")
    print(f"   Expected announcement: '{expected}'")
    print(f"   (Row context + value, because you moved across columns)")
    
    # Move vertically to Jake Meyers AB (ROW navigation - should announce column context)
    table.setCurrentCell(4, 2)  # Jake Meyers, AB = "3"
    expected = "AB: 3"
    print(f"3. VERTICAL move to Jake Meyers AB")
    print(f"   Expected announcement: '{expected}'")
    print(f"   (Column context + value, because you moved across rows)")
    
    # Move horizontally to H column (COLUMN navigation - should announce row context)
    table.setCurrentCell(4, 3)  # Jake Meyers, H = "0"
    expected = "Jake Meyers: 0"
    print(f"4. HORIZONTAL move to H column")
    print(f"   Expected announcement: '{expected}'")
    print(f"   (Row context + value, because you moved across columns)")
    
    print(f"\nSUMMARY:")
    print(f"• COLUMN navigation (horizontal moves): Row name + value")
    print(f"• ROW navigation (vertical moves): Column name + value")
    print(f"• This gives users the context they need for their navigation direction")
    
    # Check the navigation history
    if hasattr(table, 'navigation_history') and table.navigation_history:
        print(f"\nActual announcements from navigation history:")
        for i, move in enumerate(table.navigation_history, 1):
            print(f"  {i}. {move['from']} → {move['to']} ({move['type']}): '{move['announcement']}'")
    
    app.quit()
    return True

if __name__ == "__main__":
    try:
        test_exact_announcements()
        print(f"\n✓ Test completed! Check announcements above.")
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
