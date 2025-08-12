#!/usr/bin/env python3
"""
Test script to debug table keyboard navigation issues
"""

import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt

# Add project root to sys.path
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from accessible_table import StandingsTable


class TestDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table Navigation Test")
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Create test table
        self.table = StandingsTable(self)
        
        # Add test data
        test_teams = [
            {"name": "Team 1", "wins": 50, "losses": 30, "win_pct": ".625", "games_behind": "—", "streak": "W3", "record": "50-30"},
            {"name": "Team 2", "wins": 48, "losses": 32, "win_pct": ".600", "games_behind": "2.0", "streak": "L1", "record": "48-32"},
            {"name": "Team 3", "wins": 45, "losses": 35, "win_pct": ".563", "games_behind": "5.0", "streak": "W1", "record": "45-35"},
            {"name": "Team 4", "wins": 42, "losses": 38, "win_pct": ".525", "games_behind": "8.0", "streak": "L2", "record": "42-38"},
            {"name": "Team 5", "wins": 40, "losses": 40, "win_pct": ".500", "games_behind": "10.0", "streak": "W2", "record": "40-40"},
        ]
        
        self.table.populate_standings(test_teams)
        layout.addWidget(self.table)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Set focus to table
        self.table.setFocus()
        
    def keyPressEvent(self, event):
        """Debug key events at dialog level"""
        print(f"Dialog received key: {event.key()} ({Qt.Key(event.key()).name if event.key() in Qt.Key.__members__.values() else 'Unknown'})")
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = TestDialog()
    dialog.exec()
    app.quit()
