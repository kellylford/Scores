#!/usr/bin/env python3
"""
Test script to verify Teams functionality works independently
This will help us isolate the Teams dialog functionality from the main corrupted file
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QStackedWidget, QListWidgetItem, QWidget,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor

# Import our services
from services.api_service import ApiService
from models.standings import StandingsData

# Constants
DIALOG_WIDTH = 800
DIALOG_HEIGHT = 600

class StandingsLoader(QThread):
    """Background thread for loading standings data"""
    standings_loaded = pyqtSignal(object)
    loading_failed = pyqtSignal(str)
    
    def __init__(self, league: str):
        super().__init__()
        self.league = league
        
    def run(self):
        try:
            print(f"Background: Loading {self.league} standings...")
            standings_data = ApiService.get_standings(self.league)
            print(f"Background: Successfully loaded {self.league} standings")
            self.standings_loaded.emit(standings_data)
        except Exception as e:
            print(f"Background: Failed to load standings - {e}")
            self.loading_failed.emit(str(e))

class ScheduleLoader(QThread):
    """Background thread for loading team schedule data"""
    schedule_loaded = pyqtSignal(str, object)
    loading_failed = pyqtSignal(str, str)
    
    def __init__(self, league: str, team_id: str, team_name: str):
        super().__init__()
        self.league = league
        self.team_id = team_id
        self.team_name = team_name
        
    def run(self):
        try:
            print(f"Background: Loading schedule for {self.team_name}...")
            schedule_data = ApiService.get_team_schedule(self.league, self.team_id)
            print(f"Background: Successfully loaded schedule for {self.team_name}")
            self.schedule_loaded.emit(self.team_id, schedule_data)
        except Exception as e:
            print(f"Background: Failed to load schedule - {e}")
            self.loading_failed.emit(self.team_id, str(e))

class TeamsDialog(QDialog):
    """Dialog for displaying team organization by divisions"""
    
    def __init__(self, league: str, parent=None):
        super().__init__(parent)
        self.league = league
        self.current_view = "divisions"
        self.current_division = None
        self.current_team = None
        self.cached_standings = None
        self.cached_schedules = {}
        self.is_loading_standings = False
        self.is_loading_schedule = False
        
        self.setWindowTitle(f"{league} Teams")
        self.resize(DIALOG_WIDTH, DIALOG_HEIGHT)
        
        # Start background loading
        self.start_background_loading()
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        self.title_label = QLabel(f"{self.league} - Divisions")
        layout.addWidget(self.title_label)
        
        # Content area
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Navigation
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        nav_layout.addWidget(self.back_btn)
        
        nav_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        nav_layout.addWidget(close_btn)
        
        layout.addLayout(nav_layout)
        self.setLayout(layout)
        
        # Show divisions
        self.show_divisions()
        
    def start_background_loading(self):
        if not self.is_loading_standings and self.cached_standings is None:
            self.is_loading_standings = True
            self.standings_loader = StandingsLoader(self.league)
            self.standings_loader.standings_loaded.connect(self.on_standings_loaded)
            self.standings_loader.loading_failed.connect(self.on_standings_failed)
            self.standings_loader.start()
            
    def on_standings_loaded(self, standings_data):
        self.cached_standings = standings_data
        self.is_loading_standings = False
        print("Background loading completed - standings cached")
        
    def on_standings_failed(self, error_message):
        self.is_loading_standings = False
        print(f"Background loading failed: {error_message}")
        
    def show_divisions(self):
        self.current_view = "divisions"
        self.title_label.setText(f"{self.league} - Divisions")
        self.back_btn.setEnabled(False)
        
        # Clear stack
        while self.stacked_widget.count():
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
            
        # Create divisions list
        widget = QWidget()
        layout = QVBoxLayout()
        
        divisions_list = QListWidget()
        divisions_list.itemActivated.connect(self.on_division_selected)
        
        # Add divisions based on league
        if self.league == "MLB":
            divisions = ["NL East", "NL Central", "NL West", "AL East", "AL Central", "AL West"]
        elif self.league == "NFL":
            divisions = ["NFC East", "NFC North", "NFC South", "NFC West", 
                        "AFC East", "AFC North", "AFC South", "AFC West"]
        else:
            divisions = []
            
        for division in divisions:
            divisions_list.addItem(division)
            
        layout.addWidget(divisions_list)
        widget.setLayout(layout)
        
        self.stacked_widget.addWidget(widget)
        self.stacked_widget.setCurrentWidget(widget)
        
        # Focus
        if divisions_list.count() > 0:
            divisions_list.setCurrentRow(0)
            divisions_list.setFocus()
            
    def on_division_selected(self, item):
        division_name = item.text()
        self.show_teams_in_division(division_name)
        
    def show_teams_in_division(self, division_name: str):
        self.current_view = "teams"
        self.current_division = division_name
        self.title_label.setText(f"{self.league} - {division_name}")
        self.back_btn.setEnabled(True)
        
        # Clear stack
        while self.stacked_widget.count():
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
            
        # Create teams widget
        widget = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel(f"Teams in {division_name}")
        layout.addWidget(info_label)
        
        teams_list = QListWidget()
        teams_list.itemActivated.connect(self.on_team_selected)
        
        layout.addWidget(teams_list)
        widget.setLayout(layout)
        
        self.stacked_widget.addWidget(widget)
        self.stacked_widget.setCurrentWidget(widget)
        
        # Load teams
        if self.cached_standings:
            self.populate_teams_list(teams_list, division_name, self.cached_standings)
        else:
            teams_list.addItem("Loading teams...")
            # Could add fallback loading here
            
        # Focus on teams list
        QTimer.singleShot(100, lambda: self.set_teams_focus(teams_list))
        
    def populate_teams_list(self, teams_list, division_name, standings_data):
        try:
            teams_list.clear()
            standings = StandingsData(standings_data)
            
            if division_name in standings.divisions:
                teams = standings.divisions[division_name]
                for team in teams:
                    team_name = team.get('team', team.get('name', 'Unknown'))
                    wins = team.get('wins', team.get('w', 0))
                    losses = team.get('losses', team.get('l', 0))
                    
                    display_text = f"{team_name} - {wins}-{losses}"
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, team)
                    teams_list.addItem(item)
            else:
                teams_list.addItem(f"No teams found for {division_name}")
                
        except Exception as e:
            teams_list.clear()
            teams_list.addItem(f"Error: {str(e)}")
            
    def set_teams_focus(self, teams_list):
        if teams_list.count() > 0:
            teams_list.setCurrentRow(0)
            teams_list.setFocus()
            print(f"Teams list focused with {teams_list.count()} items")
            
    def on_team_selected(self, item):
        team_data = item.data(Qt.ItemDataRole.UserRole)
        if team_data:
            team_name = team_data.get('team', team_data.get('name', 'Unknown'))
            QMessageBox.information(self, "Team Selected", f"Selected: {team_name}\\n\\nSchedule and roster functionality would go here!")
            
    def go_back(self):
        if self.current_view == "teams":
            self.show_divisions()
        elif self.current_view == "schedule":
            self.show_teams_in_division(self.current_division)

def main():
    app = QApplication(sys.argv)
    
    # Test with MLB
    dialog = TeamsDialog("MLB")
    result = dialog.exec()
    
    sys.exit(0)

if __name__ == "__main__":
    main()
