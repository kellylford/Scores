#!/usr/bin/env python3
"""
Debug script to test expanded standings functionality
"""

import sys
from PyQt6.QtWidgets import QApplication
from espn_api import get_standings
from models.standings import StandingsData
from accessible_table import StandingsTable

def test_expanded_standings():
    """Test the expanded standings table functionality"""
    
    print("Testing Expanded Standings...")
    print("=" * 50)
    
    # Get MLB standings
    print("Fetching MLB standings...")
    raw_standings = get_standings("MLB")
    print(f"Raw standings type: {type(raw_standings)}")
    print(f"Raw standings length: {len(raw_standings) if raw_standings else 0}")
    
    if raw_standings:
        print("\nFirst raw team data:")
        first_team = raw_standings[0]
        print("Available fields:", list(first_team.keys()))
        print("Sample fields:")
        for key, value in list(first_team.items())[:15]:  # Show first 15 fields
            print(f"  {key}: {value}")
        print("...")
    
    standings_data = StandingsData(raw_standings)
    
    if not standings_data:
        print("ERROR: No standings data received")
        return
        
    print(f"Got {len(standings_data.divisions)} divisions")
    
    # Test with AL East
    if "AL East" in standings_data.divisions:
        teams = standings_data.divisions["AL East"]
        print(f"\nAL East has {len(teams)} teams")
        
        # Print first team's data
        if teams:
            team = teams[0]
            print(f"\nFirst team data: {team.get('name', 'No name field')}")
            print("Available fields in team:", list(team.keys()))
            print("Full team data:", team)
    
    # Create QApplication for testing
    app = QApplication(sys.argv)
    
    # Test basic table
    print(f"\n{'='*20} BASIC TABLE TEST {'='*20}")
    basic_table = StandingsTable(division_name="AL East", league="MLB", expanded=False)
    print(f"Basic table columns: {basic_table.columnCount()}")
    for i in range(basic_table.columnCount()):
        header = basic_table.horizontalHeaderItem(i)
        print(f"  Column {i}: {header.text() if header else 'No header'}")
    
    if "AL East" in standings_data.divisions:
        basic_table.populate_standings(standings_data.divisions["AL East"])
        print(f"Basic table populated with {basic_table.rowCount()} rows")
    
    # Test expanded table
    print(f"\n{'='*20} EXPANDED TABLE TEST {'='*20}")
    expanded_table = StandingsTable(division_name="AL East", league="MLB", expanded=True)
    print(f"Expanded table columns: {expanded_table.columnCount()}")
    for i in range(expanded_table.columnCount()):
        header = expanded_table.horizontalHeaderItem(i)
        print(f"  Column {i}: {header.text() if header else 'No header'}")
    
    if "AL East" in standings_data.divisions:
        expanded_table.populate_standings(standings_data.divisions["AL East"])
        print(f"Expanded table populated with {expanded_table.rowCount()} rows")
        
        # Print first row data
        if expanded_table.rowCount() > 0:
            print("\nFirst row data:")
            for col in range(expanded_table.columnCount()):
                header = expanded_table.horizontalHeaderItem(col)
                item = expanded_table.item(0, col)
                header_text = header.text() if header else f"Col{col}"
                item_text = item.text() if item else "EMPTY"
                print(f"  {header_text}: {item_text}")
    
    # Test toggle functionality
    print(f"\n{'='*20} TOGGLE TEST {'='*20}")
    basic_table.set_expanded_view(True)
    print(f"After toggle to expanded: {basic_table.columnCount()} columns")
    for i in range(basic_table.columnCount()):
        header = basic_table.horizontalHeaderItem(i)
        print(f"  Column {i}: {header.text() if header else 'No header'}")
    
    if "AL East" in standings_data.divisions:
        basic_table.populate_standings(standings_data.divisions["AL East"])
        print(f"After repopulation: {basic_table.rowCount()} rows")

if __name__ == "__main__":
    test_expanded_standings()
