#!/usr/bin/env python3
"""
Debug script to test table behavior without GUI
"""

from services.api_service import ApiService
from models.standings import StandingsData
from accessible_table import StandingsTable

def test_table_behavior():
    """Test table behavior directly"""
    
    print("Testing table toggle behavior...")
    
    # Get MLB standings
    standings_list = ApiService.get_standings('MLB')
    standings_data = StandingsData(standings_list)
    
    print(f"Retrieved {len(standings_list)} teams")
    print(f"Divisions: {list(standings_data.divisions.keys())}")
    
    if "AL East" in standings_data.divisions:
        teams = standings_data.divisions["AL East"]
        print(f"\nAL East has {len(teams)} teams")
        
        # Check team data
        team = teams[0]
        print(f"First team: {team.get('team_name', team.get('name'))}")
        print(f"Expanded fields present:")
        expanded_fields = ['runs_for', 'runs_against', 'run_differential', 'home_wins', 'home_losses', 'road_wins', 'road_losses', 'playoff_percent', 'magic_number']
        for field in expanded_fields:
            value = team.get(field, 'MISSING')
            print(f"  {field}: {value}")
        
        print(f"\n--- Testing Basic Table ---")
        # Create table in basic mode
        table = StandingsTable(division_name="AL East", league="MLB", expanded=False)
        print(f"Basic table - Columns: {table.columnCount()}, Expanded: {table.expanded}")
        
        # Populate table
        table.populate_standings(teams, set_focus=False)
        print(f"After populate - Rows: {table.rowCount()}")
        
        print(f"\n--- Testing Toggle to Expanded ---")
        # Toggle to expanded
        table.set_expanded_view(True)
        print(f"After set_expanded_view(True) - Columns: {table.columnCount()}, Expanded: {table.expanded}")
        
        # Repopulate
        table.populate_standings(teams, set_focus=False)
        print(f"After repopulate - Rows: {table.rowCount()}")
        
        # Check if expanded data is actually in the table
        if table.rowCount() > 0:
            print(f"\nChecking actual table data:")
            print(f"Table has {table.columnCount()} columns")
            
            # Print headers
            for col in range(table.columnCount()):
                header = table.horizontalHeaderItem(col)
                header_text = header.text() if header else f"Col{col}"
                print(f"  Column {col}: {header_text}")
            
            # Print first row
            print(f"\nFirst row data:")
            for col in range(table.columnCount()):
                header = table.horizontalHeaderItem(col)
                item = table.item(0, col)
                header_text = header.text() if header else f"Col{col}"
                item_text = item.text() if item else "EMPTY"
                print(f"  {header_text}: {item_text}")
        
        print(f"\n--- Testing Toggle Back to Basic ---")
        # Toggle back to basic
        table.set_expanded_view(False)
        print(f"After set_expanded_view(False) - Columns: {table.columnCount()}, Expanded: {table.expanded}")
        
        # Repopulate
        table.populate_standings(teams, set_focus=False)
        print(f"After repopulate - Rows: {table.rowCount()}, Columns: {table.columnCount()}")

if __name__ == "__main__":
    test_table_behavior()
