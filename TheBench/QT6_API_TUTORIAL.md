# Qt6 API Integration Tutorial: Building a Sports Scores App

## Overview

This tutorial teaches you how to build a sports data application using Qt6 (PyQt6) and ESPN's API. You'll learn fundamental concepts for creating desktop applications with real-time data integration, proper UI design, and accessibility features.

## Table of Contents

1. [Prerequisites and Setup](#prerequisites-and-setup)
2. [Understanding Qt6 Controls](#understanding-qt6-controls)
3. [API Integration Fundamentals](#api-integration-fundamentals)
4. [Building Your First Widget](#building-your-first-widget)
5. [Populating Controls with API Data](#populating-controls-with-api-data)
6. [Advanced UI Patterns](#advanced-ui-patterns)
7. [Accessibility Best Practices](#accessibility-best-practices)
8. [Error Handling and Robustness](#error-handling-and-robustness)
9. [Complete Example Application](#complete-example-application)

## Prerequisites and Setup

### Required Knowledge
- Basic Python programming
- Understanding of object-oriented programming
- Familiarity with JSON data structures

### Installation
```bash
pip install PyQt6 requests
```

### Project Structure
```
sports_app/
├── main.py              # Application entry point
├── api_client.py        # ESPN API integration
├── widgets.py           # Custom UI components
└── requirements.txt     # Dependencies
```

## Understanding Qt6 Controls

### Core Widget Types

Qt6 provides several fundamental widget types. Understanding when and how to use each is crucial:

#### 1. QListWidget - For Simple Lists
**Use Case**: Displaying a list of selectable items
```python
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt

# Create a list widget
league_list = QListWidget()
league_list.setAccessibleName("League Selection List")

# Add items
leagues = ["NFL", "NBA", "MLB", "NHL"]
for league in leagues:
    item = QListWidgetItem(league)
    league_list.addItem(item)

# Handle selection
def on_league_selected(item):
    selected_league = item.text()
    print(f"Selected: {selected_league}")

league_list.itemActivated.connect(on_league_selected)
```

#### 2. QTableWidget - For Structured Data
**Use Case**: Displaying tabular data with rows and columns
```python
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem

# Create table
table = QTableWidget()
table.setRowCount(3)
table.setColumnCount(4)
table.setHorizontalHeaderLabels(["Team", "Wins", "Losses", "Win %"])

# Populate data
teams_data = [
    ("Chiefs", "14", "3", ".824"),
    ("Bills", "13", "4", ".765"),
    ("Bengals", "12", "5", ".706")
]

for row, (team, wins, losses, pct) in enumerate(teams_data):
    table.setItem(row, 0, QTableWidgetItem(team))
    table.setItem(row, 1, QTableWidgetItem(wins))
    table.setItem(row, 2, QTableWidgetItem(losses))
    table.setItem(row, 3, QTableWidgetItem(pct))

# Enable sorting and selection
table.setSortingEnabled(True)
table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
```

#### 3. QTabWidget - For Organized Content
**Use Case**: Grouping related information into tabs
```python
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel

# Create tab widget
tab_widget = QTabWidget()

# Create tabs
for category in ["Offense", "Defense", "Special Teams"]:
    tab = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(QLabel(f"{category} Statistics"))
    tab.setLayout(layout)
    tab_widget.addTab(tab, category)
```

### Widget Properties and Behavior

#### Accessibility Features
```python
# Always set accessible names and descriptions
widget.setAccessibleName("Standings Table")
widget.setAccessibleDescription("Team standings with wins, losses, and win percentage")

# Add tooltips for additional context
item.setToolTip(f"Team: {team_name}, Record: {wins}-{losses}")
```

#### Selection and Navigation
```python
# Configure selection behavior
table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

# Enable keyboard navigation
list_widget.setFocus()  # Set initial focus
```

## API Integration Fundamentals

### ESPN API Structure

ESPN provides sports data through RESTful APIs. Understanding the URL patterns is essential:

```python
# Base URL pattern
BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

# League mappings
LEAGUES = {
    "NFL": "football/nfl",
    "NBA": "basketball/nba", 
    "MLB": "baseball/mlb",
    "NHL": "hockey/nhl"
}

# Common endpoints
# Scores: {BASE_URL}/{league_path}/scoreboard
# Standings: {BASE_URL}/{league_path}/standings
# Statistics: {BASE_URL}/{league_path}/leaders
```

### Basic API Client

```python
import requests
import json
from typing import Dict, List, Optional

class ESPNApiClient:
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports"
        self.leagues = {
            "NFL": "football/nfl",
            "NBA": "basketball/nba",
            "MLB": "baseball/mlb", 
            "NHL": "hockey/nhl"
        }
    
    def get_scores(self, league: str, date: str = None) -> List[Dict]:
        """Get scores for a specific league"""
        league_path = self.leagues.get(league)
        if not league_path:
            raise ValueError(f"Unsupported league: {league}")
        
        url = f"{self.base_url}/{league_path}/scoreboard"
        if date:
            url += f"?dates={date}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_scores(data)
            
        except requests.RequestException as e:
            print(f"API Error: {e}")
            return []
    
    def _parse_scores(self, data: Dict) -> List[Dict]:
        """Parse ESPN API response into simplified format"""
        games = []
        events = data.get("events", [])
        
        for event in events:
            # Extract basic game information
            competitions = event.get("competitions", [])
            if not competitions:
                continue
                
            competition = competitions[0]
            competitors = competition.get("competitors", [])
            
            if len(competitors) < 2:
                continue
            
            # Parse team information
            home_team = next((c for c in competitors if c.get("homeAway") == "home"), {})
            away_team = next((c for c in competitors if c.get("homeAway") == "away"), {})
            
            game = {
                "id": event.get("id"),
                "status": competition.get("status", {}).get("type", {}).get("description", ""),
                "home_team": {
                    "name": home_team.get("team", {}).get("displayName", ""),
                    "abbreviation": home_team.get("team", {}).get("abbreviation", ""),
                    "score": home_team.get("score", "0")
                },
                "away_team": {
                    "name": away_team.get("team", {}).get("displayName", ""),
                    "abbreviation": away_team.get("team", {}).get("abbreviation", ""),
                    "score": away_team.get("score", "0")
                }
            }
            games.append(game)
        
        return games
```

## Building Your First Widget

Let's create a simple league selector widget:

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal

class LeagueSelector(QWidget):
    # Signal emitted when a league is selected
    league_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        # Create layout
        layout = QVBoxLayout()
        
        # Add title
        title = QLabel("Select a League:")
        title.setAccessibleName("League Selection Title")
        layout.addWidget(title)
        
        # Create list widget
        self.league_list = QListWidget()
        self.league_list.setAccessibleName("Available Sports Leagues")
        self.league_list.setAccessibleDescription("List of sports leagues to view scores")
        
        # Add leagues
        leagues = ["NFL", "NBA", "MLB", "NHL"]
        for league in leagues:
            item = QListWidgetItem(league)
            self.league_list.addItem(item)
        
        # Connect selection signal
        self.league_list.itemActivated.connect(self._on_league_selected)
        
        layout.addWidget(self.league_list)
        self.setLayout(layout)
    
    def _on_league_selected(self, item):
        """Handle league selection"""
        league = item.text()
        self.league_selected.emit(league)
    
    def set_focus(self):
        """Set focus to the list for keyboard navigation"""
        self.league_list.setFocus()
        if self.league_list.count() > 0:
            self.league_list.setCurrentRow(0)
```

## Populating Controls with API Data

### Asynchronous Data Loading

For responsive UIs, load data asynchronously:

```python
from PyQt6.QtCore import QThread, pyqtSignal

class ScoresLoader(QThread):
    """Background thread for loading scores data"""
    data_loaded = pyqtSignal(list)  # Emits list of games
    error_occurred = pyqtSignal(str)  # Emits error message
    
    def __init__(self, league: str):
        super().__init__()
        self.league = league
        self.api_client = ESPNApiClient()
    
    def run(self):
        """Run in background thread"""
        try:
            scores = self.api_client.get_scores(self.league)
            self.data_loaded.emit(scores)
        except Exception as e:
            self.error_occurred.emit(str(e))

class ScoresWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.loader = None
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Select a league to view scores")
        layout.addWidget(self.status_label)
        
        # Scores table
        self.scores_table = QTableWidget()
        self.scores_table.setColumnCount(3)
        self.scores_table.setHorizontalHeaderLabels(["Away Team", "Home Team", "Status"])
        layout.addWidget(self.scores_table)
        
        self.setLayout(layout)
    
    def load_scores(self, league: str):
        """Load scores for the specified league"""
        self.status_label.setText(f"Loading {league} scores...")
        
        # Start background loading
        self.loader = ScoresLoader(league)
        self.loader.data_loaded.connect(self._on_scores_loaded)
        self.loader.error_occurred.connect(self._on_error)
        self.loader.start()
    
    def _on_scores_loaded(self, games: List[Dict]):
        """Handle successful data loading"""
        self.status_label.setText(f"Loaded {len(games)} games")
        self._populate_scores_table(games)
    
    def _on_error(self, error_message: str):
        """Handle loading errors"""
        self.status_label.setText(f"Error: {error_message}")
    
    def _populate_scores_table(self, games: List[Dict]):
        """Populate the scores table with game data"""
        self.scores_table.setRowCount(len(games))
        
        for row, game in enumerate(games):
            # Away team
            away_item = QTableWidgetItem(f"{game['away_team']['name']} {game['away_team']['score']}")
            away_item.setToolTip(f"Away: {game['away_team']['name']}")
            self.scores_table.setItem(row, 0, away_item)
            
            # Home team  
            home_item = QTableWidgetItem(f"{game['home_team']['name']} {game['home_team']['score']}")
            home_item.setToolTip(f"Home: {game['home_team']['name']}")
            self.scores_table.setItem(row, 1, home_item)
            
            # Status
            status_item = QTableWidgetItem(game['status'])
            status_item.setToolTip(f"Game status: {game['status']}")
            self.scores_table.setItem(row, 2, status_item)
        
        # Configure table
        self.scores_table.resizeColumnsToContents()
        self.scores_table.setSortingEnabled(True)
```

## Advanced UI Patterns

### Stack-Based Navigation

For complex applications with multiple views:

```python
from PyQt6.QtWidgets import QStackedWidget, QPushButton, QHBoxLayout

class SportsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.view_history = []  # For back navigation
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)
        nav_layout.addWidget(self.back_button)
        
        nav_layout.addStretch()  # Push back button to left
        
        layout.addLayout(nav_layout)
        
        # Stacked widget for different views
        self.stack = QStackedWidget()
        
        # Add views
        self.league_selector = LeagueSelector()
        self.scores_widget = ScoresWidget()
        
        self.stack.addWidget(self.league_selector)
        self.stack.addWidget(self.scores_widget)
        
        # Connect signals
        self.league_selector.league_selected.connect(self.show_scores)
        
        layout.addWidget(self.stack)
        self.setLayout(layout)
    
    def show_scores(self, league: str):
        """Show scores for selected league"""
        # Add current view to history
        current_index = self.stack.currentIndex()
        self.view_history.append(current_index)
        
        # Switch to scores view
        self.stack.setCurrentWidget(self.scores_widget)
        self.scores_widget.load_scores(league)
        
        # Enable back button
        self.back_button.setEnabled(True)
    
    def go_back(self):
        """Navigate back to previous view"""
        if self.view_history:
            previous_index = self.view_history.pop()
            self.stack.setCurrentIndex(previous_index)
            
            # Disable back button if no more history
            if not self.view_history:
                self.back_button.setEnabled(False)
```

### Modal Dialogs for Detailed Information

```python
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

class GameDetailsDialog(QDialog):
    def __init__(self, game_data: Dict, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Game Details")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Game information
        game_info = QLabel(f"{self.game_data['away_team']['name']} vs {self.game_data['home_team']['name']}")
        game_info.setAccessibleName("Game Matchup")
        layout.addWidget(game_info)
        
        # Detailed statistics table (if available)
        details_table = QTableWidget()
        # ... populate with detailed game data
        layout.addWidget(details_table)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
```

## Accessibility Best Practices

### Keyboard Navigation

```python
def keyPressEvent(self, event):
    """Handle keyboard shortcuts"""
    if event.key() == Qt.Key.Key_F5:
        self.refresh_data()
    elif event.key() == Qt.Key.Key_Escape:
        if self.view_history:
            self.go_back()
    else:
        super().keyPressEvent(event)

def setup_focus_management(self):
    """Set up proper focus order"""
    # Set tab order for keyboard navigation
    self.setTabOrder(self.league_list, self.refresh_button)
    self.setTabOrder(self.refresh_button, self.scores_table)
    
    # Set initial focus
    QTimer.singleShot(50, lambda: self.league_list.setFocus())
```

### Screen Reader Support

```python
def configure_accessibility(self, widget, name: str, description: str):
    """Configure widget for screen readers"""
    widget.setAccessibleName(name)
    widget.setAccessibleDescription(description)
    
    # Add context-specific tooltips
    if isinstance(widget, QTableWidget):
        widget.setToolTip("Use arrow keys to navigate. Press Enter to select.")
    elif isinstance(widget, QListWidget):
        widget.setToolTip("Use up/down arrows to navigate. Press Enter to select.")
```

## Error Handling and Robustness

### Graceful API Failure Handling

```python
class RobustApiClient(ESPNApiClient):
    def __init__(self):
        super().__init__()
        self.retry_count = 3
        self.timeout = 10
    
    def get_scores_with_fallback(self, league: str) -> List[Dict]:
        """Get scores with multiple endpoint fallback"""
        endpoints = [
            f"{self.base_url}/{self.leagues[league]}/scoreboard",
            f"{self.base_url}/{self.leagues[league]}/scores",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_scores(data)
            except requests.RequestException as e:
                print(f"Failed endpoint {endpoint}: {e}")
                continue
        
        # Return sample data if all endpoints fail
        return self._get_sample_data(league)
    
    def _get_sample_data(self, league: str) -> List[Dict]:
        """Provide sample data when API is unavailable"""
        if league == "NFL":
            return [
                {
                    "id": "sample1",
                    "status": "Final",
                    "home_team": {"name": "Kansas City Chiefs", "abbreviation": "KC", "score": "31"},
                    "away_team": {"name": "Buffalo Bills", "abbreviation": "BUF", "score": "24"}
                }
            ]
        # Add sample data for other leagues...
        return []
```

### User Feedback for Long Operations

```python
from PyQt6.QtWidgets import QProgressBar

class LoadingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Loading...")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def show_loading(self, message: str):
        """Show loading state"""
        self.status_label.setText(message)
        self.progress_bar.show()
        self.show()
    
    def hide_loading(self):
        """Hide loading state"""
        self.hide()
```

## Complete Example Application

Here's a complete working example that demonstrates all concepts:

```python
#!/usr/bin/env python3
"""
Complete Sports Scores Application Example
Demonstrates Qt6 controls, API integration, and accessibility
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
import requests
from typing import Dict, List

class ESPNApiClient:
    """ESPN API client for fetching sports data"""
    
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports"
        self.leagues = {
            "NFL": "football/nfl",
            "NBA": "basketball/nba",
            "MLB": "baseball/mlb",
            "NHL": "hockey/nhl"
        }
    
    def get_scores(self, league: str) -> List[Dict]:
        """Get current scores for a league"""
        league_path = self.leagues.get(league)
        if not league_path:
            return []
        
        url = f"{self.base_url}/{league_path}/scoreboard"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return self._parse_scores(data)
        except requests.RequestException:
            # Return sample data on API failure
            return self._get_sample_data(league)
    
    def _parse_scores(self, data: Dict) -> List[Dict]:
        """Parse ESPN API response"""
        games = []
        events = data.get("events", [])
        
        for event in events:
            competitions = event.get("competitions", [])
            if not competitions:
                continue
            
            competition = competitions[0]
            competitors = competition.get("competitors", [])
            
            if len(competitors) < 2:
                continue
            
            home_team = next((c for c in competitors if c.get("homeAway") == "home"), {})
            away_team = next((c for c in competitors if c.get("homeAway") == "away"), {})
            
            game = {
                "id": event.get("id"),
                "status": competition.get("status", {}).get("type", {}).get("description", ""),
                "home_team": {
                    "name": home_team.get("team", {}).get("displayName", ""),
                    "score": home_team.get("score", "0")
                },
                "away_team": {
                    "name": away_team.get("team", {}).get("displayName", ""),
                    "score": away_team.get("score", "0")
                }
            }
            games.append(game)
        
        return games
    
    def _get_sample_data(self, league: str) -> List[Dict]:
        """Sample data for demonstration"""
        sample_data = {
            "NFL": [
                {
                    "id": "sample1",
                    "status": "Final",
                    "home_team": {"name": "Kansas City Chiefs", "score": "31"},
                    "away_team": {"name": "Buffalo Bills", "score": "24"}
                }
            ],
            "NBA": [
                {
                    "id": "sample2", 
                    "status": "Final",
                    "home_team": {"name": "Los Angeles Lakers", "score": "112"},
                    "away_team": {"name": "Boston Celtics", "score": "108"}
                }
            ]
        }
        return sample_data.get(league, [])

class ScoresLoader(QThread):
    """Background thread for loading scores"""
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, league: str):
        super().__init__()
        self.league = league
        self.api_client = ESPNApiClient()
    
    def run(self):
        try:
            scores = self.api_client.get_scores(self.league)
            self.data_loaded.emit(scores)
        except Exception as e:
            self.error_occurred.emit(str(e))

class LeagueSelector(QWidget):
    """Widget for selecting sports leagues"""
    league_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Select a Sports League:")
        title.setAccessibleName("League Selection Title")
        layout.addWidget(title)
        
        # League list
        self.league_list = QListWidget()
        self.league_list.setAccessibleName("Available Sports Leagues")
        self.league_list.setAccessibleDescription("List of sports leagues to view current scores")
        
        leagues = ["NFL", "NBA", "MLB", "NHL"]
        for league in leagues:
            item = QListWidgetItem(league)
            self.league_list.addItem(item)
        
        self.league_list.itemActivated.connect(self._on_league_selected)
        layout.addWidget(self.league_list)
        
        self.setLayout(layout)
    
    def _on_league_selected(self, item):
        league = item.text()
        self.league_selected.emit(league)
    
    def set_focus(self):
        self.league_list.setFocus()
        if self.league_list.count() > 0:
            self.league_list.setCurrentRow(0)

class ScoresView(QWidget):
    """Widget for displaying scores"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.loader = None
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Loading...")
        layout.addWidget(self.status_label)
        
        # Scores table
        self.scores_table = QTableWidget()
        self.scores_table.setAccessibleName("Game Scores Table")
        self.scores_table.setAccessibleDescription("Current game scores and status")
        self.scores_table.setColumnCount(3)
        self.scores_table.setHorizontalHeaderLabels(["Away Team", "Home Team", "Status"])
        self.scores_table.setSortingEnabled(True)
        self.scores_table.setAlternatingRowColors(True)
        self.scores_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.scores_table)
        self.setLayout(layout)
    
    def load_scores(self, league: str):
        """Load scores for specified league"""
        self.status_label.setText(f"Loading {league} scores...")
        self.scores_table.setRowCount(0)
        
        self.loader = ScoresLoader(league)
        self.loader.data_loaded.connect(self._on_scores_loaded)
        self.loader.error_occurred.connect(self._on_error)
        self.loader.start()
    
    def _on_scores_loaded(self, games: List[Dict]):
        """Handle successful data loading"""
        self.status_label.setText(f"Showing {len(games)} games")
        self._populate_table(games)
    
    def _on_error(self, error_message: str):
        """Handle loading errors"""
        self.status_label.setText(f"Error loading data: {error_message}")
    
    def _populate_table(self, games: List[Dict]):
        """Populate scores table with game data"""
        self.scores_table.setRowCount(len(games))
        
        for row, game in enumerate(games):
            # Away team with score
            away_text = f"{game['away_team']['name']} {game['away_team']['score']}"
            away_item = QTableWidgetItem(away_text)
            away_item.setToolTip(f"Away: {game['away_team']['name']}")
            self.scores_table.setItem(row, 0, away_item)
            
            # Home team with score
            home_text = f"{game['home_team']['name']} {game['home_team']['score']}"
            home_item = QTableWidgetItem(home_text)
            home_item.setToolTip(f"Home: {game['home_team']['name']}")
            self.scores_table.setItem(row, 1, home_item)
            
            # Game status
            status_item = QTableWidgetItem(game['status'])
            status_item.setToolTip(f"Game status: {game['status']}")
            self.scores_table.setItem(row, 2, status_item)
        
        self.scores_table.resizeColumnsToContents()

class SportsScoresApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.view_history = []
    
    def setup_ui(self):
        self.setWindowTitle("Sports Scores Tutorial App")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Navigation bar
        nav_layout = QHBoxLayout()
        
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)
        nav_layout.addWidget(self.back_button)
        
        nav_layout.addStretch()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_current_view)
        nav_layout.addWidget(self.refresh_button)
        
        layout.addLayout(nav_layout)
        
        # Stacked widget for different views
        self.stack = QStackedWidget()
        
        # Create views
        self.league_selector = LeagueSelector()
        self.scores_view = ScoresView()
        
        self.stack.addWidget(self.league_selector)
        self.stack.addWidget(self.scores_view)
        
        # Connect signals
        self.league_selector.league_selected.connect(self.show_scores)
        
        layout.addWidget(self.stack)
        central_widget.setLayout(layout)
        
        # Set initial focus
        QTimer.singleShot(100, self.league_selector.set_focus)
    
    def show_scores(self, league: str):
        """Show scores for selected league"""
        # Save current view to history
        current_index = self.stack.currentIndex()
        self.view_history.append((current_index, league))
        
        # Switch to scores view
        self.stack.setCurrentWidget(self.scores_view)
        self.scores_view.load_scores(league)
        
        # Enable back button
        self.back_button.setEnabled(True)
        
        # Update window title
        self.setWindowTitle(f"Sports Scores - {league}")
    
    def go_back(self):
        """Navigate back to previous view"""
        if self.view_history:
            self.view_history.pop()
            
            # Go back to league selector
            self.stack.setCurrentWidget(self.league_selector)
            self.league_selector.set_focus()
            
            # Update UI state
            if not self.view_history:
                self.back_button.setEnabled(False)
            
            self.setWindowTitle("Sports Scores Tutorial App")
    
    def refresh_current_view(self):
        """Refresh the current view"""
        if self.stack.currentWidget() == self.scores_view and self.view_history:
            _, league = self.view_history[-1]
            self.scores_view.load_scores(league)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_F5:
            self.refresh_current_view()
        elif event.key() == Qt.Key.Key_Escape:
            if self.view_history:
                self.go_back()
        else:
            super().keyPressEvent(event)

def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = SportsScoresApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

## Key Takeaways

1. **Widget Selection**: Choose the right widget for your data type (QListWidget for simple lists, QTableWidget for tabular data)

2. **API Integration**: Use background threads (QThread) for network requests to keep the UI responsive

3. **Error Handling**: Always provide fallback data and graceful error handling for network failures

4. **Accessibility**: Set accessible names, descriptions, and tooltips for all interactive elements

5. **Navigation**: Implement consistent navigation patterns with proper focus management

6. **Signals and Slots**: Use Qt's signal/slot system for loose coupling between components

## Next Steps

- Explore additional Qt6 widgets (QTreeWidget, QCalendarWidget, etc.)
- Implement data caching for better performance
- Add configuration management for API endpoints
- Create custom widgets for specialized displays
- Implement automated testing for your widgets

This tutorial provides a solid foundation for building robust desktop applications with Qt6 and real-world API integration.
