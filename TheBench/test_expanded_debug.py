#!/usr/bin/env python3
"""
Test script to debug expanded standings table behavior
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QRadioButton, QButtonGroup
from services.api_service import ApiService
from models.standings import StandingsData
from accessible_table import StandingsTable

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expanded Standings Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Get MLB standings data
        standings_list = ApiService.get_standings('MLB')
        self.standings_data = StandingsData(standings_list)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create radio buttons
        self.basic_radio = QRadioButton("Basic View (7 columns)")
        self.expanded_radio = QRadioButton("Expanded View (14 columns)")
        
        self.view_group = QButtonGroup()
        self.view_group.addButton(self.basic_radio, 0)
        self.view_group.addButton(self.expanded_radio, 1)
        self.basic_radio.setChecked(True)
        
        self.view_group.buttonClicked.connect(self.on_view_changed)
        
        layout.addWidget(self.basic_radio)
        layout.addWidget(self.expanded_radio)
        
        # Create table with AL East data
        self.table = StandingsTable(division_name="AL East", league="MLB", expanded=False)
        layout.addWidget(self.table)
        
        # Populate with AL East teams
        if "AL East" in self.standings_data.divisions:
            teams = self.standings_data.divisions["AL East"]
            print(f"Populating table with {len(teams)} AL East teams")
            print(f"First team expanded fields check:")
            team = teams[0]
            print(f"  runs_for: {team.get('runs_for', 'MISSING')}")
            print(f"  playoff_percent: {team.get('playoff_percent', 'MISSING')}")
            self.table.populate_standings(teams, set_focus=True)
            print(f"Table populated. Current columns: {self.table.columnCount()}")
    
    def on_view_changed(self, button):
        """Handle radio button change"""
        button_id = self.view_group.id(button)
        expanded = button_id == 1
        
        print(f"\nToggling to {'expanded' if expanded else 'basic'} view...")
        print(f"Before toggle: {self.table.columnCount()} columns, expanded={self.table.expanded}")
        
        self.table.set_expanded_view(expanded)
        
        print(f"After set_expanded_view: {self.table.columnCount()} columns, expanded={self.table.expanded}")
        
        # Repopulate with fresh data
        if "AL East" in self.standings_data.divisions:
            teams = self.standings_data.divisions["AL East"]
            self.table.populate_standings(teams, set_focus=True)
            
            print(f"After repopulation: {self.table.columnCount()} columns")
            
            # Check first row data
            if self.table.rowCount() > 0 and expanded:
                print("Expanded view first row data:")
                for col in range(min(14, self.table.columnCount())):
                    header = self.table.horizontalHeaderItem(col)
                    item = self.table.item(0, col)
                    header_text = header.text() if header else f"Col{col}"
                    item_text = item.text() if item else "EMPTY"
                    print(f"  {header_text}: {item_text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
