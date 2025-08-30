#!/usr/bin/env python3
"""
Debug script to test the actual StandingsDialog behavior
"""

import sys
from PyQt6.QtWidgets import QApplication
from services.api_service import ApiService
from scores import StandingsDialog

def test_standings_dialog():
    """Test the actual StandingsDialog"""
    
    app = QApplication(sys.argv)
    
    # Get MLB standings
    standings_list = ApiService.get_standings('MLB')
    print(f"Retrieved {len(standings_list)} MLB teams")
    
    # Create the actual dialog
    dialog = StandingsDialog(standings_list, "MLB")
    print(f"Dialog created with expanded_view = {dialog.expanded_view}")
    
    # Check if dialog has division tables
    if dialog.division_tables:
        print(f"Dialog has {len(dialog.division_tables)} division tables")
        
        # Check first table
        first_table = dialog.division_tables[0]
        print(f"First table: {first_table.division_name}")
        print(f"  Columns: {first_table.columnCount()}")
        print(f"  Expanded flag: {first_table.expanded}")
        print(f"  League: {first_table.league}")
        
        # Print headers
        print("  Headers:")
        for i in range(first_table.columnCount()):
            header = first_table.horizontalHeaderItem(i)
            print(f"    {i}: {header.text() if header else 'No header'}")
        
        # Check first row data if available
        if first_table.rowCount() > 0:
            print("  First row data:")
            for col in range(first_table.columnCount()):
                item = first_table.item(0, col)
                print(f"    Col {col}: {item.text() if item else 'EMPTY'}")
    
    # Test the toggle functionality
    print(f"\n--- Testing Toggle to Expanded ---")
    dialog._toggle_view(True)
    
    if dialog.division_tables:
        first_table = dialog.division_tables[0]
        print(f"After toggle - Columns: {first_table.columnCount()}")
        print(f"After toggle - Expanded flag: {first_table.expanded}")
        
        # Print headers after toggle
        print("  Headers after toggle:")
        for i in range(first_table.columnCount()):
            header = first_table.horizontalHeaderItem(i)
            print(f"    {i}: {header.text() if header else 'No header'}")
        
        # Check first row data after toggle
        if first_table.rowCount() > 0:
            print("  First row data after toggle:")
            for col in range(first_table.columnCount()):
                item = first_table.item(0, col)
                print(f"    Col {col}: {item.text() if item else 'EMPTY'}")

if __name__ == "__main__":
    test_standings_dialog()
