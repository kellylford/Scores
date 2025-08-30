#!/usr/bin/env python3
"""
Focused test to isolate the expanded flag persistence issue
"""

import sys
from PyQt6.QtWidgets import QApplication
from services.api_service import ApiService
from models.standings import StandingsData
from accessible_table import StandingsTable

def test_flag_persistence():
    """Test if the expanded flag persists correctly"""
    
    app = QApplication(sys.argv)
    
    # Get data
    standings_list = ApiService.get_standings('MLB')
    standings_data = StandingsData(standings_list)
    
    if "AL East" in standings_data.divisions:
        teams = standings_data.divisions["AL East"]
        
        print("=== Testing expanded flag persistence ===")
        
        # Create table in basic mode
        table = StandingsTable(division_name="AL East", league="MLB", expanded=False)
        print(f"1. Initial state: expanded={table.expanded}, columns={table.columnCount()}")
        
        # Populate basic
        table.populate_standings(teams, set_focus=False)
        print(f"2. After basic populate: expanded={table.expanded}, columns={table.columnCount()}")
        
        # Try to toggle to expanded
        print(f"3. Calling set_expanded_view(True)...")
        table.set_expanded_view(True)
        print(f"4. After set_expanded_view(True): expanded={table.expanded}, columns={table.columnCount()}")
        
        # Check headers
        print(f"5. Headers after toggle:")
        for i in range(table.columnCount()):
            header = table.horizontalHeaderItem(i)
            print(f"   {i}: {header.text() if header else 'No header'}")
        
        # Repopulate
        print(f"6. Calling populate_standings again...")
        table.populate_standings(teams, set_focus=False)
        print(f"7. After repopulate: expanded={table.expanded}, columns={table.columnCount()}")
        
        # Check if data is actually expanded
        if table.rowCount() > 0:
            print(f"8. First row data:")
            for col in range(min(14, table.columnCount())):
                header = table.horizontalHeaderItem(col)
                item = table.item(0, col)
                header_text = header.text() if header else f"Col{col}"
                item_text = item.text() if item else "EMPTY"
                print(f"   {header_text}: {item_text}")
        
        # Test the expanded row building directly
        print(f"\n=== Testing row building directly ===")
        team = teams[0]
        
        # Test what _build_expanded_row would return
        try:
            # Simulate the expanded row building
            basic_row = table._build_basic_row(1, team)
            expanded_row = table._build_expanded_row(1, team)
            
            print(f"Basic row length: {len(basic_row)}")
            print(f"Expanded row length: {len(expanded_row)}")
            print(f"Basic row: {basic_row}")
            print(f"Expanded row: {expanded_row}")
            
        except Exception as e:
            print(f"Error building rows: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_flag_persistence()
