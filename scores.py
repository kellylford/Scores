"""
Scores - Sports Analysis Application
Version: 0.5.0-preview
A comprehensive sports analysis application supporting MLB and NFL
"""

__version__ = "0.51.0-preview"
__author__ = "Kelly Ford"
__description__ = "Sports Analysis Application with ESPN API integration"

import sys
import webbrowser
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Union
# Add project root to sys.path if running as script
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel,
    QHBoxLayout, QCheckBox, QDialog, QMessageBox, QTextEdit, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QStackedWidget,
    QListWidgetItem, QTreeWidget, QTreeWidgetItem, QSpinBox, QComboBox,
    QSizePolicy, QMenu
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QAction, QFont

# Windows UIA notification support
try:
    import platform
    if platform.system() == "Windows":
        import ctypes
        from ctypes import wintypes
        WINDOWS_UIA_AVAILABLE = True
    else:
        WINDOWS_UIA_AVAILABLE = False
except ImportError:
    WINDOWS_UIA_AVAILABLE = False

# New separated modules
from exceptions import ApiError, DataModelError
from services.api_service import ApiService
from models.game import GameData
from models.news import NewsData
from models.standings import StandingsData
from accessible_table import AccessibleTable, StandingsTable, LeadersTable, BoxscoreTable, InjuryTable
from windows_notifications import WindowsNotificationHelper

# Audio system for pitch mapping
try:
    from simple_audio_mapper import SimpleAudioPitchMapper as AudioPitchMapper
    from pitch_exploration_dialog import PitchExplorationDialog
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    AudioPitchMapper = None

# Constants
DETAIL_FIELDS = ["boxscore", "plays", "drives", "leaders", "standings", "odds", "injuries", "broadcasts", "news", "gameInfo"]
BASEBALL_STAT_HEADERS = ["Player", "Position", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
STANDINGS_HEADERS = ["Rank", "Team", "Wins", "Losses", "Win %", "GB", "Streak", "Record"]
TEAM_SUMMARY_HEADERS = ["Team", "Statistic", "Value"]
INJURY_HEADERS = ["Player", "Position", "Team", "Status", "Type", "Details", "Return Date"]
LEADERS_HEADERS = ["Category/Player", "Team", "Statistic", "Value"]
FOCUS_DELAY_MS = 50
WINDOW_WIDTH = 800  # Increased from 600 for better default size
WINDOW_HEIGHT = 600  # Increased from 400 for better default size
DIALOG_WIDTH = 800
DIALOG_HEIGHT = 600
NEWS_DIALOG_WIDTH = 700
NEWS_DIALOG_HEIGHT = 500
STANDINGS_DIALOG_WIDTH = 900
STANDINGS_DIALOG_HEIGHT = 600

def get_pitch_location(horizontal: int, vertical: int, batter_side: str = None) -> str:
    """Convert pitch coordinates to accessible location description
    
    CORRECTED SYSTEM based on ESPN's 3x3 grid (catcher's perspective):
    - ESPN uses ABSOLUTE coordinates (catcher's view)
    - Lower horizontal numbers = LEFT side of plate (X=80 is left edge)
    - Higher horizontal numbers = RIGHT side of plate  
    - Higher vertical numbers = LOWER pitches
    - No handedness adjustment - pure catcher's perspective positioning
    """
    if horizontal is None or vertical is None:
        return ""
    
    # Determine vertical location (height) - adjusted thresholds
    if vertical > 180:  # Lowered threshold for "low"
        height_desc = "Low"
    elif vertical < 140:  # Raised threshold for "high"
        height_desc = "High" 
    else:
        height_desc = "Middle"
    
    # Determine horizontal location (absolute positioning)
    # CORRECTED: Based on ESPN coordinate system from catcher's perspective
    # Lower X values = LEFT side, Higher X values = RIGHT side
    # Left edge of strike zone is at X=80 (based on user analysis)
    # If X=86 is "lower left" section, strike zone might be wider than initially thought
    if 90 <= horizontal <= 170:  # Strike zone center (narrower definition)
        if vertical > 180:  # Adjusted to match above
            return "Low Strike Zone"
        elif vertical < 140:  # Adjusted to match above
            return "High Strike Zone"
        else:
            return "Strike Zone Center"
    
    # No batter handedness adjustment - pure catcher's perspective
    # Lower numbers = LEFT side, Higher numbers = RIGHT side
    if horizontal < 50:
        location = "Far Left"
    elif horizontal < 90:  # Include X=86 as "Left Side"
        location = "Left Side"
    elif horizontal > 220:
        location = "Far Right"
    elif horizontal > 170:
        location = "Right Side"
    else:
        location = "Strike Zone"  # This should have been caught above, but safety net
    
    # Combine height and location
    if "Strike Zone" in location:
        return location  # Already includes height
    else:
        return f"{height_desc} {location}"

class AudioOnFocusAction(QAction):
    """Custom QAction that plays audio when highlighted in menu (for strike zone exploration)"""
    
    def __init__(self, text, parent, audio_callback, zone_id):
        super().__init__(text, parent)
        self.audio_callback = audio_callback
        self.zone_id = zone_id

class StrikeZoneMenu(QMenu):
    """Custom QMenu that plays audio when actions are highlighted"""
    
    def __init__(self, title, parent, audio_callback):
        super().__init__(title, parent)
        self.audio_callback = audio_callback
        self._last_highlighted = None
        self.setToolTipsVisible(True)
        
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # Get the action under the mouse
        action = self.actionAt(event.pos())
        if action and hasattr(action, 'zone_id') and action != self._last_highlighted:
            self._last_highlighted = action
            # Play audio for this zone with a small delay to avoid rapid-fire
            QTimer.singleShot(100, lambda: self.audio_callback(action.zone_id))
    
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        # Handle arrow key navigation
        if event.key() in [Qt.Key.Key_Up, Qt.Key.Key_Down]:
            QTimer.singleShot(50, self._play_highlighted_action_audio)
    
    def _play_highlighted_action_audio(self):
        """Play audio for currently highlighted action"""
        highlighted = self.activeAction()
        if highlighted and hasattr(highlighted, 'zone_id'):
            self.audio_callback(highlighted.zone_id)

class ConfigDialog(QDialog):
    def __init__(self, details, selected, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Game Details")
        layout = QVBoxLayout()
        self.checkboxes = {}
        for d in details:
            cb = QCheckBox(d)
            cb.setChecked(d in selected)
            layout.addWidget(cb)
            self.checkboxes[d] = cb
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
        self.setLayout(layout)
    def get_selected(self):
        return [d for d, cb in self.checkboxes.items() if cb.isChecked()]

class DatePickerDialog(QDialog):
    """Dialog for selecting a specific date to view scores"""
    
    def __init__(self, current_date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Go to Date")
        self.setModal(True)
        self.selected_date = current_date
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Instructions
        layout.addWidget(QLabel("Select a date to view scores:"))
        
        # Date controls in a horizontal layout
        date_layout = QHBoxLayout()
        
        # Month selection
        date_layout.addWidget(QLabel("Month:"))
        self.month_combo = QComboBox()
        self.month_combo.setEditable(True)  # Allow typing
        months = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        self.month_combo.addItems(months)
        self.month_combo.setCurrentIndex(self.selected_date.month - 1)
        date_layout.addWidget(self.month_combo)
        
        # Day selection
        date_layout.addWidget(QLabel("Day:"))
        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(self.selected_date.day)
        self.day_spin.setKeyboardTracking(True)  # Allow typing numbers
        date_layout.addWidget(self.day_spin)
        
        # Year selection
        date_layout.addWidget(QLabel("Year:"))
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1900, 2030)  # ESPN accepts dates back to 1900 (data available from ~1993)
        self.year_spin.setValue(self.selected_date.year)
        self.year_spin.setKeyboardTracking(True)  # Allow typing numbers
        date_layout.addWidget(self.year_spin)
        
        layout.addLayout(date_layout)
        
        # Update day range when month/year changes
        self.month_combo.currentIndexChanged.connect(self.update_day_range)
        self.year_spin.valueChanged.connect(self.update_day_range)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Go to Date")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Set focus to month combo
        self.month_combo.setFocus()
    
    def update_day_range(self):
        """Update the valid day range based on selected month and year"""
        import calendar
        
        month = self.month_combo.currentIndex() + 1
        year = self.year_spin.value()
        
        # Get the number of days in the selected month
        max_days = calendar.monthrange(year, month)[1]
        
        # Update the day spinner range
        current_day = self.day_spin.value()
        self.day_spin.setRange(1, max_days)
        
        # If current day is now invalid, set to max valid day
        if current_day > max_days:
            self.day_spin.setValue(max_days)
    
    def get_selected_date(self):
        """Get the selected date as a datetime.date object"""
        from datetime import date
        
        month = self.month_combo.currentIndex() + 1
        day = self.day_spin.value()
        year = self.year_spin.value()
        
        try:
            return date(year, month, day)
        except ValueError:
            # Invalid date, return current date
            return self.selected_date
    
    def keyPressEvent(self, event):
        """Handle Escape key to close dialog"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

class BaseView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
    
    def keyPressEvent(self, event):
        """Handle key press events for all views"""
        if event.key() == Qt.Key.Key_F5:
            self.refresh()
        elif event.key() == Qt.Key.Key_Escape:
            # Escape key goes back to previous level
            if self.parent_app and hasattr(self.parent_app, 'go_back'):
                self.parent_app.go_back()
        else:
            super().keyPressEvent(event)
    
    def setup_ui(self):
        pass
    
    def on_show(self):
        pass
    
    def refresh(self):
        """Override in subclasses to implement refresh functionality"""
        pass
    
    def set_focus_with_delay(self, w):
        QTimer.singleShot(FOCUS_DELAY_MS, lambda: w.setFocus())
    
    def set_focus_and_select_first(self, list_widget):
        """Set focus to list widget and select the first item"""
        def focus_and_select():
            list_widget.setFocus()
            if list_widget.count() > 0:
                list_widget.setCurrentRow(0)
        QTimer.singleShot(FOCUS_DELAY_MS, focus_and_select)

class HomeView(BaseView):
    """Home view showing league selection"""
    
    def keyPressEvent(self, event):
        """Handle key press events - but don't handle Escape for home view"""
        if event.key() == Qt.Key.Key_F5:
            self.refresh()
        else:
            super(BaseView, self).keyPressEvent(event)  # Skip BaseView's Escape handling
    
    def setup_ui(self):
        self.layout.addWidget(QLabel("Select a League:"))
        
        self.league_list = QListWidget()
        self.league_list.setAccessibleName("League Selection List")
        self.league_list.setAccessibleDescription("List of available sports leagues and live scores")
        
        # Add Live Scores as the first item
        live_scores_item = QListWidgetItem("Live Scores - All Sports")
        live_scores_item.setData(Qt.ItemDataRole.UserRole, "__live_scores__")
        self.league_list.addItem(live_scores_item)
        
        # Add separator
        separator_item = QListWidgetItem("─" * 30)
        separator_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-selectable
        self.league_list.addItem(separator_item)
        
        # Load leagues with error handling
        leagues = ApiService.get_leagues()
        if not leagues:
            self._show_api_error("Failed to load leagues")
            return
        
        for league in leagues:
            self.league_list.addItem(league)
        
        self.league_list.itemActivated.connect(self._on_league_selected)
        self.layout.addWidget(self.league_list)
        
        # Navigation buttons
        self._add_nav_buttons()
    
    def _on_league_selected(self, item):
        league = item.text()
        user_data = item.data(Qt.ItemDataRole.UserRole)
        
        if user_data == "__live_scores__":
            # Open Live Scores view
            if self.parent_app:
                self.parent_app.open_live_scores()
        elif self.parent_app:
            # Regular league selection
            self.parent_app.open_league(league)
    
    def _add_nav_buttons(self):
        btn_layout = QHBoxLayout()
        # Home view typically doesn't have navigation buttons
        self.layout.addLayout(btn_layout)
    
    def _show_api_error(self, message: str):
        """Show API error message to user"""
        error_label = QLabel(f"Error: {message}")
        error_label.setStyleSheet("color: red; font-weight: bold;")
        self.layout.addWidget(error_label)
    
    def on_show(self):
        self.set_focus_and_select_first(self.league_list)
    
    def refresh(self):
        """Refresh the league list"""
        self.league_list.clear()
        
        # Add Live Scores as the first item
        live_scores_item = QListWidgetItem("Live Scores - All Sports")
        live_scores_item.setData(Qt.ItemDataRole.UserRole, "__live_scores__")
        self.league_list.addItem(live_scores_item)
        
        # Add separator
        separator_item = QListWidgetItem("─" * 30)
        separator_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-selectable
        self.league_list.addItem(separator_item)
        
        leagues = ApiService.get_leagues()
        if not leagues:
            self._show_api_error("Failed to load leagues")
            return
        
        for league in leagues:
            self.league_list.addItem(league)
        
        self.set_focus_and_select_first(self.league_list)

class LiveScoresView(BaseView):
    """View showing live games from all sports"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.monitored_games = set()  # Track games being monitored for notifications
        self.game_data = {}  # Store complete game data for notifications
        self.current_time = datetime.now()
        
        # Initialize Windows UIA notification helper
        self.notification_helper = WindowsNotificationHelper()
        
        # Refresh frequency options (in milliseconds)
        self.refresh_intervals = {
            "30 seconds": 30000,
            "1 minute": 60000,
            "2 minutes": 120000,
            "Manual (F5 only)": 0
        }
        self.current_refresh_interval = 60000  # Default to 1 minute
        
        self.setup_ui()
        
        # Setup auto-refresh timer for live updates
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_live_scores)
        self._update_refresh_timer()
    
    def setup_ui(self):
        # Header with current time
        self.time_label = QLabel()
        self.layout.addWidget(self.time_label)
        
        self.layout.addWidget(QLabel("Live Scores - All Sports:"))
        
        # Refresh frequency control
        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(QLabel("Update frequency:"))
        
        self.refresh_combo = QComboBox()
        self.refresh_combo.addItems(list(self.refresh_intervals.keys()))
        self.refresh_combo.setCurrentText("1 minute")  # Default selection
        self.refresh_combo.currentTextChanged.connect(self._on_refresh_frequency_changed)
        self.refresh_combo.setAccessibleName("Refresh Frequency")
        self.refresh_combo.setAccessibleDescription("Select how often live scores should update automatically")
        refresh_layout.addWidget(self.refresh_combo)
        
        refresh_layout.addStretch()  # Push combo to the left
        self.layout.addLayout(refresh_layout)
        
        # Instructions for manual refresh
        info_label = QLabel("Press 'F5' to refresh manually")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        self.layout.addWidget(info_label)
        
        self.live_scores_list = QListWidget()
        self.live_scores_list.setAccessibleName("Live Scores List")
        self.live_scores_list.setAccessibleDescription("List of currently live games from all sports. Press Alt+M to monitor a game for notifications.")
        self.live_scores_list.itemActivated.connect(self._on_game_selected)
        self.layout.addWidget(self.live_scores_list)
        
        self._add_nav_buttons()
        self.load_live_scores()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.modifiers() == Qt.KeyboardModifier.AltModifier and event.key() == Qt.Key.Key_M:
            self._toggle_monitoring()
        elif event.key() == Qt.Key.Key_F5:
            # Provide feedback for manual refresh
            if hasattr(self, 'refresh_combo') and self.refresh_combo.currentText() == "Manual (F5 only)":
                self.notification_helper.announce("Refreshing live scores manually")
            self.refresh_live_scores()
        else:
            super().keyPressEvent(event)
    
    def _toggle_monitoring(self):
        """Toggle monitoring for the currently selected game"""
        current_item = self.live_scores_list.currentItem()
        if not current_item:
            return
            
        game_data = current_item.data(Qt.ItemDataRole.UserRole)
        if not game_data or not isinstance(game_data, dict):
            return
            
        game_id = game_data.get("id", "")
        if not game_id:
            return
        
        if game_id in self.monitored_games:
            self.monitored_games.remove(game_id)
            # Update display to remove monitoring indicator
            text = current_item.text()
            if text.endswith(" - monitoring"):
                current_item.setText(text[:-12])  # Remove " - monitoring"
            self._announce_monitoring(False, game_data)
        else:
            self.monitored_games.add(game_id)
            # Update display to show monitoring indicator
            text = current_item.text()
            if not text.endswith(" - monitoring"):
                current_item.setText(text + " - monitoring")
            self._announce_monitoring(True, game_data)
    
    def _announce_monitoring(self, monitoring: bool, game_data: dict):
        """Announce monitoring status change for accessibility"""
        game_name = game_data.get("name", "Selected game")
        
        # Use Windows UIA notifications for better accessibility
        self.notification_helper.announce_monitoring_change(game_name, monitoring)
        
        # Also update the UI
        status = "now monitoring" if monitoring else "no longer monitoring"
        message = f"{status} {game_name} for score updates"
        self.time_label.setText(f"Live Scores - {message}")
        QTimer.singleShot(3000, self._update_time_label)  # Reset after 3 seconds
    
    def _update_time_label(self):
        """Update the time label with current time"""
        self.current_time = datetime.now()
        time_str = self.current_time.strftime("%I:%M %p")
        refresh_mode = self.refresh_combo.currentText() if hasattr(self, 'refresh_combo') else "30 seconds"
        self.time_label.setText(f"Live Scores - Last updated: {time_str} (Refresh: {refresh_mode})")
    
    def _on_refresh_frequency_changed(self, frequency_text):
        """Handle refresh frequency change"""
        self.current_refresh_interval = self.refresh_intervals[frequency_text]
        self._update_refresh_timer()
        
        # Announce the change for accessibility
        if frequency_text == "Manual (F5 only)":
            message = "Automatic refresh disabled. Press F5 to refresh manually."
        else:
            message = f"Refresh frequency set to {frequency_text}"
        
        self.notification_helper.announce(message)
        self._update_time_label()  # Update the display immediately
    
    def _update_refresh_timer(self):
        """Update the refresh timer based on current interval"""
        self.refresh_timer.stop()
        
        if self.current_refresh_interval > 0:
            self.refresh_timer.start(self.current_refresh_interval)
        # If interval is 0 (manual mode), timer stays stopped
    
    def _on_game_selected(self, item):
        """Handle game selection - open game details"""
        game_data = item.data(Qt.ItemDataRole.UserRole)
        if game_data and isinstance(game_data, dict):
            game_id = game_data.get("id")
            league = game_data.get("league")
            if game_id and league and self.parent_app:
                # Set the current league for proper navigation
                self.parent_app.current_league = league
                self.parent_app.open_game_details(game_id, from_live_scores=True)
    
    def load_live_scores(self):
        """Load live scores from all sports"""
        self.live_scores_list.clear()
        self.game_data.clear()
        self._update_time_label()
        
        try:
            live_games = ApiService.get_live_scores_all_sports()
            
            if not live_games:
                self.live_scores_list.addItem("No live games currently in progress.")
                return
            
            # Group games by league for better organization
            games_by_league = {}
            for game in live_games:
                league = game.get("league", "Unknown")
                if league not in games_by_league:
                    games_by_league[league] = []
                games_by_league[league].append(game)
            
            # Add games to list, organized by league
            for league in sorted(games_by_league.keys()):
                # Always show league headers for consistency
                league_item = QListWidgetItem(f"--- {league} ---")
                league_item.setBackground(QColor(240, 240, 240))
                self.live_scores_list.addItem(league_item)
                
                for game in games_by_league[league]:
                    game_id = game.get("id", "")
                    game_name = game.get("name", "Unknown Game")
                    status = game.get("status", "")
                    teams = game.get("teams", [])
                    recent_play = game.get("recent_play", "")
                    game_league = game.get("league", "")
                    
                    # Build display text
                    display_text = f"{game_name}"
                    if teams and len(teams) >= 2:
                        team1, team2 = teams[0], teams[1]
                        score1 = team1.get("score", "")
                        score2 = team2.get("score", "")
                        if score1 and score2:
                            display_text += f" - {score1}-{score2}"
                    
                    if status and game_league not in ["NFL", "NCAAF"]:
                        display_text += f" ({status})"
                    
                    # Enhanced display for different sports
                    if recent_play:
                        if game_league in ["NFL", "NCAAF"]:
                            # Enhanced football display with two-line format
                            display_text = self._format_enhanced_football(game_name, teams, status, recent_play, game_id)
                        elif game_league == "MLB":
                            # For baseball, try to extract more detailed info
                            display_text += f" | {recent_play[:100]}"  # Longer for baseball details
                        else:
                            display_text += f" | {recent_play[:50]}"  # Truncate long plays for other sports
                    else:
                        # Standard format for games without enhanced play info
                        if status:
                            display_text += f" ({status})"
                    
                    # Note: Monitoring functionality available via Alt+M but not displayed
                    # if game_id in self.monitored_games:
                    #     display_text += " - monitoring"
                    
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, game)  # Store full game data
                    self.live_scores_list.addItem(item)
                    
                    # Store game data for monitoring
                    if game_id:
                        self.game_data[game_id] = game
                        
        except Exception as e:
            self._show_api_error(f"Failed to load live scores: {str(e)}")
    
    def refresh_live_scores(self):
        """Refresh live scores and check for changes in monitored games"""
        old_scores = {}
        
        # Capture current scores for monitored games
        for game_id in self.monitored_games:
            if game_id in self.game_data:
                game = self.game_data[game_id]
                teams = game.get("teams", [])
                if len(teams) >= 2:
                    old_scores[game_id] = (
                        teams[0].get("score", ""),
                        teams[1].get("score", "")
                    )
        
        # Reload the scores
        self.load_live_scores()
        
        # Check for score changes in monitored games
        for game_id in self.monitored_games:
            if game_id in self.game_data and game_id in old_scores:
                game = self.game_data[game_id]
                teams = game.get("teams", [])
                if len(teams) >= 2:
                    new_scores = (
                        teams[0].get("score", ""),
                        teams[1].get("score", "")
                    )
                    old_score = old_scores[game_id]
                    
                    if new_scores != old_score:
                        self._notify_score_change(game, old_score, new_scores)
    
    def _notify_score_change(self, game, old_scores, new_scores):
        """Notify about score changes in monitored games"""
        game_name = game.get("name", "Game")
        teams = game.get("teams", [])
        
        if len(teams) >= 2:
            team1_name = teams[0].get("name", "Team 1") 
            team2_name = teams[1].get("name", "Team 2")
            score_text = f"{team1_name} {new_scores[0]} - {team2_name} {new_scores[1]}"
            
            # Use Windows UIA notifications for accessibility
            self.notification_helper.notify_score_change(game_name, score_text)
            
            # Also update the UI
            self.time_label.setText(f"SCORE UPDATE: {game_name} - {score_text}")
            QTimer.singleShot(5000, self._update_time_label)  # Reset after 5 seconds
    
    def _add_nav_buttons(self):
        """Add navigation buttons"""
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh (F5)")
        refresh_btn.clicked.connect(self.refresh_live_scores)
        btn_layout.addWidget(refresh_btn)
        
        back_btn = QPushButton("Back to Home")
        back_btn.clicked.connect(lambda: self.parent_app.show_home() if self.parent_app else None)
        btn_layout.addWidget(back_btn)
        
        self.layout.addLayout(btn_layout)
    
    def on_show(self):
        """Called when view is shown"""
        self.set_focus_and_select_first(self.live_scores_list)
    
    def _show_api_error(self, message: str):
        """Show API error message to user"""
        error_label = QLabel(f"Error: {message}")
        error_label.setStyleSheet("color: red; font-weight: bold;")
        self.layout.addWidget(error_label)
    
    def _format_enhanced_football(self, game_name, teams, status, recent_play, game_id):
        """Format enhanced football display with two-line format"""
        try:
            # The recent_play already contains the hybrid format with newline separation
            # Line 1: Team names with (RZ) indicator
            # Line 2: Clock | Down & Distance | Drive Stats
            lines = recent_play.split('\n')
            
            if len(lines) >= 2:
                # Two-line format: use both lines
                team_line = lines[0]
                stats_line = lines[1]
                
                # Add status if available and not already in stats
                if status and status not in stats_line:
                    stats_line += f" ({status})"
                
                display_text = f"{team_line}\n{stats_line}"
            else:
                # Fallback to single line if format doesn't have newline
                score_text = f"{teams[0].get('name', '')} {teams[0].get('score', '')} - {teams[1].get('name', '')} {teams[1].get('score', '')}"
                if status:
                    display_text = f"{score_text} ({status}) | {recent_play}"
                else:
                    display_text = f"{score_text} | {recent_play}"
            
            return display_text
            
        except Exception as e:
            # Fallback to basic format if something goes wrong
            score_text = f"{teams[0].get('name', '')} {teams[0].get('score', '')} - {teams[1].get('name', '')} {teams[1].get('score', '')}"
            if status:
                return f"{score_text} ({status}) | {recent_play[:50]}"
            else:
                return f"{score_text} | {recent_play[:50]}"

    def refresh(self):
        """Refresh the live scores"""
        self.refresh_live_scores()

class LeagueView(BaseView):
    """View showing scores for a specific league"""
    
    def __init__(self, parent=None, league=None):
        super().__init__(parent)
        self.league = league
        self.current_date = datetime.now().date()
        self.news_headlines = []
        self.setup_ui()
    
    def setup_ui(self):
        # Date navigation label
        self.date_label = QLabel()
        self.layout.addWidget(self.date_label)
        
        self.layout.addWidget(QLabel(f"Scores for {self.league}:"))
        
        self.scores_list = QListWidget()
        self.scores_list.setAccessibleName("Scores List")
        self.scores_list.setAccessibleDescription("List of games and scores for the selected date")
        self.scores_list.itemActivated.connect(self._on_score_item_selected)
        self.layout.addWidget(self.scores_list)
        
        self._add_nav_buttons()
        self.load_scores()
    
    def _on_score_item_selected(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data == "__news__":
            self._show_news_dialog(); return
        if data == "__standings__":
            self._show_standings_dialog(); return
        if data == "__teams__":
            self._show_teams_dialog(); return
        if data and isinstance(data, str) and self.parent_app:
            self.parent_app.open_game_details(data)

    def load_scores(self):
        """Load scores for the current date"""
        self.scores_list.clear()
        date_str = self.current_date.strftime("%A, %B %d, %Y")
        self.date_label.setText(f"Date: {date_str}")
        try:
            scores_data = ApiService.get_scores(self.league, self.current_date)
            self.news_headlines = ApiService.get_news(self.league)
            if not scores_data:
                self.scores_list.addItem("No games found for this date.")
            else:
                for game_raw in scores_data:
                    game = GameData(game_raw)
                    item_text = game.get_display_text()
                    self.scores_list.addItem(item_text)
                    list_item = self.scores_list.item(self.scores_list.count()-1)
                    if list_item:
                        list_item.setData(Qt.ItemDataRole.UserRole, game_raw.get("id"))
            if self.news_headlines:
                self.scores_list.addItem("--- News Headlines ---")
                news_item = self.scores_list.item(self.scores_list.count()-1)
                news_item.setData(Qt.ItemDataRole.UserRole, "__news__")  # type: ignore
            if self.league in ["MLB", "NFL", "NBA", "NCAAF"]:
                self.scores_list.addItem("--- Standings ---")
                standings_item = self.scores_list.item(self.scores_list.count()-1)
                standings_item.setData(Qt.ItemDataRole.UserRole, "__standings__")  # type: ignore
                
                self.scores_list.addItem("--- Teams ---")
                teams_item = self.scores_list.item(self.scores_list.count()-1)
                teams_item.setData(Qt.ItemDataRole.UserRole, "__teams__")  # type: ignore
        except Exception as e:
            self._show_api_error(f"Failed to load scores: {str(e)}")

    def _show_news_dialog(self):
        """Show news dialog"""
        try:
            dialog = NewsDialog(self.news_headlines, self.league, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show news: {str(e)}")
    
    def _show_standings_dialog(self):
        """Show standings dialog with caching and fast background loading"""
        try:
            # Check cache first
            cache = DataCache()
            cached_data = cache.get_standings(self.league)
            
            if cached_data:
                # Use cached data immediately
                dialog = StandingsDialog(cached_data, self.league, self)
                dialog.exec()
            else:
                # Load in background (now fast enough to not need loading dialog)
                self.standings_loader = StandingsLoader(self.league)
                self.standings_loader.data_loaded.connect(self._on_standings_data_loaded)
                self.standings_loader.error_occurred.connect(self._on_standings_data_error)
                self.standings_loader.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show standings: {str(e)}")
    
    def _on_standings_progress(self, message: str):
        """Update standings loading progress (no longer used)"""
        pass
    
    def _on_standings_data_loaded(self, standings_data):
        """Handle standings data loaded from background thread"""
        try:
            # Cache the data
            cache = DataCache()
            cache.set_standings(self.league, standings_data)
            
            # Show the dialog immediately (no loading dialog to close)
            dialog = StandingsDialog(standings_data, self.league, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display standings: {str(e)}")
    
    def _on_standings_data_error(self, error_message):
        """Handle standings data loading error"""
        QMessageBox.warning(self, "Standings", error_message)
    
    def _show_teams_dialog(self):
        """Show teams dialog with simple tabbed interface"""
        try:
            standings_data = ApiService.get_standings(self.league)
            if not standings_data:
                QMessageBox.information(self, "Teams", 
                                      f"No teams data available for {self.league}.")
                return
            
            # Filter data by league to avoid MLB/NFL mixing
            filtered_data = [team for team in standings_data 
                           if self._is_team_for_league(team, self.league)]
            
            dialog = SimpleTeamsDialog(filtered_data, self.league, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show teams: {str(e)}")
    
    def _is_team_for_league(self, team_data: Dict, league: str) -> bool:
        """Check if team belongs to the specified league"""
        team_name = team_data.get('team_name', '')
        logo_url = team_data.get('logo', '')
        
        if league == "MLB":
            return '/mlb/' in logo_url
        elif league == "NFL":
            return '/nfl/' in logo_url
        return True  # Default to include if uncertain
    
    def previous_day(self):
        """Navigate to previous day"""
        self.current_date -= timedelta(days=1)
        self.load_scores()
        self.set_focus_and_select_first(self.scores_list)
    
    def next_day(self):
        """Navigate to next day"""
        self.current_date += timedelta(days=1)
        self.load_scores()
        self.set_focus_and_select_first(self.scores_list)
    
    def go_to_date(self):
        """Show date picker dialog and navigate to selected date"""
        try:
            dialog = DatePickerDialog(self.current_date, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_date = dialog.get_selected_date()
                if new_date != self.current_date:
                    self.current_date = new_date
                    self.load_scores()
                    self.set_focus_and_select_first(self.scores_list)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to change date: {str(e)}")
    
    def refresh(self):
        """Refresh the current view"""
        self.load_scores()
        self.set_focus_and_select_first(self.scores_list)
    
    def _add_nav_buttons(self):
        btn_layout = QHBoxLayout()
        
        back_btn = QPushButton("Back (Alt+B)")
        back_btn.setShortcut("Alt+B")
        back_btn.clicked.connect(lambda: self.parent_app.go_back() if self.parent_app else None)
        btn_layout.addWidget(back_btn)
        
        prev_btn = QPushButton("Previous Day (Alt+P)")
        prev_btn.setShortcut("Alt+P")
        prev_btn.clicked.connect(self.previous_day)
        btn_layout.addWidget(prev_btn)
        
        next_btn = QPushButton("Next Day (Alt+N)")
        next_btn.setShortcut("Alt+N")
        next_btn.clicked.connect(self.next_day)
        btn_layout.addWidget(next_btn)
        
        go_to_date_btn = QPushButton("Go to Date (Ctrl+G)")
        go_to_date_btn.setShortcut("Ctrl+G")
        go_to_date_btn.clicked.connect(self.go_to_date)
        btn_layout.addWidget(go_to_date_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(refresh_btn)
        
        self.layout.addLayout(btn_layout)
    
    def _show_api_error(self, message: str):
        """Show API error message"""
        self.scores_list.clear()
        error_item = self.scores_list.addItem(f"Error: {message}")
        QMessageBox.warning(self, "API Error", message)
    
    def keyPressEvent(self, event):
        """Handle key press events for league view"""
        if event.key() == Qt.Key.Key_G and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.go_to_date()
        else:
            # Call parent to handle F5, Escape, etc.
            super().keyPressEvent(event)
    
    def on_show(self):
        self.set_focus_and_select_first(self.scores_list)

class GameDetailsView(BaseView):
    """View showing detailed information for a specific game"""
    
    def __init__(self, parent=None, league=None, game_id=None):
        super().__init__(parent)
        self.league = league
        self.game_id = game_id
        self.config = parent.config if parent else {}
        self.raw_game_data = None  # Store raw data for drill-down access
        
        # Initialize audio pitch mapper
        self.audio_mapper = None
        if AUDIO_AVAILABLE:
            try:
                self.audio_mapper = AudioPitchMapper(self)
                self.audio_mapper.audio_generated.connect(self._on_audio_feedback)
                self.audio_mapper.audio_error.connect(self._on_audio_error)
            except Exception as e:
                print(f"Audio initialization failed: {e}")
                self.audio_mapper = None
        
        self.setup_ui()
    
    def setup_ui(self):
        self.layout.addWidget(QLabel("Game Details:"))
        
        self.details_list = QListWidget()
        self.details_list.setAccessibleName("Game Details List")
        self.details_list.setAccessibleDescription("List of detailed information about the selected game")
        self.details_list.itemActivated.connect(self._on_detail_item_selected)
        self.layout.addWidget(self.details_list)
        
        self._add_nav_buttons()
        self.load_game_details()
    
    def _on_audio_feedback(self, message):
        """Handle audio generation feedback"""
        # Provide accessible feedback about audio generation
        if hasattr(self, 'details_list'):
            self.details_list.setAccessibleDescription(f"Audio: {message}")
    
    def _on_audio_error(self, error_message):
        """Handle audio errors"""
        print(f"Audio error: {error_message}")
        # Could show a non-intrusive error message if needed
    
    def _on_detail_item_selected(self, item):
        """Handle selection of detailed data items"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        field_name = data.get("field")
        field_data = data.get("data")
        
        if not field_name or not field_data:
            return
        
        try:
            self._show_detail_dialog(field_name, field_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show {field_name} details: {str(e)}")
    
    def _show_detail_dialog(self, field_name: str, field_data: Any):
        """Show detailed data in a dialog"""
        if field_name == "standings":
            # Convert game details standings format to list format if needed
            if isinstance(field_data, dict) and "groups" in field_data:
                # Game details format - convert to list format
                standings_list = []
                for group in field_data.get("groups", []):
                    standings = group.get("standings", {})
                    entries = standings.get("entries", [])
                    for entry in entries:
                        standings_list.append(entry)
                dlg = StandingsDetailDialog(standings_list, self.league, self)
            elif isinstance(field_data, list):
                # Already in list format (from main standings)
                dlg = StandingsDetailDialog(field_data, self.league, self)
            else:
                QMessageBox.information(self, "Standings", "No standings data available.")
                return
            dlg.exec()
            return
        
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{field_name.title()} Details")
        dlg.resize(DIALOG_WIDTH, DIALOG_HEIGHT)
        layout = QVBoxLayout()
        
        # Store reference to tab widget for F6 handling
        tab_widget_ref = None
        
        if field_name == "leaders" and isinstance(field_data, list):
            self._add_leaders_data_to_layout(layout, field_data)
        elif field_name == "boxscore" and isinstance(field_data, dict):
            self._add_boxscore_data_to_layout(layout, field_data)
            # Find the tab widget that was just added
            for child in layout.children():
                if hasattr(child, 'widget') and isinstance(child.widget(), QTabWidget):
                    tab_widget_ref = child.widget()
                    break
        elif field_name == "plays" and isinstance(field_data, list):
            self._add_plays_list_to_layout(layout, field_data)
        elif field_name == "drives" and isinstance(field_data, dict):
            self._add_drives_list_to_layout(layout, field_data)
        elif field_name == "officials" and isinstance(field_data, list):
            self._add_officials_list_to_layout(layout, field_data)
        elif field_name == "injuries" and isinstance(field_data, list):
            self._add_injuries_list_to_layout(layout, field_data)
        elif field_name == "news" and isinstance(field_data, (list, dict)):
            self._add_news_list_to_layout(layout, field_data)
        else:
            # Fallback to formatted text
            text_widget = QTextEdit()
            try:
                formatted_data = ApiService.format_complex_data(field_name, field_data)
                text_widget.setPlainText(formatted_data)
            except ApiError:
                text_widget.setPlainText("Error formatting data")
            text_widget.setReadOnly(True)
            layout.addWidget(text_widget)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        
        dlg.setLayout(layout)
        
        # Add F5 refresh support for all dialogs
        original_keyPressEvent = dlg.keyPressEvent
        focus_state = {"current": "tab_bar"}  # Track current focus state for F6 navigation
        
        def custom_keyPressEvent(event):
            if event.key() == Qt.Key.Key_F5:
                # Refresh the dialog by reloading the data
                try:
                    dlg.accept()  # Close current dialog
                    # Reload and reshow
                    raw_details = ApiService.get_game_details(self.league, self.game_id)
                    updated_field_data = raw_details.get(field_name)
                    if updated_field_data:
                        self._show_detail_dialog(field_name, updated_field_data)
                except Exception as e:
                    QMessageBox.critical(self, "Refresh Error", f"Failed to refresh {field_name}: {str(e)}")
                return
            elif event.key() == Qt.Key.Key_Escape:
                # Escape closes the dialog
                dlg.reject()
                return
            
            # Handle F6 for boxscore dialogs
            if event.key() == Qt.Key.Key_F6 and field_name == "boxscore" and tab_widget_ref:
                # Cycle through: tab_bar -> first_table -> other_tables -> next_tab -> repeat
                current_tab_index = tab_widget_ref.currentIndex()
                current_widget = tab_widget_ref.widget(current_tab_index)
                
                if current_widget:
                    tables = current_widget.findChildren(BoxscoreTable)
                    
                    if focus_state["current"] == "tab_bar":
                        # Move from tab bar to first table in current tab
                        if tables and tables[0].rowCount() > 0:
                            tables[0].setFocus()
                            tables[0].setCurrentCell(0, 0)
                            focus_state["current"] = f"table_0"
                        event.accept()
                        return
                        
                    elif focus_state["current"].startswith("table_"):
                        # Currently on a table, move to next table or next tab
                        try:
                            current_table_idx = int(focus_state["current"].split("_")[1])
                            next_table_idx = current_table_idx + 1
                            
                            if next_table_idx < len(tables) and tables[next_table_idx].rowCount() > 0:
                                # Move to next table in same tab
                                tables[next_table_idx].setFocus()
                                tables[next_table_idx].setCurrentCell(0, 0)
                                focus_state["current"] = f"table_{next_table_idx}"
                            else:
                                # Move to next tab
                                next_tab_index = (current_tab_index + 1) % tab_widget_ref.count()
                                tab_widget_ref.setCurrentIndex(next_tab_index)
                                tab_widget_ref.tabBar().setFocus()
                                focus_state["current"] = "tab_bar"
                        except:
                            # Fallback to tab bar
                            tab_widget_ref.tabBar().setFocus()
                            focus_state["current"] = "tab_bar"
                        
                        event.accept()
                        return
                
                # Fallback: just go to tab bar
                tab_widget_ref.tabBar().setFocus()
                focus_state["current"] = "tab_bar"
                event.accept()
                return
                
            original_keyPressEvent(event)
            
        dlg.keyPressEvent = custom_keyPressEvent
        
        # Set focus to first table after dialog is shown (for boxscore)
        if field_name == "boxscore":
            def set_focus_to_table():
                # Find the tab widget in the dialog
                tab_widgets = dlg.findChildren(QTabWidget)
                if tab_widgets:
                    tab_widget = tab_widgets[0]
                    tab_widget.setFocus()
                    # Set focus to first table in first tab
                    first_widget = tab_widget.widget(0)
                    if first_widget:
                        tables = first_widget.findChildren(BoxscoreTable)
                        if tables and tables[0].rowCount() > 0:
                            QTimer.singleShot(100, lambda: tables[0].setFocus())
                            QTimer.singleShot(100, lambda: tables[0].setCurrentCell(0, 0))
            
            QTimer.singleShot(FOCUS_DELAY_MS, set_focus_to_table)
        
        dlg.exec()
    
    def load_game_details(self):
        """Load detailed game information"""
        self.details_list.clear()
        
        try:
            raw_details = ApiService.get_game_details(self.league, self.game_id)
            details = ApiService.extract_meaningful_game_info(raw_details)
            
            # Store raw details for export functionality
            self.current_raw_details = raw_details
            
            # Display basic game information
            self._add_basic_game_info(details)
            
            # Show configurable details
            self._add_configurable_details(raw_details)
            
        except Exception as e:
            self._show_api_error(f"Failed to load game details: {str(e)}")
    
    def _add_basic_game_info(self, details: Dict, raw_details: Dict = None):
        """Add basic game information to the details list"""
        # Display teams and records
        if 'teams' in details:
            for team in details['teams']:
                home_away = " (Home)" if team['home_away'] == 'home' else " (Away)"
                self.details_list.addItem(f"{team['name']}{home_away}")
                self.details_list.addItem(f"  Record: {team['record']}")
        
        # Game status and timing
        if 'status' in details:
            self.details_list.addItem(f"Status: {details['status']}")
        
        # Score information
        if 'scores' in details and details['scores']:
            score_display = " - ".join(details['scores'])
            self.details_list.addItem(f"Score: {score_display}")
        
        if 'detailed_status' in details and details['detailed_status'] != 'N/A':
            self.details_list.addItem(f"Game Time: {details['detailed_status']}")
        
        # Venue information
        if 'venue' in details:
            venue_info = details['venue']
            if 'venue_city' in details and details['venue_city'] != 'Unknown':
                venue_info += f" ({details['venue_city']}"
                if 'venue_state' in details and details['venue_state']:
                    venue_info += f", {details['venue_state']}"
                venue_info += ")"
            self.details_list.addItem(f"Venue: {venue_info}")
        
        # Weather is handled in the configurable details section (gameInfo) for better formatting
        # if 'weather' in details:
        #     weather_display = details['weather']
        #     if 'temperature' in details:
        #         weather_display += f", {details['temperature']}"
        #     self.details_list.addItem(f"Weather: {weather_display}")
        
        # Officials - make interactive if available
        if raw_details and 'gameInfo' in raw_details:
            game_info = raw_details['gameInfo']
            if 'officials' in game_info and isinstance(game_info['officials'], list):
                officials = game_info['officials']
                if officials:
                    officials_item = QListWidgetItem(f"Officials: {len(officials)} assigned (Press Enter for details)")
                    officials_item.setData(Qt.ItemDataRole.UserRole, {
                        "field": "officials",
                        "data": officials
                    })
                    self.details_list.addItem(officials_item)
        
        # Betting information
        if 'betting_line' in details:
            self.details_list.addItem(f"Betting Line: {details['betting_line']}")
        if 'over_under' in details:
            self.details_list.addItem(f"Over/Under: {details['over_under']}")
        
        # Broadcast info
        if 'broadcast' in details:
            self.details_list.addItem(f"TV: {details['broadcast']}")
        
        # Injuries
        if 'injuries' in details:
            self.details_list.addItem(f"Injuries: {details['injuries']}")
    
    def _add_configurable_details(self, raw_details: Dict):
        """Add all available detail fields (no longer configurable - show everything)"""
        # Show all available detail fields - be more permissive than before
        all_available_fields = []
        
        # Include ALL detail fields that have any data (even empty lists/dicts) 
        for field in DETAIL_FIELDS:
            value = raw_details.get(field)
            if value is not None:  # Include if field exists, even if empty
                all_available_fields.append(field)
        
        # Always include plays if available (even if empty, for consistency)
        if raw_details.get("plays") is not None and "plays" not in all_available_fields:
            all_available_fields.append("plays")
        
        if all_available_fields:
            self.details_list.addItem("--- Additional Details ---")
            for field in all_available_fields:
                value = raw_details.get(field, "N/A")
                if value == "N/A" or not value:
                    self.details_list.addItem(f"{field}: No data available")
                else:
                    self._add_configurable_field(field, value)
    
    def _add_configurable_field(self, field: str, value: Any):
        """Add a configurable field to the details list"""
        navigable_fields = ["standings", "leaders", "boxscore", "plays", "drives", "injuries", "news"]
        
        if field in navigable_fields:
            has_data = self._check_field_has_data(field, value)
            
            if has_data:
                item_text = f"{field.title()}"
                self.details_list.addItem(item_text)
                list_item_widget = self.details_list.item(self.details_list.count() - 1)
                if list_item_widget:
                    # For news field, pass full raw details to enable game-specific article detection
                    if field == "news" and hasattr(self, 'current_raw_details'):
                        list_item_widget.setData(Qt.ItemDataRole.UserRole, {"field": field, "data": self.current_raw_details})
                    else:
                        list_item_widget.setData(Qt.ItemDataRole.UserRole, {"field": field, "data": value})
            else:
                try:
                    formatted_value = ApiService.format_complex_data(field, value)
                    self.details_list.addItem(f"{field}: {formatted_value}")
                except ApiError:
                    self.details_list.addItem(f"{field}: Error formatting data")
        else:
            # Use enhanced formatting for simple data
            try:
                formatted_value = ApiService.format_complex_data(field, value)
                if '\n' in formatted_value:
                    self.details_list.addItem(f"{field}:")
                    for line in formatted_value.split('\n'):
                        if line.strip():
                            self.details_list.addItem(f"  {line}")
                else:
                    self.details_list.addItem(f"{field}: {formatted_value}")
            except ApiError:
                self.details_list.addItem(f"{field}: Error formatting data")
    
    def _check_field_has_data(self, field: str, value: Any) -> bool:
        """Check if a field has navigable data"""
        if field == "standings" and isinstance(value, (list, dict)):
            if isinstance(value, list):
                return len(value) > 0
            elif isinstance(value, dict):
                # Check for game details standings format (groups with standings.entries)
                groups = value.get("groups", [])
                return any(group.get("standings", {}).get("entries") for group in groups)
        elif field == "leaders":
            # ESPN leaders data is a list of teams with leader categories
            if isinstance(value, list):
                return len(value) > 0 and any(
                    isinstance(team, dict) and team.get("leaders") 
                    for team in value
                )
            elif isinstance(value, dict):
                return len(value) > 0
            return False
        elif field == "boxscore" and isinstance(value, dict):
            return bool(value.get("teams") or value.get("players"))
        elif field == "plays" and isinstance(value, list):
            return len(value) > 0
        elif field == "drives" and isinstance(value, dict):
            # NFL/NCAAF drives data - check for current drive or previous drives
            current = value.get("current")
            previous = value.get("previous", [])
            return bool(current) or len(previous) > 0
        elif field == "injuries" and isinstance(value, list):
            return len(value) > 0
        elif field == "news" and isinstance(value, (list, dict)):
            return len(value) > 0 if isinstance(value, list) else bool(value.get("articles"))
        return False
    
    def refresh(self):
        """Refresh the game details"""
        self.load_game_details()
        self.set_focus_and_select_first(self.details_list)
    
    def _add_nav_buttons(self):
        btn_layout = QHBoxLayout()
        
        back_btn = QPushButton("Back (Alt+B)")
        back_btn.setShortcut("Alt+B")
        back_btn.clicked.connect(lambda: self.parent_app.go_back() if self.parent_app else None)
        btn_layout.addWidget(back_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(refresh_btn)
        
        self.layout.addLayout(btn_layout)
    
    def _show_api_error(self, message: str):
        """Show API error message"""
        self.details_list.clear()
        error_item = self.details_list.addItem(f"Error: {message}")
        QMessageBox.warning(self, "API Error", message)
    
    def on_show(self):
        self.set_focus_and_select_first(self.details_list)
    
    def _add_standings_table_to_layout(self, layout, data):
        """Add standings table to layout"""
        standings_data = StandingsData(data)
        if not standings_data.teams:
            layout.addWidget(QLabel("No standings data available."))
            return
        
        # Check if we have division data for MLB
        has_divisions = len(standings_data.divisions) > 1 or any(
            div != "League" for div in standings_data.divisions.keys()
        )
        
        if has_divisions and hasattr(self, 'league') and self.league == "MLB":
            # Create tabbed view for divisions
            tab_widget = QTabWidget()
            tab_widget.setAccessibleName("Division Standings")
            tab_widget.setAccessibleDescription("Baseball divisions, use arrow keys to navigate between divisions")
            
            # Sort divisions for consistent ordering
            division_order = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West", "League"]
            sorted_divisions = []
            
            for div_name in division_order:
                if div_name in standings_data.divisions:
                    sorted_divisions.append((div_name, standings_data.divisions[div_name]))
            
            # Add any divisions not in our predefined order
            for div_name, teams in standings_data.divisions.items():
                if div_name not in division_order:
                    sorted_divisions.append((div_name, teams))
            
            for div_name, teams in sorted_divisions:
                if teams:  # Only create tab if there are teams
                    # Create table for this division
                    table = QTableWidget()
                    table.setColumnCount(len(STANDINGS_HEADERS))
                    table.setHorizontalHeaderLabels(STANDINGS_HEADERS)
                    table.setRowCount(len(teams))
                    
                    # Populate table with division ranking
                    for row, team_data in enumerate(teams):
                        rank = str(row + 1)  # Rank within division
                        items_data = [
                            rank,
                            team_data["name"],
                            team_data["wins"],
                            team_data["losses"],
                            team_data["win_pct"],
                            team_data["games_behind"],
                            team_data.get("streak", "N/A"),
                            team_data["record"]
                        ]
                        
                        for col, value in enumerate(items_data):
                            item = QTableWidgetItem(str(value))
                            table.setItem(row, col, item)
                    
                    # Configure table
                    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
                    table.setAlternatingRowColors(True)
                    table.verticalHeader().setVisible(False)
                    
                    # Auto-resize columns
                    header = table.horizontalHeader()
                    header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Team name stretches
                    
                    # Add table to tab
                    tab_widget.addTab(table, div_name)
            
            layout.addWidget(tab_widget)
        else:
            # Create single table for non-divisional leagues
            table = QTableWidget()
            table.setColumnCount(len(STANDINGS_HEADERS))
            table.setHorizontalHeaderLabels(STANDINGS_HEADERS)
            table.setRowCount(len(standings_data.teams))
            
            # Populate table
            for row, team_data in enumerate(standings_data.teams):
                rank = str(row + 1)
                items_data = [
                    rank,
                    team_data["name"],
                    team_data["wins"],
                    team_data["losses"],
                    team_data["win_pct"],
                    team_data["games_behind"],
                    team_data.get("streak", "N/A"),
                    team_data["record"]
                ]
                
                for col, value in enumerate(items_data):
                    item = QTableWidgetItem(str(value))
                    table.setItem(row, col, item)
            
            # Configure table
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setAlternatingRowColors(True)
            table.verticalHeader().setVisible(False)
            
            # Auto-resize columns
            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Team name stretches
            
            layout.addWidget(table)
    
    def _add_leaders_data_to_layout(self, layout, data):
        """Add leaders data to layout using ESPN's nested team structure"""
        if not data:
            layout.addWidget(QLabel("No leaders data available."))
            return
        
        # ESPN leaders data is a list of teams, each with their own leaders
        if not isinstance(data, list):
            layout.addWidget(QLabel("Leaders data format not recognized."))
            return
        
        # Create accessible table for leaders
        leaders_table = LeadersTable(parent=self)
        
        # Parse ESPN's nested structure into rows
        rows = []
        for team_data in data:
            if not isinstance(team_data, dict):
                continue
                
            team_info = team_data.get("team", {})
            team_name = team_info.get("displayName", team_info.get("abbreviation", "Unknown Team"))
            
            team_leaders = team_data.get("leaders", [])
            for category_data in team_leaders:
                if not isinstance(category_data, dict):
                    continue
                    
                category_name = category_data.get("displayName", category_data.get("name", "Unknown Category"))
                category_leaders = category_data.get("leaders", [])
                
                # Add each leader in this category
                for leader in category_leaders:
                    if not isinstance(leader, dict):
                        continue
                        
                    athlete_info = leader.get("athlete", {})
                    player_name = athlete_info.get("displayName", athlete_info.get("fullName", "Unknown Player"))
                    display_value = leader.get("displayValue", "N/A")
                    
                    rows.append([
                        category_name,
                        team_name,
                        player_name,
                        display_value
                    ])
        
        if not rows:
            layout.addWidget(QLabel("No statistical leaders found in data."))
            return
        
        # Populate the table and add to layout
        leaders_table.populate_data(rows, set_focus=True)
        layout.addWidget(leaders_table)
    
    def _add_boxscore_data_to_layout(self, layout, data):
        """Add boxscore data to layout using accessible tables with proper keyboard navigation"""
        if not data:
            layout.addWidget(QLabel("No boxscore data available."))
            return
        
        # Check if data has the expected ESPN API structure
        has_teams = isinstance(data, dict) and "teams" in data and data["teams"]
        has_players = isinstance(data, dict) and "players" in data and data["players"]
        
        if not has_teams and not has_players:
            info_label = QLabel("Boxscore data is not available for this game.\n\n"
                               "This can happen for several reasons:\n"
                               "• Game is too old (ESPN may not provide detailed statistics for older games)\n"
                               "• Game was postponed or cancelled\n"
                               "• Game has not yet started\n"
                               "• Data is temporarily unavailable from ESPN\n\n"
                               "Try checking recent games or games currently in progress for boxscore data.")
            info_label.setWordWrap(True)
            info_label.setStyleSheet("padding: 10px; color: #666; font-size: 12px;")
            layout.addWidget(info_label)
            return
        
        # Create tab widget for organized boxscore display
        tab_widget = QTabWidget()
        tab_widget.setAccessibleName("Boxscore Tabs")
        tab_widget.setAccessibleDescription("Tabbed view of team and player statistics. Use Left/Right arrow keys to navigate tabs, Tab to enter tables.")
        tab_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Process each team separately - create tabs for each team
        if has_teams or has_players:
            # Determine team names first
            team_names = []
            if has_teams:
                for team_data in data["teams"]:
                    team_name = team_data.get("team", {}).get("displayName", "Unknown Team")
                    team_names.append(team_name)
            elif has_players:
                for team_players in data["players"]:
                    team_name = team_players.get("team", {}).get("displayName", "Unknown Team")
                    team_names.append(team_name)
            
            # Create tabs for each team
            for team_idx in range(len(team_names)):
                team_name = team_names[team_idx]
                
                # Team Statistics Tab
                if has_teams and team_idx < len(data["teams"]):
                    team_data = data["teams"][team_idx]
                    team_stats = team_data.get("statistics", [])
                    
                    if team_stats:
                        team_widget = QWidget()
                        team_layout = QVBoxLayout()
                        
                        # Create team header
                        team_label = QLabel(f"=== {team_name} Team Statistics ===")
                        team_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
                        team_layout.addWidget(team_label)
                        
                        first_team_table = None  # Track first table for focus
                        
                        for stat_group in team_stats:
                            stat_type = stat_group.get("displayName", stat_group.get("name", "Team Stats"))
                            stats_array = stat_group.get("stats", [])
                            
                            if stats_array:
                                # Create team statistics table
                                team_table = BoxscoreTable(title=f"{team_name} {stat_type}")
                                team_table.setup_columns(["Statistic", "Value"])
                                
                                # Prioritize important stats by putting them first
                                important_stats = ['runs', 'hits', 'errors', 'homeRuns', 'runsBattedIn']
                                if stat_type.lower() == 'pitching':
                                    important_stats = ['earnedRuns', 'runs', 'hits', 'strikeouts', 'walks', 'homeRuns']
                                
                                stats_data = []
                                remaining_stats = []
                                
                                # First pass: find important stats
                                for stat in stats_array:
                                    stat_name = stat.get("displayName", stat.get("name", "Unknown"))
                                    stat_value = stat.get("displayValue", str(stat.get("value", "N/A")))
                                    stat_key = stat.get("name", "").lower()
                                    
                                    if any(important in stat_key for important in important_stats):
                                        stats_data.append([stat_name, stat_value])
                                    else:
                                        remaining_stats.append([stat_name, stat_value])
                                
                                # Add a separator if we have both important and remaining stats
                                if stats_data and remaining_stats:
                                    stats_data.append(["--- Other Stats ---", ""])
                                
                                # Add remaining stats
                                stats_data.extend(remaining_stats)
                                
                                # Set focus on first table created
                                should_focus = first_team_table is None
                                if should_focus:
                                    first_team_table = team_table
                                
                                team_table.populate_data(stats_data, set_focus=should_focus)
                                team_layout.addWidget(team_table)
                        
                        team_widget.setLayout(team_layout)
                        tab_widget.addTab(team_widget, f"{team_name} Stats")
                
                # Player Statistics Tabs for this team
                if has_players and team_idx < len(data["players"]):
                    team_players = data["players"][team_idx]
                    player_stats_groups = team_players.get("statistics", [])
                    
                    for stat_group in player_stats_groups:
                        stat_type = stat_group.get("type", "Unknown")
                        stat_names = stat_group.get("names", [])
                        athletes = stat_group.get("athletes", [])
                        
                        if not athletes or not stat_names:
                            continue
                        
                        # Create widget for this stat type (batting/pitching)
                        stat_widget = QWidget()
                        stat_layout = QVBoxLayout()
                        
                        # Create team header
                        team_label = QLabel(f"=== {team_name} {stat_type.title()} ===")
                        team_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
                        stat_layout.addWidget(team_label)
                        
                        # Create player statistics table
                        stat_table = BoxscoreTable(title=f"{team_name} {stat_type.title()}")
                        
                        # Build headers - Player name + position + stat names
                        headers = ["Player", "Pos"] + stat_names
                        stat_table.setup_columns(headers, stretch_column=0)
                        
                        # Build player data
                        player_data = []
                        for athlete in athletes:
                            if not athlete.get("active", True):
                                continue
                                
                            player_info = athlete.get("athlete", {})
                            player_name = player_info.get("displayName", "Unknown")
                            position = player_info.get("position", {}).get("abbreviation", "")
                            stats = athlete.get("stats", [])
                            
                            # Build row data
                            row = [player_name, position]
                            row.extend(stats)
                            player_data.append(row)
                        
                        # Set focus for first tab created
                        should_focus = tab_widget.count() == 0
                        stat_table.populate_data(player_data, set_focus=should_focus)
                        stat_layout.addWidget(stat_table)
                        
                        stat_widget.setLayout(stat_layout)
                        tab_widget.addTab(stat_widget, f"{team_name} {stat_type.title()}")
        
        # Add the tab widget to the main layout
        layout.addWidget(tab_widget)
        
        # Configure custom keyboard navigation for tab widget
        original_keyPressEvent = tab_widget.keyPressEvent
        
        def custom_keyPressEvent(event):
            key = event.key()
            
            # Handle arrow keys for tab navigation when focus is on tab bar
            if tab_widget.tabBar().hasFocus():
                if key == Qt.Key.Key_Left:
                    current = tab_widget.currentIndex()
                    new_index = (current - 1) % tab_widget.count()
                    tab_widget.setCurrentIndex(new_index)
                    event.accept()
                    return
                elif key == Qt.Key.Key_Right:
                    current = tab_widget.currentIndex()
                    new_index = (current + 1) % tab_widget.count()
                    tab_widget.setCurrentIndex(new_index)
                    event.accept()
                    return
                elif key == Qt.Key.Key_Tab:
                    # Tab from tab bar into first table of current tab
                    current_widget = tab_widget.currentWidget()
                    if current_widget:
                        tables = current_widget.findChildren(BoxscoreTable)
                        if tables:
                            tables[0].setFocus()
                            if tables[0].rowCount() > 0:
                                tables[0].setCurrentCell(0, 0)
                    event.accept()
                    return
            
            # Default handling
            original_keyPressEvent(event)
        
        tab_widget.keyPressEvent = custom_keyPressEvent
        
        # Set up initial tab focus
        if tab_widget.count() > 0:
            tab_widget.setCurrentIndex(0)
            # Focus on the tab bar initially so arrows can navigate tabs
            QTimer.singleShot(50, lambda: tab_widget.tabBar().setFocus())

    def _add_plays_list_to_layout(self, layout, data):
        """Add hierarchical play-by-play tree to layout"""
        if not data:
            layout.addWidget(QLabel("No play-by-play data available."))
            return
        
        # Store plays data for export functionality
        self.current_plays_data = data
        
        # Detect sport type from data structure or current league
        sport_type = self._detect_sport_type(data)
        
        # Add header info with export button
        header_layout = QHBoxLayout()
        info_label = QLabel(f"Play-by-Play ({len(data)} plays)")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
        header_layout.addWidget(info_label)
        
        # Add Export Game Log button
        export_btn = QPushButton("Export Game Log")
        export_btn.setAccessibleName("Export Game Log Button")
        export_btn.setAccessibleDescription("Export the complete game log as an HTML file")
        export_btn.clicked.connect(self._export_game_log)
        export_btn.setMaximumWidth(150)
        header_layout.addWidget(export_btn)
        
        # Add Pitch Audio button for baseball games
        if sport_type == 'baseball':
            pitch_audio_btn = QPushButton("Pitch Audio")
            pitch_audio_btn.setAccessibleName("Pitch Audio Button")
            pitch_audio_btn.setAccessibleDescription("Play audio for the currently selected pitch (Alt+P)")
            pitch_audio_btn.clicked.connect(lambda: self._play_current_pitch_audio(plays_tree))
            pitch_audio_btn.setMaximumWidth(120)
            header_layout.addWidget(pitch_audio_btn)
        
        header_layout.addStretch()  # Push buttons to the left
        
        layout.addLayout(header_layout)
        
        # Create tree widget for hierarchical view
        plays_tree = QTreeWidget()
        plays_tree.setAccessibleName("Play-by-Play Tree")
        plays_tree.setAccessibleDescription("Hierarchical view of game plays organized by period and drive/inning. Use up/down arrows to navigate, left/right to expand/collapse.")
        plays_tree.setHeaderLabels(["Play Description"])
        
        # Add custom event handling for better accessibility
        def on_item_expanded(item):
            # Provide accessibility feedback for expansions
            item_text = item.text(0)
            plays_tree.setAccessibleDescription(f"Expanded {item_text}. Use arrow keys to navigate children.")
        
        def on_item_collapsed(item):
            # Provide accessibility feedback for collapses
            item_text = item.text(0)
            plays_tree.setAccessibleDescription(f"Collapsed {item_text}. Use right arrow to expand.")
        
        plays_tree.itemExpanded.connect(on_item_expanded)
        plays_tree.itemCollapsed.connect(on_item_collapsed)
        
        # Add context menu for pitch audio options
        def show_context_menu(position):
            current_item = plays_tree.itemAt(position)
            if current_item:
                self._show_pitch_context_menu(current_item, plays_tree.mapToGlobal(position))
        
        def on_key_press(event):
            current_item = plays_tree.currentItem()
            
            if event.key() == Qt.Key.Key_F10 and event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Shift+F10 for context menu (works on any item)
                if current_item:
                    item_rect = plays_tree.visualItemRect(current_item)
                    self._show_pitch_context_menu(current_item, plays_tree.mapToGlobal(item_rect.center()))
                    event.accept()
                    return
            elif event.key() == Qt.Key.Key_P and event.modifiers() == Qt.KeyboardModifier.AltModifier:
                # Alt+P for pitch audio (only works on actual pitches)
                if current_item and self._is_pitch_item(current_item):
                    self._play_pitch_audio(current_item)
                    event.accept()
                    return
            elif event.key() == Qt.Key.Key_S and event.modifiers() == Qt.KeyboardModifier.AltModifier:
                # Alt+S for pitch sequence (works on pitches and at-bat items)
                if current_item:
                    is_pitch = self._is_pitch_item(current_item)
                    is_at_bat = current_item.parent() is None  # Top-level item
                    if is_pitch or is_at_bat:
                        self._play_pitch_sequence(current_item)
                        event.accept()
                        return
            # Fall back to default behavior
            plays_tree.__class__.keyPressEvent(plays_tree, event)
        
        # Enable context menu
        plays_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        plays_tree.customContextMenuRequested.connect(show_context_menu)
        plays_tree.keyPressEvent = on_key_press
        
        # Store reference for strike zone audio context
        self.current_tree_widget = plays_tree
        
        if sport_type == "MLB":
            self._build_baseball_tree(plays_tree, data)
        elif sport_type == "NFL":
            self._build_football_tree(plays_tree, data)
        else:
            # Default to generic organization
            self._build_generic_tree(plays_tree, data)
        
        layout.addWidget(plays_tree)
        
        # Set focus to the tree for better accessibility
        QTimer.singleShot(100, lambda: plays_tree.setFocus())
    
    def _add_drives_list_to_layout(self, layout, drives_data):
        """Add NFL/NCAAF drives data to layout (Football-specific method)"""
        
        def get_drive_result_info(drive):
            """Get scoring drive information with accessibility-compliant colors"""
            result = drive.get('result', '').upper()
            
            # WCAG AA compliant colors (4.5:1 contrast ratio minimum)
            if result == 'TD':
                return {
                    'icon': '🏈', 
                    'badge': 'TD 7pts', 
                    'color': QColor(0, 100, 0, 80),      # Dark green background
                    'accessible_text': 'Touchdown scoring drive'
                }
            elif result == 'FG':
                return {
                    'icon': '🥅', 
                    'badge': 'FG 3pts', 
                    'color': QColor(0, 0, 139, 60),      # Dark blue background
                    'accessible_text': 'Field goal scoring drive'
                }
            elif result == 'MISSED FG':
                return {
                    'icon': '❌', 
                    'badge': 'MISSED FG', 
                    'color': QColor(139, 0, 0, 60),      # Dark red background
                    'accessible_text': 'Missed field goal attempt'
                }
            elif result in ['FUMBLE', 'INT', 'INTERCEPTION', 'TURNOVER']:
                return {
                    'icon': '🔄', 
                    'badge': 'TURNOVER', 
                    'color': QColor(255, 140, 0, 60),    # Dark orange background
                    'accessible_text': 'Turnover drive'
                }
            elif result == 'DOWNS':
                return {
                    'icon': '🛑', 
                    'badge': '4TH DOWN', 
                    'color': QColor(255, 140, 0, 60),    # Dark orange background
                    'accessible_text': 'Turnover on downs'
                }
            elif result == 'PUNT':
                return {
                    'icon': '⚡', 
                    'badge': 'PUNT', 
                    'color': QColor(128, 128, 128, 40),  # Light gray background
                    'accessible_text': 'Punt drive'
                }
            elif result in ['END OF HALF', 'END OF GAME']:
                return {
                    'icon': '⏰', 
                    'badge': 'CLOCK', 
                    'color': QColor(128, 128, 128, 40),  # Light gray background
                    'accessible_text': 'Clock expiration drive'
                }
            elif result == 'SAFETY':
                return {
                    'icon': '🛡️', 
                    'badge': 'SAFETY 2pts', 
                    'color': QColor(128, 0, 128, 60),    # Purple background
                    'accessible_text': 'Safety scoring drive'
                }
            else:
                return {
                    'icon': '📌', 
                    'badge': result if result else 'DRIVE', 
                    'color': QColor(255, 255, 255, 0),   # No background
                    'accessible_text': 'Non-scoring drive'
                }
        
        if not drives_data:
            layout.addWidget(QLabel("No drives data available."))
            return
        
        # Handle both current drive and drive history
        all_drives = []
        
        # Add current drive if available
        current_drive = drives_data.get("current")
        if current_drive:
            all_drives.append(("Current Drive", current_drive))
        
        # Add previous drives if available
        previous_drives = drives_data.get("previous", [])
        for i, drive in enumerate(previous_drives):
            drive_num = len(previous_drives) - i  # Number drives in reverse order
            all_drives.append((f"Drive {drive_num}", drive))
        
        if not all_drives:
            layout.addWidget(QLabel("No drive data available."))
            return
        
        # Store drives data for export functionality
        self.current_drives_data = drives_data
        
        # Add header info with export button
        header_layout = QHBoxLayout()
        total_drives = len(all_drives)
        info_label = QLabel(f"Drive-by-Drive Summary ({total_drives} drives)")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
        header_layout.addWidget(info_label)
        
        # Add Export Game Log button
        export_btn = QPushButton("Export Game Log")
        export_btn.setAccessibleName("Export Game Log Button")
        export_btn.setAccessibleDescription("Export the complete game log as an HTML file")
        export_btn.clicked.connect(self._export_game_log)
        export_btn.setMaximumWidth(150)
        header_layout.addWidget(export_btn)
        header_layout.addStretch()  # Push button to the left
        
        layout.addLayout(header_layout)
        
        # Create tree widget for drives
        drives_tree = QTreeWidget()
        sport_name = "NFL/NCAAF" if self.league in ["NFL", "NCAAF"] else "Football"
        drives_tree.setAccessibleName(f"{sport_name} Drives Tree")
        drives_tree.setAccessibleDescription(f"Hierarchical view of {sport_name} drives organized by quarter. Use up/down arrows to navigate, left/right to expand/collapse.")
        drives_tree.setHeaderLabels(["Drive Summary"])
        
        # Group drives by quarter for better organization
        quarter_groups = {}
        
        for drive_label, drive in all_drives:
            if not drive or not isinstance(drive, dict):
                continue
                
            # Get drive info
            description = drive.get("description", "Unknown drive")
            team_info = drive.get("team", {})
            team_name = team_info.get("displayName", "Unknown Team")
            
            # Determine quarter from plays
            plays = drive.get("plays", [])
            quarter = "Unknown Quarter"
            if plays and len(plays) > 0:
                first_play = plays[0]
                period_info = first_play.get("period", {})
                quarter_num = period_info.get("number", "?")
                quarter = f"Quarter {quarter_num}"
            
            # Separate kickoffs from regular drive plays
            drive_plays = []
            kickoff_plays = []
            
            for play in plays:
                play_type = play.get("type", {})
                play_type_text = play_type.get("text", "").lower()
                
                if "kickoff" in play_type_text:
                    kickoff_plays.append(play)
                else:
                    drive_plays.append(play)
            
            # Group by quarter
            if quarter not in quarter_groups:
                quarter_groups[quarter] = []
            
            # Add kickoffs as separate entries
            for kickoff in kickoff_plays:
                quarter_groups[quarter].append(("Kickoff", {"plays": [kickoff]}, "Special Teams", "Kickoff", True))
            
            # Add regular drive if it has non-kickoff plays
            if drive_plays:
                modified_drive = drive.copy()
                modified_drive["plays"] = drive_plays
                quarter_groups[quarter].append((drive_label, modified_drive, team_name, description, False))
        
        # Build tree structure by quarter
        for quarter in sorted(quarter_groups.keys()):
            quarter_item = QTreeWidgetItem([quarter])
            quarter_item.setExpanded(True)
            drives_tree.addTopLevelItem(quarter_item)
            
            drives_in_quarter = quarter_groups[quarter]
            for drive_label, drive, team_name, description, is_kickoff in drives_in_quarter:
                if is_kickoff:
                    # Create kickoff item directly under quarter
                    kickoff_item = QTreeWidgetItem(["⚡ Kickoff"])
                    kickoff_item.setBackground(0, QColor(240, 240, 255))  # Light blue
                    kickoff_item.setExpanded(False)
                    quarter_item.addChild(kickoff_item)
                    
                    # Add the kickoff play
                    plays = drive.get("plays", [])
                    for play in plays:
                        play_text = play.get("text", "Unknown play")
                        
                        # Add clock context
                        clock = play.get("clock", {})
                        if clock:
                            clock_display = clock.get("displayValue", "")
                            if clock_display:
                                play_text = f"[{clock_display}] {play_text}"
                        
                        play_item = QTreeWidgetItem([play_text])
                        kickoff_item.addChild(play_item)
                else:
                    # Create enhanced drive summary node with scoring information
                    result_info = get_drive_result_info(drive)
                    
                    # Build enhanced drive summary with scoring indicators
                    enhanced_summary = f"{result_info['icon']} [{result_info['badge']}] {team_name}: {description}"
                    
                    drive_item = QTreeWidgetItem([enhanced_summary])
                    drive_item.setExpanded(False)  # Collapsed by default
                    
                    # Apply accessibility-compliant background color
                    drive_item.setBackground(0, result_info['color'])
                    
                    # Add accessible description for screen readers
                    drive_item.setToolTip(0, f"{result_info['accessible_text']}: {team_name} - {description}")
                    
                    quarter_item.addChild(drive_item)
                    
                    # Add individual plays under the drive (already filtered to exclude kickoffs)
                    plays = drive.get("plays", [])
                    for play in plays:
                        play_text = play.get("text", "Unknown play")
                        
                        # Add down and distance information for NFL plays
                        down_distance_prefix = ""
                        start = play.get("start", {})
                        
                        # For display, we want to show the situation at the START of the play
                        down = start.get("down", 0)
                        distance = start.get("distance", 0)
                        possession_text = start.get("possessionText", "")
                        yards_to_endzone = start.get("yardsToEndzone", 0)
                        
                        # Get additional NFL-specific data
                        stat_yardage = play.get("statYardage", 0)
                        play_type = play.get("type", {})
                        play_type_text = play_type.get("text", "")
                        
                        # Build enhanced play description
                        enhanced_text = play_text
                        
                        # Add yardage information if available
                        if stat_yardage != 0:
                            yardage_display = f"(+{stat_yardage} yards)" if stat_yardage > 0 else f"({stat_yardage} yards)"
                            enhanced_text = f"{yardage_display} {enhanced_text}"
                        
                        # Add play type for clarity (accessible text)
                        if play_type_text and play_type_text.lower() not in enhanced_text.lower():
                            if "pass" in play_type_text.lower():
                                enhanced_text = f"PASS: {enhanced_text}"
                            elif "rush" in play_type_text.lower():
                                enhanced_text = f"RUSH: {enhanced_text}"
                            elif "sack" in play_type_text.lower():
                                enhanced_text = f"SACK: {enhanced_text}"
                            elif "penalty" in play_type_text.lower():
                                enhanced_text = f"PENALTY: {enhanced_text}"
                            elif "punt" in play_type_text.lower():
                                enhanced_text = f"PUNT: {enhanced_text}"
                            elif "field goal" in play_type_text.lower():
                                enhanced_text = f"FIELD GOAL: {enhanced_text}"
                        
                        # Add situational context
                        situation_prefix = ""
                        if yards_to_endzone <= 5:
                            situation_prefix = "GOAL LINE "
                        elif yards_to_endzone <= 20:
                            situation_prefix = "RED ZONE "
                        elif down == 4:
                            situation_prefix = "4TH DOWN "
                        
                        # Use start data for down/distance display (not end!)
                        if down > 0:  # Regular downs
                            if possession_text:
                                if situation_prefix:
                                    down_distance_prefix = f"[{situation_prefix}{down} & {distance} from {possession_text}] "
                                else:
                                    down_distance_prefix = f"[{down} & {distance} from {possession_text}] "
                            else:
                                down_distance_prefix = f"[{situation_prefix}{down} & {distance}] "
                        
                        # Add extra context for key plays
                        if play.get("scoringPlay"):
                            away_score = play.get("awayScore", 0)
                            home_score = play.get("homeScore", 0)
                            play_text = f"TOUCHDOWN: {down_distance_prefix}{enhanced_text} ({away_score}-{home_score})"
                        else:
                            play_text = f"{down_distance_prefix}{enhanced_text}"
                        
                        # Add clock context
                        clock = play.get("clock", {})
                        if clock:
                            clock_display = clock.get("displayValue", "")
                            if clock_display:
                                play_text = f"[{clock_display}] {play_text}"
                        
                        play_item = QTreeWidgetItem([play_text])
                        
                        # Highlight scoring plays
                        if play.get("scoringPlay"):
                            play_item.setBackground(0, QColor(255, 255, 150))  # Light yellow
                        # Highlight goal line plays
                        elif yards_to_endzone <= 5:
                            play_item.setBackground(0, QColor(255, 240, 240))  # Light red
                        # Highlight red zone plays  
                        elif yards_to_endzone <= 20:
                            play_item.setBackground(0, QColor(255, 250, 240))  # Light orange
                        
                        drive_item.addChild(play_item)
        
        layout.addWidget(drives_tree)
    
    def _detect_sport_type(self, data):
        """Detect sport type from play data or current league"""
        if hasattr(self, 'league') and self.league:
            return self.league
        
        # Try to detect from data structure
        if data and len(data) > 0:
            sample_play = data[0]
            period = sample_play.get("period", {})
            period_display = period.get("displayValue", "")
            
            if "inning" in period_display.lower():
                return "MLB"
            elif "quarter" in period_display.lower():
                return "NFL"
        
        return "Generic"
    
    def _build_baseball_tree(self, plays_tree, data):
        """Build baseball-specific hierarchical tree with enhanced information"""
        # Group plays by inning/period
        inning_groups = {}
        for play in data:
            period_info = play.get("period", {})
            period_number = period_info.get("number", 0)
            period_display = period_info.get("displayValue", f"Period {period_number}")
            period_type = period_info.get("type", "Unknown").lower()
            
            if period_display not in inning_groups:
                inning_groups[period_display] = {"top": [], "bottom": []}
            
            # Use the actual period type from ESPN data
            if period_type == "top":
                inning_groups[period_display]["top"].append(play)
            elif period_type == "bottom":
                inning_groups[period_display]["bottom"].append(play)
            else:
                # Fallback for other sports or unknown types
                inning_groups[period_display]["top"].append(play)
        
        # Calculate running scores and pitcher info
        score_tracker = self._calculate_running_scores(data)
        
        # Build tree structure
        for period_display in sorted(inning_groups.keys(), key=lambda x: int(x.split()[0][:-2]) if x.split()[0][:-2].isdigit() else 0):
            inning_item = QTreeWidgetItem([period_display])
            inning_item.setExpanded(True)  # Expand by default
            plays_tree.addTopLevelItem(inning_item)
            
            period_data = inning_groups[period_display]
            inning_num = period_display.split()[0]  # "1st", "2nd", etc.
            
            # Add top half (if any plays)
            if period_data["top"]:
                # Get score after top half and pitcher info
                half_key = f"{period_display}_top"
                score_info = score_tracker.get(half_key, {})
                pitcher_info = self._extract_pitcher_info(period_data["top"])
                
                # Create enhanced label with score and pitcher
                label = self._create_enhanced_half_inning_label(f"Top of the {inning_num}", score_info, pitcher_info)
                top_item = QTreeWidgetItem([label])
                top_item.setExpanded(True)
                inning_item.addChild(top_item)
                self._add_baseball_plays_to_tree_group(top_item, period_data["top"])
            
            # Add bottom half (if any plays)
            if period_data["bottom"]:
                # Get score after bottom half and pitcher info
                half_key = f"{period_display}_bottom"
                score_info = score_tracker.get(half_key, {})
                pitcher_info = self._extract_pitcher_info(period_data["bottom"])
                
                # Create enhanced label with score and pitcher
                label = self._create_enhanced_half_inning_label(f"Bottom of the {inning_num}", score_info, pitcher_info)
                bottom_item = QTreeWidgetItem([label])
                bottom_item.setExpanded(True)
                inning_item.addChild(bottom_item)
                self._add_baseball_plays_to_tree_group(bottom_item, period_data["bottom"])
    
    def _calculate_running_scores(self, plays_data):
        """Calculate running scores after each half-inning"""
        score_tracker = {}
        home_score = 0
        away_score = 0
        
        # Group plays by inning and half for scoring calculations
        for play in plays_data:
            period_info = play.get("period", {})
            period_display = period_info.get("displayValue", "Unknown")
            period_type = period_info.get("type", "Unknown").lower()
            
            # Track scoring plays
            if play.get("scoringPlay", False):
                # Extract runs scored from play text
                runs_scored = self._extract_runs_from_play(play.get("text", ""))
                team_id = play.get("team", {}).get("id")
                
                # Determine if home or away team scored
                if self._is_home_team_batting(period_type):
                    home_score += runs_scored
                else:
                    away_score += runs_scored
            
            # Store score after this half-inning
            half_key = f"{period_display}_{period_type}"
            score_tracker[half_key] = {
                "home": home_score,
                "away": away_score,
                "total_runs": home_score + away_score
            }
        
        return score_tracker
    
    def _extract_runs_from_play(self, play_text):
        """Extract number of runs scored from a play description"""
        import re
        # Look for patterns like "scores", "2 runs score", etc.
        if "scores" in play_text.lower():
            # Try to find number before "run" or "runs"
            match = re.search(r'(\d+)\s+runs?\s+score', play_text.lower())
            if match:
                return int(match.group(1))
            # Single run if just "scores"
            return 1
        return 0
    
    def _is_home_team_batting(self, period_type):
        """Determine if home team is batting based on period type"""
        return period_type == "bottom"
    
    def _extract_pitcher_info(self, half_inning_plays):
        """Extract pitcher information from half-inning plays"""
        pitcher_name = "Unknown"
        pitcher_changes = []
        
        for play in half_inning_plays:
            play_text = play.get("text", "")
            
            # Look for pitcher announcements
            if " pitches to " in play_text:
                parts = play_text.split(" pitches to ")
                if len(parts) >= 2:
                    pitcher_name = parts[0].strip()
                    break
            
            # Look for pitching changes
            if "pitching change" in play_text.lower() or "new pitcher" in play_text.lower():
                pitcher_changes.append(play_text)
        
        return {
            "pitcher": pitcher_name,
            "changes": pitcher_changes
        }
    
    def _create_enhanced_half_inning_label(self, base_label, score_info, pitcher_info):
        """Create enhanced label with score and pitcher information"""
        label_parts = [base_label]
        
        # Add score information if available
        if score_info and score_info.get("total_runs", 0) > 0:
            away_score = score_info.get("away", 0)
            home_score = score_info.get("home", 0)
            label_parts.append(f"({away_score}-{home_score})")
        
        # Add pitcher information if available
        pitcher = pitcher_info.get("pitcher")
        if pitcher and pitcher != "Unknown":
            # Keep it concise - just last name if possible
            pitcher_parts = pitcher.split()
            display_pitcher = pitcher_parts[-1] if pitcher_parts else pitcher
            label_parts.append(f"- {display_pitcher} pitching")
        
        return " ".join(label_parts)
    
    def _build_football_tree(self, plays_tree, data):
        """Build NFL-specific hierarchical tree"""
        # Group plays by quarter and drive
        quarter_groups = {}
        
        for play in data:
            period_info = play.get("period", {})
            period_number = period_info.get("number", 1)
            period_display = period_info.get("displayValue", f"{period_number}Q")
            
            drive_number = play.get("driveNumber", "Unknown")
            drive_team = play.get("team", {}).get("id", "Unknown")
            
            if period_display not in quarter_groups:
                quarter_groups[period_display] = {}
            
            drive_key = f"Drive {drive_number} (Team {drive_team})"
            if drive_key not in quarter_groups[period_display]:
                quarter_groups[period_display][drive_key] = []
            
            quarter_groups[period_display][drive_key].append(play)
        
        # Build tree structure
        for period_display in sorted(quarter_groups.keys()):
            quarter_item = QTreeWidgetItem([period_display])
            quarter_item.setExpanded(True)
            plays_tree.addTopLevelItem(quarter_item)
            
            drives = quarter_groups[period_display]
            for drive_key in sorted(drives.keys()):
                drive_plays = drives[drive_key]
                if drive_plays:
                    # Determine drive result
                    drive_result = self._determine_drive_result(drive_plays)
                    drive_display = f"{drive_key}: {drive_result}" if drive_result else drive_key
                    
                    drive_item = QTreeWidgetItem([drive_display])
                    drive_item.setExpanded(False)  # Collapsed by default
                    quarter_item.addChild(drive_item)
                    
                    self._add_football_plays_to_drive(drive_item, drive_plays)
    
    def _build_generic_tree(self, plays_tree, data):
        """Build generic hierarchical tree for unknown sports"""
        # Group by period only
        period_groups = {}
        for play in data:
            period_info = play.get("period", {})
            period_display = period_info.get("displayValue", "Unknown Period")
            
            if period_display not in period_groups:
                period_groups[period_display] = []
            period_groups[period_display].append(play)
        
        # Build simple tree
        for period_display in sorted(period_groups.keys()):
            period_item = QTreeWidgetItem([period_display])
            period_item.setExpanded(True)
            plays_tree.addTopLevelItem(period_item)
            
            for play in period_groups[period_display]:
                play_text = play.get("text", "Unknown play")
                play_item = QTreeWidgetItem([play_text])
                period_item.addChild(play_item)
    
    def _add_baseball_plays_to_tree_group(self, parent_item, plays):
        """Add plays to a tree group, organizing by at-bat with result as main node"""
        # Filter out transition plays (inning markers, etc.)
        meaningful_plays = []
        for play in plays:
            play_text = play.get("text", "")
            
            # Skip inning transition markers and empty plays
            if (play_text.startswith("Top of the") or 
                play_text.startswith("Bottom of the") or 
                play_text.startswith("End of the") or
                play_text.startswith("Middle of the") or
                not play_text.strip()):
                continue
                
            meaningful_plays.append(play)
        
        # Group plays by at-bat
        at_bats = []
        current_at_bat = None
        
        for play in meaningful_plays:
            play_text = play.get("text", "")
            
            # Check if this is a batter announcement (start of new at-bat)
            if " pitches to " in play_text:
                # End previous at-bat if exists
                if current_at_bat:
                    at_bats.append(current_at_bat)
                
                # Start new at-bat
                parts = play_text.split(" pitches to ")
                if len(parts) >= 2:
                    batter_name = parts[1].strip()
                    current_at_bat = {
                        "batter": batter_name,
                        "plays": [],
                        "result": None,
                        "scoring": False
                    }
                continue
            
            # Add play to current at-bat
            if current_at_bat:
                current_at_bat["plays"].append(play)
                
                # Check if this is the result play (final outcome)
                # Look for player name in the play text to identify result plays
                batter_name = current_at_bat["batter"]
                name_words = batter_name.split()
                
                # Check if any part of the player's name appears in the play text
                name_found_in_play = any(name_part.lower() in play_text.lower() 
                                       for name_part in name_words if len(name_part) > 2)
                
                if name_found_in_play or any(outcome in play_text.lower() for outcome in 
                       ["struck out", "grounded out", "flied out", "popped out", "lined out", 
                        "fouled out", "reached on error", "singled", "doubled", "tripled", "homered",
                        "walked", "hit by pitch", "reached on fielder's choice", "reached on",
                        "grounded into", "flied into", "popped into", "lined into", "single to", "double to"]):
                    current_at_bat["result"] = play_text
                    if play.get("scoringPlay", False):
                        current_at_bat["scoring"] = True
                        current_at_bat["score"] = f"({play.get('awayScore', 0)}-{play.get('homeScore', 0)})"
                    
                    # End this at-bat
                    at_bats.append(current_at_bat)
                    current_at_bat = None
        
        # Add any remaining at-bat
        if current_at_bat:
            # If no clear result, use last play as result
            if current_at_bat["plays"] and not current_at_bat["result"]:
                last_play = current_at_bat["plays"][-1]
                current_at_bat["result"] = last_play.get("text", "At-bat in progress")
            at_bats.append(current_at_bat)
        
        # Create tree nodes for each at-bat
        for at_bat in at_bats:
            if not at_bat["batter"] or not at_bat["result"]:
                continue
                
            # Create main node with batter name and result
            result_text = at_bat["result"]
            if at_bat["scoring"]:
                main_text = f"⚾ {at_bat['batter']}: {result_text} {at_bat.get('score', '')}"
            else:
                main_text = f"{at_bat['batter']}: {result_text}"
            
            at_bat_item = QTreeWidgetItem([main_text])
            at_bat_item.setExpanded(False)  # Collapsed by default
            
            # Highlight scoring at-bats
            if at_bat["scoring"]:
                at_bat_item.setBackground(0, QColor(255, 255, 150))  # Light yellow
            
            parent_item.addChild(at_bat_item)
            
            # Add pitch-by-pitch details as children (excluding the result play)
            pitch_count = 0
            for play in at_bat["plays"]:
                play_text = play.get("text", "")
                
                # Skip the result play since it's already in the main node
                if play_text == at_bat["result"]:
                    continue
                
                # Add pitch details
                if "Pitch" in play_text or any(pitch_type in play_text.lower() for pitch_type in 
                                             ["ball", "strike", "foul", "looking", "swinging"]):
                    pitch_count += 1
                    
                    # Extract additional pitch details if available
                    enhanced_text = play_text
                    velocity = play.get("pitchVelocity")
                    pitch_type = play.get("pitchType", {})
                    pitch_type_text = pitch_type.get("text", "") if isinstance(pitch_type, dict) else ""
                    pitch_coordinate = play.get("pitchCoordinate", {})
                    
                    # Get pitch location with absolute coordinates
                    location = ""
                    if pitch_coordinate and isinstance(pitch_coordinate, dict):
                        espn_x = pitch_coordinate.get("x")  # Horizontal (absolute)
                        espn_y = pitch_coordinate.get("y")  # Vertical (absolute)
                        if espn_x is not None and espn_y is not None:
                            # Try to determine batter handedness
                            batter_side = None
                            
                            # Check if we can extract batter info from the play data
                            if isinstance(play, dict) and 'participants' in play:
                                for participant in play.get('participants', []):
                                    if isinstance(participant, dict) and participant.get('type') == 'batter':
                                        batter_side = participant.get('batSide')
                                        break
                            
                            # For now, use simple heuristics for known players
                            # TODO: Improve batter data extraction from ESPN API
                            if not batter_side:
                                batter_name = at_bat.get('batter', '') if isinstance(at_bat, dict) else ''
                                if 'Lindor' in batter_name:
                                    batter_side = 'L'  # Based on our hit-by-pitch analysis
                                # Add more known players as needed
                            
                            # Get location with batter context  
                            location = get_pitch_location(espn_x, espn_y, batter_side)
                    
                    # Build enhanced text with velocity, type, and coordinates
                    # Note: location now contains coordinates, so no need for separate coordinates_text
                    details = []
                    if velocity:
                        details.append(f"{velocity} mph")
                    if pitch_type_text:
                        details.append(pitch_type_text)
                    
                        # Show only raw coordinates if available
                        coord_text = ""
                        if espn_x is not None and espn_y is not None:
                            coord_text = f"({espn_x}, {espn_y})"
                        if details:
                            detail_text = " ".join(details)
                            if coord_text:
                                enhanced_text = f"{play_text} ({detail_text}) - {coord_text}"
                            else:
                                enhanced_text = f"{play_text} ({detail_text})"
                        elif coord_text:
                            enhanced_text = f"{play_text} - {coord_text}"
                        else:
                            enhanced_text = play_text
                    
                    pitch_item = QTreeWidgetItem([f"  {enhanced_text}"])
                    
                    # Store pitch data for audio playback
                    pitch_data = {
                        'x': espn_x,
                        'y': espn_y,
                        'velocity': velocity,
                        'pitch_type': pitch_type_text,
                        'batter_hand': batter_side,
                        'is_pitch': True
                    }
                    pitch_item.setData(0, Qt.ItemDataRole.UserRole, pitch_data)
                    at_bat_item.addChild(pitch_item)
                else:
                    # Other play details (substitutions, etc.)
                    detail_item = QTreeWidgetItem([f"  {play_text}"])
                    at_bat_item.addChild(detail_item)

    def _determine_drive_result(self, drive_plays):
        """Determine the result of an NFL drive"""
        if not drive_plays:
            return "No plays"
        
        last_play = drive_plays[-1]
        play_text = last_play.get("text", "").lower()
        
        # Check for common drive outcomes
        if "touchdown" in play_text:
            return "Touchdown"
        elif "field goal" in play_text:
            return "Field Goal"
        elif "punt" in play_text:
            return "Punt"
        elif "turnover" in play_text or "interception" in play_text or "fumble" in play_text:
            return "Turnover"
        elif "safety" in play_text:
            return "Safety"
        elif any(end_indicator in play_text for end_indicator in ["end of quarter", "end of half", "end of game"]):
            return "End of Period"
        else:
            return f"{len(drive_plays)} plays"
    
    def _add_football_plays_to_drive(self, parent_item, plays):
        """Add NFL plays to a drive, organizing by meaningful sequences"""
        for play in plays:
            play_text = play.get("text", "Unknown play")
            
            # Extract down and distance info if available
            down = play.get("down")
            distance = play.get("distance")
            yard_line = play.get("yardLine")
            
            # Enhance play text with context
            enhanced_text = play_text
            if down and distance:
                enhanced_text = f"{down} & {distance}: {play_text}"
            
            if yard_line:
                enhanced_text = f"{enhanced_text} (at {yard_line})"
            
            # Create play item
            play_item = QTreeWidgetItem([enhanced_text])
            
            # Highlight scoring plays
            if play.get("scoringPlay", False):
                play_item.setBackground(0, QColor(255, 255, 150))  # Light yellow
                away_score = play.get("awayScore", 0)
                home_score = play.get("homeScore", 0)
                play_item.setText(0, f"🏈 {enhanced_text} ({away_score}-{home_score})")
            
            parent_item.addChild(play_item)

    def _is_pitch_item(self, tree_item):
        """Check if the tree item represents a pitch (for audio playback)"""
        if not tree_item:
            return False
            
        # Check if item text contains pitch-related keywords
        item_text = tree_item.text(0).lower()
        
        # Look for pitch indicators
        pitch_indicators = [
            "ball", "strike", "foul", "looking", "swinging",
            "fastball", "slider", "curveball", "changeup", "sinker", "cutter",
            "mph", "hit by pitch"
        ]
        
        # Also check for coordinate patterns (x, y)
        has_coordinates = "(" in item_text and ")" in item_text and "," in item_text
        
        return any(indicator in item_text for indicator in pitch_indicators) or has_coordinates
    
    def _play_pitch_audio(self, tree_item):
        """Extract pitch data from tree item and play spatial audio"""
        if not self.audio_mapper:
            return
            
        try:
            # Try to get stored pitch data first
            pitch_data = tree_item.data(0, Qt.ItemDataRole.UserRole)
            
            if pitch_data and isinstance(pitch_data, dict) and pitch_data.get('is_pitch'):
                # Use stored data
                x = pitch_data.get('x')
                y = pitch_data.get('y') 
                velocity = pitch_data.get('velocity')
                pitch_type = pitch_data.get('pitch_type')
                batter_hand = pitch_data.get('batter_hand')
            else:
                # Fall back to text parsing
                item_text = tree_item.text(0)
                parsed_data = self._extract_pitch_data_from_text(item_text)
                
                if not parsed_data:
                    self._on_audio_error("Could not parse pitch data from selected item")
                    return
                    
                x = parsed_data.get('x')
                y = parsed_data.get('y') 
                velocity = parsed_data.get('velocity')
                pitch_type = parsed_data.get('pitch_type')
                batter_hand = parsed_data.get('batter_hand')
            
            if x is not None and y is not None:
                # Generate and play spatial audio
                self.audio_mapper.generate_pitch_audio(
                    x, y, velocity, pitch_type, batter_hand
                )
                
                # Provide accessible feedback
                location_desc = self.audio_mapper._get_location_description(x, y, batter_hand)
                feedback = f"Playing audio for pitch at ({x}, {y}) - {location_desc}"
                self._on_audio_feedback(feedback)
            else:
                self._on_audio_error("Could not extract coordinates from pitch data")
                
        except Exception as e:
            self._on_audio_error(f"Failed to play pitch audio: {str(e)}")
    
    def _extract_pitch_data_from_text(self, item_text):
        """Extract pitch data from enhanced tree item text"""
        import re
        
        pitch_data = {}
        
        # Extract coordinates (x, y) 
        coord_pattern = r'\((\d+),\s*(\d+)\)'
        coord_match = re.search(coord_pattern, item_text)
        if coord_match:
            pitch_data['x'] = int(coord_match.group(1))
            pitch_data['y'] = int(coord_match.group(2))
        
        # Extract velocity
        velocity_pattern = r'(\d+)\s*mph'
        velocity_match = re.search(velocity_pattern, item_text, re.IGNORECASE)
        if velocity_match:
            pitch_data['velocity'] = int(velocity_match.group(1))
        
        # Extract pitch type
        pitch_types = [
            'four-seam fastball', 'fastball', 'slider', 'curveball', 'changeup', 
            'sinker', 'cutter', 'knuckleball', 'splitter', 'curve'
        ]
        
        for pitch_type in pitch_types:
            if pitch_type.lower() in item_text.lower():
                pitch_data['pitch_type'] = pitch_type
                break
        
        # Try to determine batter handedness from context
        # This is a simplified approach - in a full implementation, 
        # we'd track the current batter's handedness more systematically
        
        # For now, use heuristics based on location description
        if 'inside' in item_text.lower() and 'way' in item_text.lower():
            # Could indicate handedness based on coordinate ranges
            x = pitch_data.get('x', 127)
            if x < 100:  # Low X values
                pitch_data['batter_hand'] = 'R'  # Inside to right-handed batter
            else:
                pitch_data['batter_hand'] = 'L'  # Inside to left-handed batter
        else:
            # Default assumption
            pitch_data['batter_hand'] = 'R'
        
        return pitch_data
    
    def _show_pitch_context_menu(self, tree_item, global_position):
        """Show context menu for pitch-related audio options"""
        if not self.audio_mapper:
            return
            
        menu = QMenu(self)
        menu.setAccessibleName("Pitch Audio Options")
        
        # Check if this is a pitch item or player/at-bat item
        is_pitch = self._is_pitch_item(tree_item)
        is_at_bat = tree_item.parent() is None  # Top-level item (at-bat)
        
        # Option 1: Play current pitch audio (only for actual pitches)
        if is_pitch:
            play_action = QAction("Play Pitch Audio", self)
            play_action.setShortcut("Alt+P")
            play_action.setStatusTip("Play spatial audio for the current pitch location")
            play_action.triggered.connect(lambda: self._play_pitch_audio(tree_item))
            menu.addAction(play_action)
        
        # Option 2: Play pitch sequence (works for both pitches and at-bat items)
        if is_pitch or is_at_bat:
            sequence_action = QAction("Play Pitch Sequence", self)
            sequence_action.setShortcut("Alt+S")
            sequence_action.setStatusTip("Play audio for all pitches in this at-bat from first to last")
            sequence_action.triggered.connect(lambda: self._play_pitch_sequence(tree_item))
            menu.addAction(sequence_action)
        
        # Option 3: Comprehensive Pitch Exploration (always available)
        if menu.actions():  # Only add separator if we have other actions
            menu.addSeparator()
            
        explore_action = QAction("Open Pitch Explorer", self)
        explore_action.setShortcut("Ctrl+E")
        explore_action.setStatusTip("Open comprehensive pitch exploration with strike zone grid and game data")
        explore_action.triggered.connect(lambda: self._open_pitch_explorer(tree_item))
        menu.addAction(explore_action)
        
        # Show menu
        menu.exec(global_position)
    
    def _play_pitch_sequence(self, tree_item):
        """Play audio sequence for all pitches in the current batter's at-bat"""
        if not self.audio_mapper:
            return
            
        try:
            # Find the parent at-bat item
            at_bat_item = tree_item.parent() if tree_item.parent() else tree_item
            
            # Collect all pitch items from this at-bat
            pitch_items = []
            for i in range(at_bat_item.childCount()):
                child_item = at_bat_item.child(i)
                if self._is_pitch_item(child_item):
                    pitch_items.append(child_item)
            
            if not pitch_items:
                self._on_audio_error("No pitches found in this at-bat")
                return
            
            # Get batter name for feedback
            batter_info = at_bat_item.text(0)
            batter_name = batter_info.split(':')[0] if ':' in batter_info else "Batter"
            
            self._on_audio_feedback(f"Playing pitch sequence for {batter_name} ({len(pitch_items)} pitches)")
            
            # Play sequence with timing
            self._play_pitch_sequence_with_timing(pitch_items, 0)
            
        except Exception as e:
            self._on_audio_error(f"Failed to play pitch sequence: {str(e)}")
    
    def _play_pitch_sequence_with_timing(self, pitch_items, index):
        """Play pitch sequence with appropriate timing between pitches"""
        if index >= len(pitch_items):
            self._on_audio_feedback("Pitch sequence complete")
            return
        
        # Play current pitch
        current_pitch = pitch_items[index]
        self._play_pitch_audio(current_pitch)
        
        # Schedule next pitch with reduced delay
        delay_ms = 800  # Reduced from 1200ms to 800ms (0.8 seconds between pitches)
        QTimer.singleShot(delay_ms, lambda: self._play_pitch_sequence_with_timing(pitch_items, index + 1))

    def _play_strike_zone_audio(self, zone_position):
        """Play audio for a specific strike zone position"""
        if not self.audio_mapper:
            return
            
        try:
            # Try to determine batter handedness from current context
            batter_hand = 'R'  # Default to right-handed
            
            # Try to get from currently selected item
            current_item = self.current_tree_widget.currentItem() if hasattr(self, 'current_tree_widget') else None
            if current_item:
                # Navigate to at-bat level to get batter info
                at_bat_item = current_item.parent() if current_item.parent() else current_item
                batter_info = at_bat_item.text(0)
                
                # Simple heuristic based on known players
                if 'Lindor' in batter_info:
                    batter_hand = 'L'
                # Add more known players as needed
            
            # Generate audio for the strike zone position
            self.audio_mapper.generate_strike_zone_audio(zone_position, batter_hand)
            
            # Provide feedback
            zone_name = zone_position.replace('_', ' ').title()
            self._on_audio_feedback(f"Strike zone: {zone_name}")
            
        except Exception as e:
            self._on_audio_error(f"Failed to play strike zone audio: {str(e)}")

    def _open_pitch_explorer(self, tree_item):
        """Open the comprehensive pitch exploration dialog"""
        if not AUDIO_AVAILABLE:
            QMessageBox.warning(self, "Audio Not Available", 
                              "Audio system is not available. Cannot open pitch explorer.")
            return
        
        try:
            # Extract pitch data from current game/at-bat
            game_pitches = self._extract_pitch_data_for_explorer(tree_item)
            
            # Open the pitch exploration dialog
            dialog = PitchExplorationDialog(self, game_pitches)
            
            # Connect dialog signals to main app feedback
            dialog.audio_feedback.connect(self._on_audio_feedback)
            dialog.audio_error.connect(self._on_audio_error)
            
            # Show dialog
            dialog.exec()
            
        except Exception as e:
            self._on_audio_error(f"Failed to open pitch explorer: {str(e)}")
    
    def _extract_pitch_data_for_explorer(self, tree_item):
        """Extract pitch data from the current game for the explorer"""
        pitch_data = []
        
        try:
            # If we have current plays data, extract pitches from it
            if hasattr(self, 'current_plays_data') and self.current_plays_data:
                for play in self.current_plays_data:
                    # Look for pitch coordinate data
                    pitch_coordinate = play.get("pitchCoordinate", {})
                    if pitch_coordinate and isinstance(pitch_coordinate, dict):
                        x = pitch_coordinate.get("x")
                        y = pitch_coordinate.get("y")
                        
                        if x is not None and y is not None:
                            # Extract additional pitch info from play text
                            play_text = play.get("text", "")
                            pitch_type = "Unknown"
                            velocity = None
                            result = "Unknown"
                            
                            # Try to parse pitch details from text
                            if "Fastball" in play_text:
                                pitch_type = "Fastball"
                            elif "Slider" in play_text:
                                pitch_type = "Slider"
                            elif "Changeup" in play_text:
                                pitch_type = "Changeup"
                            elif "Curveball" in play_text:
                                pitch_type = "Curveball"
                            
                            # Extract result
                            if "Strike" in play_text:
                                result = "Strike"
                            elif "Ball" in play_text:
                                result = "Ball"
                            elif "Foul" in play_text:
                                result = "Foul"
                            elif "Hit" in play_text or "In Play" in play_text:
                                result = "In Play"
                            
                            pitch_data.append({
                                'x': x,
                                'y': y,
                                'type': pitch_type,
                                'velocity': velocity,
                                'result': result,
                                'text': play_text
                            })
            
        except Exception as e:
            print(f"Error extracting pitch data: {e}")
        
        return pitch_data

    def _play_current_pitch_audio(self, plays_tree):
        """Play audio for the currently selected pitch"""
        current_item = plays_tree.currentItem()
        if current_item and self._is_pitch_item(current_item):
            self._play_pitch_audio(current_item)
        else:
            # Provide feedback if no pitch is selected
            QMessageBox.information(None, "Pitch Audio", "Please select a pitch to play audio.")

    def _export_game_log(self):
        """Export complete game log as HTML file"""
        try:
            # Check for either plays data or drives data
            has_plays = hasattr(self, 'current_plays_data') and self.current_plays_data
            has_drives = hasattr(self, 'current_drives_data') and self.current_drives_data
            
            if not has_plays and not has_drives:
                QMessageBox.warning(self, "Export Error", "No play or drive data available to export.")
                return
            
            # Generate filename with game information
            filename = self._generate_export_filename()
            
            # Generate HTML content
            html_content = self._generate_game_log_html()
            
            # Save to file in the application directory
            app_dir = os.getcwd()  # Current working directory where app was launched
            file_path = os.path.join(app_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Show success message
            QMessageBox.information(
                self,
                "Export Complete",
                f"Game log exported successfully!\n\nFile saved as:\n{filename}\n\nLocation: {app_dir}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export game log:\n{str(e)}")
    
    def _generate_export_filename(self):
        """Generate a unique filename for the exported game log"""
        from datetime import datetime
        
        # Get current date for the filename
        current_date = datetime.now().strftime("%Y%m%d")
        
        # Try to extract team information for a meaningful filename
        game_info = ""
        team_names = self._extract_team_nicknames()
        
        if team_names:
            away_team, home_team = team_names
            game_info = f"{away_team}_vs_{home_team}"
        elif hasattr(self, 'game_id') and self.game_id:
            game_info = f"game_{self.game_id}"
        
        # Fallback to league if no specific game info
        if not game_info:
            league = getattr(self, 'league', 'UNKNOWN').upper()
            game_info = f"{league}_game"
        
        # Create filename
        filename = f"game_log_{game_info}_{current_date}.html"
        
        # Sanitize filename (remove/replace invalid characters)
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        return filename
    
    def _extract_team_nicknames(self):
        """Extract team nicknames from game data"""
        try:
            # Try to get team info from the stored raw details
            if hasattr(self, 'current_raw_details') and self.current_raw_details:
                details = self.current_raw_details
                if 'header' in details:
                    competitors = details['header'].get('competitions', [{}])[0].get('competitors', [])
                    if len(competitors) >= 2:
                        # Find away team (order=0) and home team (order=1)
                        away_team = None
                        home_team = None
                        for competitor in competitors:
                            if competitor.get('homeAway') == 'away':
                                away_team = competitor['team']['name']  # e.g., "Athletics", "Brewers"
                            elif competitor.get('homeAway') == 'home':
                                home_team = competitor['team']['name']  # e.g., "Nationals", "Yankees"
                        
                        if away_team and home_team:
                            return away_team, home_team
                        
                        # Fallback to order-based extraction
                        if len(competitors) >= 2:
                            away_team = competitors[0]['team']['name']
                            home_team = competitors[1]['team']['name']
                            return away_team, home_team
            
            # Fallback: try to extract from plays data
            if hasattr(self, 'current_plays_data') and self.current_plays_data:
                # Look for team info in the first play
                first_play = self.current_plays_data[0]
                if 'homeTeam' in first_play and 'awayTeam' in first_play:
                    away_team = first_play['awayTeam'].get('name', first_play['awayTeam'].get('abbreviation', 'AWAY'))
                    home_team = first_play['homeTeam'].get('name', first_play['homeTeam'].get('abbreviation', 'HOME'))
                    return away_team, home_team
            
            # Fallback: try to extract from drives data
            if hasattr(self, 'current_drives_data') and self.current_drives_data:
                # Look for team info in drives
                all_teams = set()
                drives_data = self.current_drives_data
                
                # Check current drive
                current_drive = drives_data.get("current")
                if current_drive and isinstance(current_drive, dict):
                    team_info = current_drive.get("team", {})
                    if team_info.get("displayName"):
                        all_teams.add(team_info["displayName"])
                
                # Check previous drives
                previous_drives = drives_data.get("previous", [])
                for drive in previous_drives:
                    if isinstance(drive, dict):
                        team_info = drive.get("team", {})
                        if team_info.get("displayName"):
                            all_teams.add(team_info["displayName"])
                
                # If we found teams, return them (order may not be perfect but better than nothing)
                teams_list = list(all_teams)
                if len(teams_list) >= 2:
                    return teams_list[0], teams_list[1]
                elif len(teams_list) == 1:
                    return teams_list[0], "Opponent"
        except Exception:
            pass
        
        return None
    
    def _generate_game_log_html(self):
        """Generate HTML content for the complete game log"""
        # Determine what data we have and sport type
        has_plays = hasattr(self, 'current_plays_data') and self.current_plays_data
        has_drives = hasattr(self, 'current_drives_data') and self.current_drives_data
        
        if has_plays:
            sport_type = self._detect_sport_type(self.current_plays_data)
            data_for_sport_detection = self.current_plays_data
            total_items = len(self.current_plays_data)
            data_type = "Plays"
        elif has_drives:
            sport_type = "Football"  # Drives are NFL/NCAAF
            data_for_sport_detection = self.current_drives_data
            # Count total drives from both current and previous
            total_drives = 0
            if self.current_drives_data.get("current"):
                total_drives += 1
            if self.current_drives_data.get("previous"):
                total_drives += len(self.current_drives_data.get("previous", []))
            total_items = total_drives
            data_type = "Drives"
        else:
            sport_type = "Unknown"
            total_items = 0
            data_type = "Items"
        
        # Generate better title with team names
        title = f"Exported Game Log - {sport_type}"
        team_names = self._extract_team_nicknames()
        if team_names:
            away_team, home_team = team_names
            title = f"Exported Game Log - {sport_type} - {away_team} vs {home_team}"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }}
        .header {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .period {{
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .period-header {{
            background-color: #e9e9e9;
            padding: 10px;
            font-weight: bold;
            font-size: 18px;
        }}
        .half-section {{
            margin: 10px;
        }}
        .half-header {{
            background-color: #f9f9f9;
            padding: 8px;
            font-weight: bold;
            border-left: 4px solid #007cba;
            margin: 10px 0 5px 0;
        }}
        .at-bat {{
            margin: 10px 0;
            padding: 8px;
            border-left: 3px solid #ccc;
            background-color: #fafafa;
        }}
        .at-bat.scoring {{
            border-left-color: #ff6b35;
            background-color: #fff5f0;
        }}
        .at-bat-list {{
            list-style-type: none;
            padding-left: 0;
            margin: 10px 0;
        }}
        .at-bat-item {{
            margin: 10px 0;
            padding: 8px;
            border-left: 3px solid #ccc;
            background-color: #fafafa;
        }}
        .at-bat-item.scoring {{
            border-left-color: #ff6b35;
            background-color: #fff5f0;
        }}
        .at-bat-header {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .at-bat-title {{
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0 8px 0;
            color: #333;
        }}
        .at-bat-title.scoring {{
            color: #ff6b35;
        }}
        .inning-half-title {{
            font-size: 20px;
            font-weight: bold;
            margin: 15px 0 10px 0;
            color: #444;
            border-bottom: 2px solid #007cba;
            padding-bottom: 5px;
        }}
        .at-bat-heading {{
            font-size: 16px;
            font-weight: bold;
            margin: 8px 0 5px 0;
            color: #333;
        }}
        .at-bat-heading.scoring {{
            color: #ff6b35;
        }}
        .pitch-list {{
            list-style-type: disc;
            margin: 8px 0;
            padding-left: 25px;
        }}
        .pitch-item {{
            color: #666;
            margin: 3px 0;
            font-size: 14px;
        }}
        .at-bat-result {{
            font-style: italic;
            color: #333;
            margin-top: 8px;
            font-weight: bold;
            border-top: 1px solid #ddd;
            padding-top: 5px;
        }}
        .pitch {{
            margin: 3px 0 3px 20px;
            color: #666;
            font-size: 14px;
        }}
        .drive {{
            margin: 10px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 3px;
        }}
        .drive-header {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
            font-size: 16px;
        }}
        .play-list {{
            list-style-type: disc;
            margin: 8px 0;
            padding-left: 25px;
        }}
        .play-item {{
            margin: 3px 0;
            color: #333;
            font-size: 14px;
        }}
        .play-item.scoring {{
            color: #ff6b35;
            font-weight: bold;
        }}
        .play {{
            margin: 3px 0 3px 15px;
            padding: 3px;
        }}
        .play.scoring {{
            background-color: #fff5f0;
            font-weight: bold;
        }}
        .export-info {{
            margin-top: 30px;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 3px;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p><strong>Total {data_type}:</strong> {total_items}</p>
        <p><strong>Export Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
"""
        
        if sport_type == "MLB":
            html += self._generate_baseball_html()
        elif sport_type == "NFL":
            if has_drives:
                html += self._generate_football_drives_html()
            else:
                html += self._generate_football_html()
        else:
            html += self._generate_generic_html()
        
        html += f"""
    <div class="export-info">
        <p>This game log was exported from the Sports Scores application.</p>
        <p>Generated on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S")}</p>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_baseball_html(self):
        """Generate HTML for baseball game log"""
        # Group plays by inning (similar to tree structure)
        inning_groups = {}
        for play in self.current_plays_data:
            period_info = play.get("period", {})
            period_display = period_info.get("displayValue", f"Period {period_info.get('number', 0)}")
            period_type = period_info.get("type", "Unknown").lower()
            
            if period_display not in inning_groups:
                inning_groups[period_display] = {"top": [], "bottom": []}
            
            if period_type == "top":
                inning_groups[period_display]["top"].append(play)
            elif period_type == "bottom":
                inning_groups[period_display]["bottom"].append(play)
            else:
                inning_groups[period_display]["top"].append(play)
        
        html = ""
        for period_display in sorted(inning_groups.keys(), key=lambda x: int(x.split()[0][:-2]) if x.split()[0][:-2].isdigit() else 0):
            period_data = inning_groups[period_display]
            
            html += f'<div class="period">'
            html += f'<div class="period-header">{period_display}</div>'
            
            # Top half
            if period_data["top"]:
                inning_num = period_display.split()[0]
                html += f'<div class="half-section">'
                html += f'<h2 class="inning-half-title">Top of the {inning_num}</h2>'
                html += self._generate_baseball_at_bats_html_with_lists(period_data["top"])
                html += '</div>'
            
            # Bottom half
            if period_data["bottom"]:
                inning_num = period_display.split()[0]
                html += f'<div class="half-section">'
                html += f'<h2 class="inning-half-title">Bottom of the {inning_num}</h2>'
                html += self._generate_baseball_at_bats_html_with_lists(period_data["bottom"])
                html += '</div>'
            
            html += '</div>'
        
        return html
    
    def _generate_baseball_at_bats_html_with_lists(self, plays):
        """Generate HTML for baseball at-bats using proper list structure"""
        # Group plays into at-bats with better logic
        at_bats = []
        current_at_bat = None
        
        for play in plays:
            play_type = play.get("type", {}).get("type", "")
            play_text = play.get("text", "")
            at_bat_id = play.get("atBatId")
            
            # Skip only true inning management plays
            if play_type in ["start-inning", "end-inning"] and "inning" in play_text.lower():
                continue
            
            # Start new at-bat or continue existing one
            if current_at_bat is None or (at_bat_id and current_at_bat["id"] != at_bat_id):
                if current_at_bat:
                    at_bats.append(current_at_bat)
                
                # Extract batter name from participants
                batter_name = "Unknown"
                participants = play.get("participants", [])
                for participant in participants:
                    if participant.get("type") == "batter":
                        athlete = participant.get("athlete", {})
                        batter_name = athlete.get("shortName") or athlete.get("displayName") or "Unknown"
                        break
                
                # If we still don't have a name, try the play text
                if batter_name == "Unknown" and play_text:
                    # Try to extract name from play text patterns
                    if " to " in play_text:
                        parts = play_text.split(" to ")
                        if len(parts) > 0:
                            potential_name = parts[0].strip()
                            if len(potential_name.split()) <= 3:
                                batter_name = potential_name
                    elif " struck out" in play_text:
                        name_part = play_text.split(" struck out")[0].strip()
                        if len(name_part.split()) <= 3:
                            batter_name = name_part
                
                current_at_bat = {
                    "id": at_bat_id,
                    "batter": batter_name,
                    "result": "",
                    "plays": [],
                    "scoring": False,
                    "score": ""
                }
            
            current_at_bat["plays"].append(play)
            
            # Check for scoring play
            if play.get("scoringPlay", False):
                current_at_bat["scoring"] = True
                away_score = play.get("awayScore", 0)
                home_score = play.get("homeScore", 0)
                current_at_bat["score"] = f"({away_score}-{home_score})"
            
            # Look for at-bat result plays (less restrictive)
            if not current_at_bat["result"] and play_text:
                # If it's not just a pitch description, it might be a result
                if not any(pitch_word in play_text.lower() for pitch_word in 
                          ["pitch", "ball ", "strike ", "foul tip"]):
                    current_at_bat["result"] = play_text
        
        if current_at_bat:
            at_bats.append(current_at_bat)
        
        if not at_bats:
            return '<p>No at-bats in this half inning.</p>'
        
        html = '<ul class="at-bat-list">'
        
        for at_bat in at_bats:
            # Be less restrictive about showing at-bats
            if not at_bat["batter"] or at_bat["batter"] == "Unknown":
                # If no batter name, use the play text as a fallback
                if at_bat["plays"] and at_bat["plays"][0].get("text"):
                    at_bat["batter"] = "Play"
                else:
                    continue
            
            # Use the result or fall back to the most meaningful play
            result_text = at_bat["result"]
            if not result_text and at_bat["plays"]:
                # Find the most meaningful play (not just pitch descriptions)
                for play in reversed(at_bat["plays"]):  # Start from the end
                    text = play.get("text", "")
                    if text and not any(pitch_word in text.lower() for pitch_word in 
                                      ["pitch ", "ball ", "strike ", "foul tip"]):
                        result_text = text
                        break
                
                # If still no result, use the last play
                if not result_text:
                    result_text = at_bat["plays"][-1].get("text", "")
            
            if not result_text:
                continue
                
            scoring_class = "scoring" if at_bat["scoring"] else ""
            score_text = f" {at_bat['score']}" if at_bat["scoring"] else ""
            
            html += f'<li class="at-bat-item {scoring_class}">'
            html += f'<h3 class="at-bat-heading {scoring_class}">{at_bat["batter"]}: {result_text}{score_text}</h3>'
            
            # Add pitch details as a nested list
            pitch_plays = []
            for play in at_bat["plays"]:
                play_text = play.get("text", "")
                
                # Skip the result play and include pitch-related plays
                if play_text != result_text and any(pitch_keyword in play_text.lower() for pitch_keyword in 
                       ["ball", "strike", "foul", "looking", "swinging", "pitch"]):
                    
                    # Extract additional pitch details if available (same logic as tree view)
                    enhanced_text = play_text
                    velocity = play.get("pitchVelocity")
                    pitch_type = play.get("pitchType", {})
                    pitch_type_text = pitch_type.get("text", "") if isinstance(pitch_type, dict) else ""
                    pitch_coordinate = play.get("pitchCoordinate", {})
                    
                    # Get pitch location with absolute coordinates (same logic as tree view)
                    location = ""
                    if pitch_coordinate and isinstance(pitch_coordinate, dict):
                        espn_x = pitch_coordinate.get("x")  # Horizontal (absolute)
                        espn_y = pitch_coordinate.get("y")  # Vertical (absolute)
                        if espn_x is not None and espn_y is not None:
                            # Try to determine batter handedness (simplified)
                            batter_side = None
                            
                            # Check if we can extract batter info from the play data (safely)
                            if isinstance(play, dict) and 'participants' in play:
                                for participant in play.get('participants', []):
                                    if isinstance(participant, dict) and participant.get('type') == 'batter':
                                        batter_side = participant.get('batSide')
                                        break
                            
                            # Use simple heuristics for known players
                            # TODO: Improve batter data extraction from ESPN API
                            
                            # Get location with batter context
                            location = get_pitch_location(espn_x, espn_y, batter_side)
                    
                    # Build enhanced text with velocity, type, and coordinates
                    # Note: location now contains coordinates, so no need for separate coordinates_text
                    details = []
                    if velocity:
                        details.append(f"{velocity} mph")
                    if pitch_type_text:
                        details.append(pitch_type_text)
                    
                    if details:
                        detail_text = " ".join(details)
                        if location:
                            enhanced_text = f"{play_text} ({detail_text}) - {location}"
                        else:
                            enhanced_text = f"{play_text} ({detail_text})"
                    elif location:
                        enhanced_text = f"{play_text} - {location}"
                    else:
                        enhanced_text = play_text
                    
                    pitch_plays.append(enhanced_text)
            
            if pitch_plays:
                html += '<ul class="pitch-list">'
                for pitch_text in pitch_plays:
                    html += f'<li class="pitch-item">{pitch_text}</li>'
                html += '</ul>'
            
            # Repeat the result at the end for better flow
            html += f'<div class="at-bat-result">Result: {result_text}{score_text}</div>'
            
            html += '</li>'
        
        html += '</ul>'
        return html
    
    def _generate_baseball_at_bats_html(self, plays):
        """Generate HTML for baseball at-bats"""
        # Group plays into at-bats with better logic
        at_bats = []
        current_at_bat = None
        
        for play in plays:
            play_type = play.get("type", {}).get("type", "")
            play_text = play.get("text", "")
            at_bat_id = play.get("atBatId")
            
            # Skip only true inning management plays
            if play_type in ["start-inning", "end-inning"] and "inning" in play_text.lower():
                continue
            
            # Start new at-bat or continue existing one
            if current_at_bat is None or (at_bat_id and current_at_bat["id"] != at_bat_id):
                if current_at_bat:
                    at_bats.append(current_at_bat)
                
                # Extract batter name from participants
                batter_name = "Unknown"
                participants = play.get("participants", [])
                for participant in participants:
                    if participant.get("type") == "batter":
                        athlete = participant.get("athlete", {})
                        batter_name = athlete.get("shortName") or athlete.get("displayName") or "Unknown"
                        break
                
                # If we still don't have a name, try the play text
                if batter_name == "Unknown" and play_text:
                    # Try to extract name from play text patterns
                    if " to " in play_text:
                        # Pattern: "John Smith to first base"
                        parts = play_text.split(" to ")
                        if len(parts) > 0:
                            potential_name = parts[0].strip()
                            if len(potential_name.split()) <= 3:  # Reasonable name length
                                batter_name = potential_name
                    elif " struck out" in play_text:
                        # Pattern: "Smith struck out swinging"
                        name_part = play_text.split(" struck out")[0].strip()
                        if len(name_part.split()) <= 3:
                            batter_name = name_part
                
                current_at_bat = {
                    "id": at_bat_id,
                    "batter": batter_name,
                    "result": "",
                    "plays": [],
                    "scoring": False,
                    "score": ""
                }
            
            current_at_bat["plays"].append(play)
            
            # Check for scoring play
            if play.get("scoringPlay", False):
                current_at_bat["scoring"] = True
                away_score = play.get("awayScore", 0)
                home_score = play.get("homeScore", 0)
                current_at_bat["score"] = f"({away_score}-{home_score})"
            
            # Look for at-bat result plays (less restrictive)
            if not current_at_bat["result"] and play_text:
                # If it's not just a pitch description, it might be a result
                if not any(pitch_word in play_text.lower() for pitch_word in 
                          ["pitch", "ball ", "strike ", "foul tip"]):
                    current_at_bat["result"] = play_text
        
        if current_at_bat:
            at_bats.append(current_at_bat)
        
        html = ""
        for at_bat in at_bats:
            # Be less restrictive about showing at-bats
            if not at_bat["batter"] or at_bat["batter"] == "Unknown":
                # If no batter name, use the play text as a fallback
                if at_bat["plays"] and at_bat["plays"][0].get("text"):
                    at_bat["batter"] = "Play"
                else:
                    continue
            
            # Use the result or fall back to the most meaningful play
            result_text = at_bat["result"]
            if not result_text and at_bat["plays"]:
                # Find the most meaningful play (not just pitch descriptions)
                for play in reversed(at_bat["plays"]):  # Start from the end
                    text = play.get("text", "")
                    if text and not any(pitch_word in text.lower() for pitch_word in 
                                      ["pitch ", "ball ", "strike ", "foul tip"]):
                        result_text = text
                        break
                
                # If still no result, use the last play
                if not result_text:
                    result_text = at_bat["plays"][-1].get("text", "")
            
            if not result_text:
                continue
                
            scoring_class = "scoring" if at_bat["scoring"] else ""
            score_text = f" {at_bat['score']}" if at_bat["scoring"] else ""
            
            html += f'<div class="at-bat {scoring_class}">'
            html += f'<strong>{at_bat["batter"]}: {result_text}{score_text}</strong>'
            
            # Add pitch details (but filter out the result play to avoid duplication)
            for play in at_bat["plays"]:
                play_text = play.get("text", "")
                
                # Skip the result play and include pitch-related plays
                if play_text != result_text and any(pitch_keyword in play_text.lower() for pitch_keyword in 
                       ["ball", "strike", "foul", "looking", "swinging", "pitch"]):
                    html += f'<div class="pitch">{play_text}</div>'
            
            html += '</div>'
        
        return html
    
    def _generate_football_html(self):
        """Generate HTML for football game log"""
        # Group by quarter and drive
        quarter_groups = {}
        
        for play in self.current_plays_data:
            period_info = play.get("period", {})
            period_display = period_info.get("displayValue", f"{period_info.get('number', 1)}Q")
            
            drive_number = play.get("driveNumber", "Unknown")
            drive_team = play.get("team", {}).get("id", "Unknown")
            
            if period_display not in quarter_groups:
                quarter_groups[period_display] = {}
            
            drive_key = f"Drive {drive_number} (Team {drive_team})"
            if drive_key not in quarter_groups[period_display]:
                quarter_groups[period_display][drive_key] = []
            
            quarter_groups[period_display][drive_key].append(play)
        
        html = ""
        for period_display in sorted(quarter_groups.keys()):
            html += f'<div class="period">'
            html += f'<div class="period-header">{period_display}</div>'
            
            for drive_key, drive_plays in quarter_groups[period_display].items():
                html += f'<div class="drive">'
                html += f'<div class="drive-header">{drive_key}</div>'
                
                for play in drive_plays:
                    scoring_class = "scoring" if play.get("scoringPlay", False) else ""
                    play_text = play.get("text", "")
                    
                    if play.get("scoringPlay", False):
                        away_score = play.get("awayScore", 0)
                        home_score = play.get("homeScore", 0)
                        play_text = f"🏈 {play_text} ({away_score}-{home_score})"
                    
                    html += f'<div class="play {scoring_class}">{play_text}</div>'
                
                html += '</div>'
            
            html += '</div>'
        
        return html
    
    def _generate_football_drives_html(self):
        """Generate HTML for football game log from drives data"""
        # Process drives data structure
        drives_data = self.current_drives_data
        all_drives = []
        
        # Add current drive if available
        current_drive = drives_data.get("current")
        if current_drive:
            all_drives.append(("Current Drive", current_drive))
        
        # Add previous drives if available
        previous_drives = drives_data.get("previous", [])
        for i, drive in enumerate(previous_drives):
            drive_num = len(previous_drives) - i  # Number drives in reverse order
            all_drives.append((f"Drive {drive_num}", drive))
        
        # Group drives by quarter for better organization
        quarter_groups = {}
        
        for drive_label, drive in all_drives:
            if not drive or not isinstance(drive, dict):
                continue
                
            # Get drive info
            description = drive.get("description", "Unknown drive")
            team_info = drive.get("team", {})
            team_name = team_info.get("displayName", "Unknown Team")
            
            # Determine quarter from plays
            plays = drive.get("plays", [])
            quarter = "Unknown Quarter"
            if plays and len(plays) > 0:
                first_play = plays[0]
                period_info = first_play.get("period", {})
                quarter = period_info.get("displayValue", f"{period_info.get('number', 1)}Q")
            
            # Separate kickoffs from regular drive plays
            drive_plays = []
            kickoff_plays = []
            
            for play in plays:
                play_type = play.get("type", {})
                play_type_text = play_type.get("text", "").lower()
                
                if "kickoff" in play_type_text:
                    kickoff_plays.append(play)
                else:
                    drive_plays.append(play)
            
            if quarter not in quarter_groups:
                quarter_groups[quarter] = []
            
            # Add kickoffs as separate entries
            for kickoff in kickoff_plays:
                quarter_groups[quarter].append({
                    "label": "Kickoff",
                    "team": "Special Teams",
                    "description": "Kickoff",
                    "plays": [kickoff],
                    "is_kickoff": True
                })
            
            # Add regular drive if it has non-kickoff plays
            if drive_plays:
                quarter_groups[quarter].append({
                    "label": drive_label,
                    "team": team_name,
                    "description": description,
                    "plays": drive_plays,
                    "is_kickoff": False
                })
        
        html = ""
        for quarter_name in sorted(quarter_groups.keys()):
            html += f'<div class="period">'
            html += f'<h2 class="period-header">{quarter_name}</h2>'
            
            for drive_info in quarter_groups[quarter_name]:
                html += f'<div class="drive">'
                
                # Handle kickoffs differently
                if drive_info.get("is_kickoff", False):
                    html += f'<h3 class="drive-header kickoff-header">⚡ Kickoff</h3>'
                else:
                    html += f'<h3 class="drive-header">{drive_info["team"]}: {drive_info["description"]}</h3>'
                
                html += f'<ul class="play-list">'
                
                for play in drive_info["plays"]:
                    play_text = play.get("text", "Unknown play")
                    play_type = play.get("type", {})
                    play_type_text = play_type.get("text", "").lower()
                    
                    # Handle kickoffs
                    if "kickoff" in play_type_text or drive_info.get("is_kickoff", False):
                        # Add clock context for kickoffs
                        clock = play.get("clock", {})
                        if clock:
                            clock_display = clock.get("displayValue", "")
                            if clock_display:
                                play_text = f"[{clock_display}] {play_text}"
                        
                        html += f'<li class="play-item kickoff">{play_text}</li>'
                        continue
                    
                    # Add down and distance information for regular plays
                    start = play.get("start", {})
                    down = start.get("down", 0)
                    distance = start.get("distance", 0)
                    possession_text = start.get("possessionText", "")
                    yards_to_endzone = start.get("yardsToEndzone", 0)
                    
                    # Get additional NFL-specific data
                    stat_yardage = play.get("statYardage", 0)
                    play_type_obj = play.get("type", {})
                    play_type_name = play_type_obj.get("text", "")
                    
                    # Build enhanced play description
                    enhanced_text = play_text
                    
                    # Add yardage information if available
                    if stat_yardage != 0:
                        yardage_display = f"(+{stat_yardage} yards)" if stat_yardage > 0 else f"({stat_yardage} yards)"
                        enhanced_text = f"{yardage_display} {enhanced_text}"
                    
                    # Add play type for clarity (accessible text)
                    if play_type_name and play_type_name.lower() not in enhanced_text.lower():
                        if "pass" in play_type_name.lower():
                            enhanced_text = f"PASS: {enhanced_text}"
                        elif "rush" in play_type_name.lower():
                            enhanced_text = f"RUSH: {enhanced_text}"
                        elif "sack" in play_type_name.lower():
                            enhanced_text = f"SACK: {enhanced_text}"
                        elif "penalty" in play_type_name.lower():
                            enhanced_text = f"PENALTY: {enhanced_text}"
                        elif "punt" in play_type_name.lower():
                            enhanced_text = f"PUNT: {enhanced_text}"
                        elif "field goal" in play_type_name.lower():
                            enhanced_text = f"FIELD GOAL: {enhanced_text}"
                    
                    # Add situational context
                    situation_prefix = ""
                    situation_class = ""
                    if yards_to_endzone <= 5:
                        situation_prefix = "GOAL LINE "
                        situation_class = "goal-line"
                    elif yards_to_endzone <= 20:
                        situation_prefix = "RED ZONE "
                        situation_class = "red-zone"
                    elif down == 4:
                        situation_prefix = "4TH DOWN "
                        situation_class = "fourth-down"
                    
                    # Use start data for down/distance display (not end!)
                    down_distance_prefix = ""
                    if down > 0:  # Regular downs
                        if possession_text:
                            if situation_prefix:
                                down_distance_prefix = f"[{situation_prefix}{down} & {distance} from {possession_text}] "
                            else:
                                down_distance_prefix = f"[{down} & {distance} from {possession_text}] "
                        else:
                            down_distance_prefix = f"[{situation_prefix}{down} & {distance}] "
                    
                    # Check for scoring play
                    scoring_class = ""
                    if play.get("scoringPlay"):
                        scoring_class = "scoring"
                        away_score = play.get("awayScore", 0)
                        home_score = play.get("homeScore", 0)
                        play_text = f"TOUCHDOWN: {down_distance_prefix}{enhanced_text} ({away_score}-{home_score})"
                    else:
                        play_text = f"{down_distance_prefix}{enhanced_text}"
                    
                    # Add clock context
                    clock = play.get("clock", {})
                    if clock:
                        clock_display = clock.get("displayValue", "")
                        if clock_display:
                            play_text = f"[{clock_display}] {play_text}"
                    
                    # Combine CSS classes
                    css_classes = f"play-item {scoring_class} {situation_class}".strip()
                    html += f'<li class="{css_classes}">{play_text}</li>'
                
                html += '</ul>'
                html += '</div>'
            
            html += '</div>'
        
        return html
    
    def _generate_generic_html(self):
        """Generate HTML for generic sport game log"""
        html = '<div class="period">'
        html += '<div class="period-header">All Plays</div>'
        
        for i, play in enumerate(self.current_plays_data, 1):
            play_text = play.get("text", f"Play {i}")
            html += f'<div class="play">{play_text}</div>'
        
        html += '</div>'
        return html

    def _add_injuries_list_to_layout(self, layout, data):
        """Add injuries list to layout using accessible table"""
        if not data:
            layout.addWidget(QLabel("No injury data available."))
            return
        
        # Create accessible injury table
        injury_table = InjuryTable(parent=self, title="Injury Report")
        injury_table.setColumnCount(len(INJURY_HEADERS))
        injury_table.setHorizontalHeaderLabels(INJURY_HEADERS)
        
        # Populate with injury data using the specialized method
        injury_table.populate_injury_data(data, set_focus=True)
        
        # Configure table appearance
        header = injury_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Player name stretches
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Team name stretches
        
        layout.addWidget(injury_table)
    
    def _add_officials_list_to_layout(self, layout, data):
        """Add officials list to layout"""
        if not data:
            layout.addWidget(QLabel("No officials data available."))
            return
        
        # Create a clean list widget for officials
        officials_list = QListWidget()
        officials_list.setAccessibleName("Officials List")
        officials_list.setAccessibleDescription("List of game officials and their positions")
        
        for official in data:
            name = official.get('displayName', 'Unknown Official')
            position_info = official.get('position', {})
            position = position_info.get('displayName', 'Unknown Position')
            order = official.get('order', 0)
            
            # Create formatted display text
            list_item = f"{order}. {name} - {position}"
            officials_list.addItem(list_item)
        
        layout.addWidget(officials_list)
    
    def _add_news_list_to_layout(self, layout, data):
        """Add news list to layout"""
        if not data:
            layout.addWidget(QLabel("No news data available."))
            return
        
        # Handle different news data formats and enhance game-specific news
        news_articles = []
        
        # Check if this is game details data that might have both 'article' and 'news'
        if isinstance(data, dict):
            if "articles" in data:
                # Standard news format with articles array
                news_articles = data["articles"]
            elif "article" in data or "news" in data:
                # This might be full game details - check for game-specific article first
                game_article = data.get("article")
                general_news = data.get("news", {}).get("articles", [])
                
                # Prioritize game-specific article, then add general news
                if game_article and isinstance(game_article, dict):
                    news_articles.append(game_article)
                if general_news and isinstance(general_news, list):
                    news_articles.extend(general_news)
            else:
                # Single article format
                news_articles = [data]
        elif isinstance(data, list):
            # Direct list of articles
            news_articles = data
        
        if not news_articles:
            layout.addWidget(QLabel("No news articles available."))
            return
        
        # Create list widget for news headlines (consistent with other views)
        news_list = QListWidget()
        news_list.setAccessibleName("News Headlines List")
        news_list.setAccessibleDescription("List of news headlines - Enter or double-click opens in browser")
        
        # Add articles as list items, with special labeling for game-specific content
        for i, news_item in enumerate(news_articles):
            news_data = NewsData(news_item)
            # Get just the headline for consistent list display
            headline = news_data.headline if hasattr(news_data, 'headline') else news_data.get_display_text()
            
            # Add indicator for game-specific article (first item if it came from 'article' field)
            if i == 0 and isinstance(data, dict) and "article" in data and "news" in data:
                headline = f"🎯 {headline}"  # Game-specific indicator
            
            item = QListWidgetItem(headline)
            item.setData(Qt.ItemDataRole.UserRole, news_data)
            news_list.addItem(item)
        
        # Connect activation (Enter key or double-click) to open in browser
        def open_news_item(item):
            news_data = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(news_data, NewsData) and news_data.has_web_url():
                if news_data.web_url.startswith(("http://", "https://")):
                    try:
                        webbrowser.open(news_data.web_url)
                    except Exception as e:
                        QMessageBox.warning(None, "Browser Error", f"Could not open browser: {str(e)}")
                else:
                    QMessageBox.warning(None, "Invalid URL", "The URL for this story is invalid.")
            else:
                QMessageBox.information(None, "No Link", "No web link available for this story.")
        
        news_list.itemActivated.connect(open_news_item)
        news_list.itemDoubleClicked.connect(open_news_item)
        
        layout.addWidget(QLabel("News Headlines (🎯 = Game-specific, Enter or double-click to open in browser):"))
        layout.addWidget(news_list)
    
    def keyPressEvent(self, event):
        """Handle key press events, but let dialog handle Escape when in modal context"""
        if event.key() == Qt.Key.Key_Escape:
            # Check if we're in a dialog context
            parent_widget = self.parent()
            while parent_widget:
                if isinstance(parent_widget, QDialog):
                    # Let the dialog handle the escape key
                    parent_widget.keyPressEvent(event)
                    return
                parent_widget = parent_widget.parent()
            
            # If not in dialog, use BaseView's escape handling
            super().keyPressEvent(event)
        else:
            # For all other keys, use BaseView's handling
            super().keyPressEvent(event)

class StandingsDetailDialog(QDialog):
    """Dialog for displaying team standings from game details with keyboard navigation"""
    
    def __init__(self, standings_data: List, league: str, parent=None):
        super().__init__(parent)
        self.standings_data = StandingsData(standings_data)
        self.league = league
        self.setWindowTitle(f"{league} Standings Details")
        self.resize(STANDINGS_DIALOG_WIDTH, STANDINGS_DIALOG_HEIGHT)
        
        self.tab_widget: QTabWidget | None = None
        self.single_table: StandingsTable | None = None
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        if not self.standings_data.teams:
            layout.addWidget(QLabel(f"No standings data available for {self.league}."))
        else:
            has_divisions = len(self.standings_data.divisions) > 1 or any(
                div != "League" for div in self.standings_data.divisions.keys()
            )
            if has_divisions and self.league in ["MLB", "NFL"]:
                self._build_division_tabs(layout)
            else:
                self.single_table = self._create_single_standings_table(self.standings_data.teams)
                layout.addWidget(QLabel(f"Current {self.league} Standings:"))
                layout.addWidget(self.single_table)
                self.single_table.setFocus()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)
    
    def _build_division_tabs(self, layout: QVBoxLayout):
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Division Standings")
        self.tab_widget.setAccessibleDescription("Team standings by division, use arrow keys to navigate between divisions")
        
        if self.league == "MLB":
            division_order = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West", "League"]
        elif self.league == "NFL":
            division_order = ["AFC East", "AFC North", "AFC South", "AFC West", 
                            "NFC East", "NFC North", "NFC South", "NFC West", "League"]
        else:
            division_order = ["League"]
            
        ordered: List[tuple[str, List[Dict]]] = []
        for name in division_order:
            if name in self.standings_data.divisions:
                ordered.append((name, self.standings_data.divisions[name]))
        for name, teams in self.standings_data.divisions.items():
            if name not in division_order:
                ordered.append((name, teams))
        for name, teams in ordered:
            if teams:
                tab = self._create_division_table(name, teams)
                self.tab_widget.addTab(tab, name)
        layout.addWidget(self.tab_widget)
        if self.tab_widget.count():
            first = self.tab_widget.widget(0)
            if hasattr(first, "table"):
                first.table.setFocus()  # type: ignore[attr-defined]
    
    def _create_division_table(self, division_name: str, teams: List[Dict]) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        table = StandingsTable(parent=self, division_name=division_name)
        table.populate_standings(teams, set_focus=True)
        layout.addWidget(table)
        widget.setLayout(layout)
        widget.table = table  # type: ignore[attr-defined]
        return widget
    
    def _create_single_standings_table(self, teams: List[Dict]) -> StandingsTable:
        table = StandingsTable(parent=self)
        table.populate_standings(teams, set_focus=True)
        return table
    
    def _configure_table(self, table: QTableWidget):
        """Configure table appearance and behavior"""
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)  # Allow cell selection
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Enable keyboard navigation
        table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        table.setTabKeyNavigation(True)
        
        # Enable accessibility features
        table.setAccessibleName("Standings Table")
        table.setAccessibleDescription("Team standings with arrow key navigation. Use arrow keys to navigate cells, Tab to enter/exit table.")
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        if table.columnCount() > 1:
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Team name stretches

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        if self.tab_widget:
            if event.key() == Qt.Key.Key_F6:
                self.tab_widget.setFocus(); event.accept(); return
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if event.key() == Qt.Key.Key_Tab:
                    i = (self.tab_widget.currentIndex() + 1) % self.tab_widget.count()
                    self.tab_widget.setCurrentIndex(i)
                    w = self.tab_widget.widget(i)
                    if hasattr(w, "table"):
                        w.table.setFocus()  # type: ignore[attr-defined]
                    event.accept(); return
                if event.key() == Qt.Key.Key_Backtab:
                    i = (self.tab_widget.currentIndex() - 1) % self.tab_widget.count()
                    self.tab_widget.setCurrentIndex(i)
                    w = self.tab_widget.widget(i)
                    if hasattr(w, "table"):
                        w.table.setFocus()  # type: ignore[attr-defined]
                    event.accept(); return
        super().keyPressEvent(event)

class KitchenSinkDialog(QDialog):
    """Dialog for displaying additional MLB data features not shown in main views"""
    
    def __init__(self, raw_game_data: Dict, parent=None):
        super().__init__(parent)
        self.raw_data = raw_game_data
        self.setWindowTitle("Kitchen Sink - Additional MLB Data")
        self.resize(1000, 700)
        
        self.tab_widget: QTabWidget | None = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create tabs for different data types
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Kitchen Sink Data")
        self.tab_widget.setAccessibleDescription("Additional baseball data features, use arrow keys to navigate between sections")
        
        # Add tabs for each available feature (only if data exists)
        self._add_rosters_tab()
        self._add_season_series_tab()
        self._add_articles_tab()
        self._add_betting_tab()
        self._add_picks_tab()
        self._add_win_probability_tab()
        self._add_videos_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Set focus to first tab
        if self.tab_widget.count() > 0:
            self.tab_widget.setCurrentIndex(0)
            QTimer.singleShot(50, lambda: self.tab_widget.setFocus())
    
    def _add_rosters_tab(self):
        """Add rosters/lineups tab"""
        rosters_data = self.raw_data.get("rosters")
        if not rosters_data:
            return
            
        scroll_area = QScrollArea()
        content_widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🧑‍🤝‍🧑 STARTING LINEUPS & ROSTERS"))
        
        if isinstance(rosters_data, list):
            for team_data in rosters_data:
                if isinstance(team_data, dict):
                    team_info = team_data.get("team", {})
                    team_name = team_info.get("displayName", "Unknown Team")
                    layout.addWidget(QLabel(f"\n{team_name}:"))
                    
                    roster = team_data.get("roster", [])
                    if roster:
                        table = AccessibleTable()
                        table.setColumnCount(4)
                        table.setHorizontalHeaderLabels(["Position", "Player", "Number", "Status"])
                        
                        table.setRowCount(len(roster))
                        for row, player in enumerate(roster):
                            position = player.get("position", {})
                            pos_name = position.get("displayName", "") if isinstance(position, dict) else str(position)
                            
                            athlete = player.get("athlete", {})
                            player_name = athlete.get("displayName", "") if isinstance(athlete, dict) else str(athlete)
                            jersey = athlete.get("jersey", "") if isinstance(athlete, dict) else ""
                            
                            status = player.get("status", "")
                            
                            table.setItem(row, 0, QTableWidgetItem(pos_name))
                            table.setItem(row, 1, QTableWidgetItem(player_name))
                            table.setItem(row, 2, QTableWidgetItem(str(jersey)))
                            table.setItem(row, 3, QTableWidgetItem(str(status)))
                        
                        table.resizeColumnsToContents()
                        layout.addWidget(table)
                    else:
                        layout.addWidget(QLabel("  No roster data available"))
        else:
            layout.addWidget(QLabel("No roster data available"))
        
        content_widget.setLayout(layout)
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        self.tab_widget.addTab(scroll_area, "Rosters")
    
    def _add_season_series_tab(self):
        """Add season series head-to-head tab"""
        series_data = self.raw_data.get("seasonseries")
        if not series_data:
            return
            
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🗓️ SEASON SERIES (Head-to-Head Record)"))
        
        if isinstance(series_data, list):
            for series_item in series_data:
                if isinstance(series_item, dict):
                    summary = series_item.get("summary", "No series data available")
                    layout.addWidget(QLabel(f"\nSeries Summary: {summary}"))
                    
                    # Show individual games if available
                    events = series_item.get("events", [])
                    if events:
                        layout.addWidget(QLabel(f"\nGames in Series ({len(events)} total):"))
                        
                        table = AccessibleTable()
                        table.setColumnCount(4)
                        table.setHorizontalHeaderLabels(["Date", "Matchup", "Score", "Result"])
                        
                        table.setRowCount(len(events))
                        for row, event in enumerate(events):
                            date = event.get("date", "")
                            name = event.get("name", "")
                            score = event.get("shortName", "")
                            status = event.get("status", {})
                            completed = status.get("type", {}).get("completed", False) if isinstance(status, dict) else False
                            result = "Completed" if completed else "Scheduled"
                            
                            table.setItem(row, 0, QTableWidgetItem(date))
                            table.setItem(row, 1, QTableWidgetItem(name))
                            table.setItem(row, 2, QTableWidgetItem(score))
                            table.setItem(row, 3, QTableWidgetItem(result))
                        
                        table.resizeColumnsToContents()
                        layout.addWidget(table)
        else:
            layout.addWidget(QLabel("No season series data available"))
        
        widget.setLayout(layout)
        self.tab_widget.addTab(widget, "Season Series")
    
    def _add_win_probability_tab(self):
        """Add win probability tracking tab"""
        win_prob_data = self.raw_data.get("winprobability")
        if not win_prob_data or (isinstance(win_prob_data, list) and len(win_prob_data) == 0):
            return
            
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📊 WIN PROBABILITY TRACKING"))
        
        if isinstance(win_prob_data, list) and win_prob_data:
            layout.addWidget(QLabel(f"\nTotal probability data points: {len(win_prob_data)}"))
            
            # Show current/final probability
            latest = win_prob_data[-1] if win_prob_data else {}
            home_prob = latest.get("homeWinPercentage", 0)
            away_prob = 100 - home_prob
            
            layout.addWidget(QLabel(f"Final/Current Probabilities:"))
            layout.addWidget(QLabel(f"  Home Team: {home_prob:.1f}%"))
            layout.addWidget(QLabel(f"  Away Team: {away_prob:.1f}%"))
            
            # Show probability changes over time (sample)
            if len(win_prob_data) > 5:
                layout.addWidget(QLabel(f"\nSample probability changes:"))
                
                table = AccessibleTable()
                table.setColumnCount(3)
                table.setHorizontalHeaderLabels(["Play", "Home Win %", "Away Win %"])
                
                # Show first 10 entries as sample
                sample_data = win_prob_data[:10]
                table.setRowCount(len(sample_data))
                
                for row, prob_point in enumerate(sample_data):
                    play_id = str(prob_point.get("playId", f"Play {row+1}"))
                    home_pct = f"{prob_point.get('homeWinPercentage', 0):.1f}%"
                    away_pct = f"{100 - prob_point.get('homeWinPercentage', 0):.1f}%"
                    
                    table.setItem(row, 0, QTableWidgetItem(play_id))
                    table.setItem(row, 1, QTableWidgetItem(home_pct))
                    table.setItem(row, 2, QTableWidgetItem(away_pct))
                
                table.resizeColumnsToContents()
                layout.addWidget(table)
        else:
            layout.addWidget(QLabel("No win probability data available"))
        
        widget.setLayout(layout)
        self.tab_widget.addTab(widget, "Win Probability")
    
    def _add_articles_tab(self):
        """Add game articles/recaps tab"""
        article_data = self.raw_data.get("article")
        if not article_data:
            return
            
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📰 GAME ARTICLES & RECAPS"))
        
        # Handle both single article and multiple articles
        articles_list = []
        if isinstance(article_data, dict):
            # Single article
            articles_list = [article_data]
        elif isinstance(article_data, list):
            # Multiple articles
            articles_list = article_data
        
        if articles_list:
            # Create list widget for articles (consistent with news display)
            articles_list_widget = QListWidget()
            articles_list_widget.setAccessibleName("Game Articles List")
            articles_list_widget.setAccessibleDescription("List of game articles and recaps")
            
            # Add each article as a list item (just the headline)
            for article in articles_list:
                if isinstance(article, dict):
                    headline = article.get("headline", "No headline")
                    article_type = article.get("type", "")
                    
                    # Create clean headline display
                    display_text = headline
                    if article_type and article_type != "Unknown":
                        display_text = f"[{article_type}] {headline}"
                    
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, article)
                    articles_list_widget.addItem(item)
            
            # Connect activation to show full article details
            def show_article_details(item):
                article = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(article, dict):
                    # Create a detailed view dialog
                    dialog = QDialog(self)
                    dialog.setWindowTitle("Article Details")
                    dialog.resize(600, 400)
                    
                    dialog_layout = QVBoxLayout()
                    
                    headline = article.get("headline", "No headline")
                    article_type = article.get("type", "Unknown")
                    description = article.get("description", "")
                    story = article.get("story", "")
                    
                    dialog_layout.addWidget(QLabel(f"Headline: {headline}"))
                    dialog_layout.addWidget(QLabel(f"Type: {article_type}"))
                    
                    if description:
                        dialog_layout.addWidget(QLabel("\nDescription:"))
                        desc_text = QTextEdit()
                        desc_text.setPlainText(description)
                        desc_text.setReadOnly(True)
                        desc_text.setMaximumHeight(100)
                        dialog_layout.addWidget(desc_text)
                    
                    if story:
                        dialog_layout.addWidget(QLabel("\nFull Article:"))
                        story_text = QTextEdit()
                        story_text.setPlainText(story)
                        story_text.setReadOnly(True)
                        dialog_layout.addWidget(story_text)
                    
                    close_btn = QPushButton("Close")
                    close_btn.clicked.connect(dialog.accept)
                    dialog_layout.addWidget(close_btn)
                    
                    dialog.setLayout(dialog_layout)
                    dialog.exec()
            
            articles_list_widget.itemActivated.connect(show_article_details)
            articles_list_widget.itemDoubleClicked.connect(show_article_details)
            
            layout.addWidget(QLabel("\nArticles (Enter or double-click to view details):"))
            layout.addWidget(articles_list_widget)
        else:
            layout.addWidget(QLabel("No article data available"))
        
        widget.setLayout(layout)
        self.tab_widget.addTab(widget, "Articles")
    
    def _add_videos_tab(self):
        """Add game videos/highlights tab"""
        videos_data = self.raw_data.get("videos")
        if not videos_data or (isinstance(videos_data, list) and len(videos_data) == 0):
            return
            
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🎥 GAME HIGHLIGHTS & VIDEOS"))
        
        if isinstance(videos_data, list) and videos_data:
            layout.addWidget(QLabel(f"\nAvailable videos: {len(videos_data)}"))
            
            table = AccessibleTable()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Title", "Description", "Duration", "Keywords"])
            
            table.setRowCount(len(videos_data))
            for row, video in enumerate(videos_data):
                title = video.get("headline", video.get("title", ""))
                description = video.get("description", "")
                duration = f"{video.get('duration', 0)} seconds"
                keywords = ", ".join(video.get("keywords", []))
                
                table.setItem(row, 0, QTableWidgetItem(title))
                table.setItem(row, 1, QTableWidgetItem(description))
                table.setItem(row, 2, QTableWidgetItem(duration))
                table.setItem(row, 3, QTableWidgetItem(keywords))
            
            table.resizeColumnsToContents()
            layout.addWidget(table)
        else:
            layout.addWidget(QLabel("No video data available"))
        
        widget.setLayout(layout)
        self.tab_widget.addTab(widget, "Videos")
    
    def _add_betting_tab(self):
        """Add against the spread betting performance tab"""
        ats_data = self.raw_data.get("againstTheSpread")
        if not ats_data:
            return
            
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🎰 AGAINST THE SPREAD PERFORMANCE"))
        
        if isinstance(ats_data, list):
            for team_data in ats_data:
                if isinstance(team_data, dict):
                    team_name = team_data.get("displayName", "Unknown Team")
                    record = team_data.get("record", "No record")
                    
                    layout.addWidget(QLabel(f"\n{team_name}:"))
                    layout.addWidget(QLabel(f"  ATS Record: {record}"))
        else:
            layout.addWidget(QLabel("No betting performance data available"))
        
        widget.setLayout(layout)
        self.tab_widget.addTab(widget, "Betting ATS")
    
    def _add_picks_tab(self):
        """Add expert picks and predictions tab"""
        picks_data = self.raw_data.get("pickcenter")
        if not picks_data:
            return
            
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🎯 EXPERT PICKS & PREDICTIONS"))
        
        if isinstance(picks_data, list) and picks_data:
            for pick_item in picks_data:
                if isinstance(pick_item, dict):
                    provider = pick_item.get("provider", {}).get("name", "Unknown")
                    details = pick_item.get("details", "")
                    spread = pick_item.get("spread", "")
                    over_under = pick_item.get("overUnder", "")
                    
                    layout.addWidget(QLabel(f"\nProvider: {provider}"))
                    if details:
                        layout.addWidget(QLabel(f"Pick Details: {details}"))
                    if spread:
                        layout.addWidget(QLabel(f"Spread: {spread}"))
                    if over_under:
                        layout.addWidget(QLabel(f"Over/Under: {over_under}"))
        else:
            layout.addWidget(QLabel("No expert picks data available"))
        
        widget.setLayout(layout)
        self.tab_widget.addTab(widget, "Expert Picks")
    
    def keyPressEvent(self, event):
        """Handle F6 for tab navigation and Escape to close"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        elif event.key() == Qt.Key.Key_F6 and self.tab_widget:
            current_tab = self.tab_widget.currentIndex()
            next_tab = (current_tab + 1) % self.tab_widget.count()
            self.tab_widget.setCurrentIndex(next_tab)
            self.tab_widget.setFocus()
            event.accept()
            return
        super().keyPressEvent(event)

class NewsDialog(QDialog):
    """Dialog for displaying news headlines"""
    
    def __init__(self, news_headlines: List, league: str, parent=None):
        super().__init__(parent)
        self.news_headlines = news_headlines
        self.league = league
        self.setWindowTitle(f"News Headlines - {league}")
        self.resize(NEWS_DIALOG_WIDTH, NEWS_DIALOG_HEIGHT)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        if not self.news_headlines:
            layout.addWidget(QLabel("No news headlines available for this league."))
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.accept)
            layout.addWidget(close_btn)
            self.setLayout(layout)
            return
        
        self.news_list = QListWidget()
        self.news_list.setAccessibleName("News Headlines List")
        self.news_list.setAccessibleDescription("List of news headlines - Enter or double-click opens in browser")
        
        # Display headlines as consistent list items
        for item in self.news_headlines:
            news = NewsData(item)
            # Get just the headline for consistent display
            headline = news.headline if hasattr(news, 'headline') else news.get_display_text()
            list_item = QListWidgetItem(headline)
            list_item.setData(Qt.ItemDataRole.UserRole, news)
            self.news_list.addItem(list_item)
        
        self.news_list.itemActivated.connect(self._open_news_story)
        self.news_list.itemDoubleClicked.connect(self._open_news_story)
        
        layout.addWidget(QLabel("Press Enter or double-click a headline to open in your browser:"))
        layout.addWidget(self.news_list)
        
        btn_row = QHBoxLayout()
        open_btn = QPushButton("Open Selected")
        open_btn.clicked.connect(lambda: self._open_selected_news_story())
        btn_row.addWidget(open_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)
        
        self.setLayout(layout)
        self.news_list.setFocus()
    
    def keyPressEvent(self, event):
        """Handle Escape key to close dialog"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
    
    def _open_news_story(self, item):
        if isinstance(item, QListWidgetItem):
            news_data = item.data(Qt.ItemDataRole.UserRole)
        else:
            news_data = item.data(Qt.ItemDataRole.UserRole) if item else None  # fallback
        if isinstance(news_data, NewsData) and news_data.has_web_url():
            if news_data.web_url.startswith(("http://", "https://")):
                webbrowser.open(news_data.web_url)
            else:
                QMessageBox.warning(self, "Invalid URL", "The URL for this story is invalid.")
        else:
            QMessageBox.information(self, "No Link", "No web link available for this story.")
    
    def _open_selected_news_story(self):
        item = self.news_list.currentItem()
        if item:
            self._open_news_story(item)
        else:
            QMessageBox.information(self, "No Selection", "Select a story first.")


# Background loading classes for performance optimization

class StandingsLoader(QThread):
    """Background thread for loading standings data"""
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, league: str):
        super().__init__()
        self.league = league
    
    def run(self):
        try:
            standings_data = ApiService.get_standings(self.league)
            if standings_data:
                self.data_loaded.emit(standings_data)
            else:
                self.error_occurred.emit(f"No standings data available for {self.league}")
        except Exception as e:
            self.error_occurred.emit(f"Failed to load standings: {str(e)}")


class GameDetailsDialog(QDialog):
    """Dialog wrapper for GameDetailsView to show game details"""
    
    def __init__(self, game_id: str, league: str, parent=None):
        super().__init__(parent)
        self.game_id = game_id
        self.league = league
        
        # Add config attribute that GameDetailsView expects
        self.config = {league: ["standings", "leaders", "boxscore", "injuries", "news"]}
        
        self.setWindowTitle(f"Game Details - {league}")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create game details view
        self.game_details_view = GameDetailsView(self, league, game_id)
        layout.addWidget(self.game_details_view)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("&Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        super().keyPressEvent(event)


class TeamScheduleDialog(QDialog):
    """Dialog showing a team's schedule with focus on today's game"""
    
    def __init__(self, team_data: Dict, league: str, parent=None):
        super().__init__(parent)
        self.team_data = team_data
        self.league = league
        self.team_name = team_data.get('team_name', 'Unknown Team')
        self.team_id = team_data.get('team_id', '')
        
        self.setWindowTitle(f"{self.team_name} - Schedule")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        self.setup_ui()
        self.load_schedule()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header with team info
        header_layout = QHBoxLayout()
        
        team_info = QLabel(f"{self.team_name}")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        team_info.setFont(font)
        header_layout.addWidget(team_info)
        
        # Add team record if available
        wins = self.team_data.get('wins', '')
        losses = self.team_data.get('losses', '')
        if wins and losses:
            record_label = QLabel(f"({wins}-{losses})")
            record_label.setFont(font)
            header_layout.addWidget(record_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Season selector
        season_layout = QHBoxLayout()
        season_label = QLabel("Season:")
        season_layout.addWidget(season_label)
        
        self.season_combo = QComboBox()
        self.season_combo.setAccessibleName("Season Selection")
        self.season_combo.setAccessibleDescription("Select a season to view the team's schedule")
        
        # Populate seasons
        try:
            available_seasons = ApiService.get_available_seasons(self.league)
            for season_value, season_display in available_seasons:
                self.season_combo.addItem(season_display, season_value)
        except Exception as e:
            # Fallback if API call fails
            from datetime import datetime
            current_year = datetime.now().year
            for year in range(current_year, current_year - 3, -1):
                self.season_combo.addItem(f"{year} Season", year)
        
        self.season_combo.currentIndexChanged.connect(self.on_season_changed)
        season_layout.addWidget(self.season_combo)
        season_layout.addStretch()
        layout.addLayout(season_layout)
        
        # Schedule list
        self.schedule_list = QListWidget()
        self.schedule_list.setAccessibleName(f"{self.team_name} Schedule")
        self.schedule_list.itemActivated.connect(self.on_game_selected)
        layout.addWidget(self.schedule_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("&Refresh")
        refresh_btn.clicked.connect(self.load_schedule)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("&Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def on_season_changed(self):
        """Handle season selection change"""
        self.load_schedule()
    
    def load_schedule(self):
        """Load team schedule data"""
        self.schedule_list.clear()
        
        # Show loading message
        self.loading_item = QListWidgetItem("Loading schedule...")
        self.schedule_list.addItem(self.loading_item)
        
        # Get selected season
        selected_season = None
        if hasattr(self, 'season_combo') and self.season_combo.currentData():
            selected_season = self.season_combo.currentData()
        
        # Start background loading
        self.schedule_loader = TeamScheduleLoader(self.team_id, self.team_name, self.league, selected_season)
        self.schedule_loader.data_loaded.connect(self.on_schedule_loaded)
        self.schedule_loader.error_occurred.connect(self.on_schedule_error)
        self.schedule_loader.loading_progress.connect(self.on_loading_progress)
        self.schedule_loader.start()

    def on_loading_progress(self, message: str):
        """Update loading progress message"""
        if hasattr(self, 'loading_item') and self.loading_item:
            self.loading_item.setText(message)

    def on_schedule_loaded(self, schedule_data: List[Dict], team_name: str, league: str):
        """Handle successful schedule loading"""
        self.schedule_list.clear()
        
        if not schedule_data:
            no_games_item = QListWidgetItem("No games found in schedule")
            self.schedule_list.addItem(no_games_item)
            return

        today_item_index = -1
        
        for i, game in enumerate(schedule_data):
            # Format game display
            date_str = game.get('date_display', '')
            opponent = game.get('opponent', 'Unknown')
            home_away = game.get('home_away', '')
            time_str = game.get('time', '')
            status = game.get('status', '')
            venue = game.get('venue', '')
            
            # Build game text
            if status in ['Final', 'Cancelled', 'Postponed']:
                home_score = game.get('home_score', '')
                away_score = game.get('away_score', '')
                if home_score and away_score:
                    if home_away == 'vs':  # Home game
                        game_text = f"{date_str}: {home_away} {opponent} - W {home_score}-{away_score}" if int(home_score) > int(away_score) else f"{date_str}: {home_away} {opponent} - L {home_score}-{away_score}"
                    else:  # Away game  
                        game_text = f"{date_str}: {home_away} {opponent} - W {away_score}-{home_score}" if int(away_score) > int(home_score) else f"{date_str}: {home_away} {opponent} - L {away_score}-{home_score}"
                else:
                    game_text = f"{date_str}: {home_away} {opponent} - {status}"
            else:
                game_text = f"{date_str}: {home_away} {opponent} - {time_str}"
                if venue and venue != "TBD":
                    game_text += f" ({venue})"
            
            item = QListWidgetItem(game_text)
            item.setData(Qt.ItemDataRole.UserRole, game)
            
            # Highlight today's game
            if game.get('is_today', False):
                font = QFont()
                font.setBold(True)
                item.setFont(font)
                item.setBackground(QColor(255, 255, 200))  # Light yellow background
                today_item_index = i
            
            self.schedule_list.addItem(item)
        
        # Focus on today's game if found, otherwise focus on first upcoming game
        if today_item_index >= 0:
            self.schedule_list.setCurrentRow(today_item_index)
        else:
            # Find first future game
            future_game_index = -1
            for i, game in enumerate(schedule_data):
                if game.get('status', '') not in ['Final', 'Cancelled', 'Postponed']:
                    future_game_index = i
                    break
            
            if future_game_index >= 0:
                self.schedule_list.setCurrentRow(future_game_index)
            else:
                # No future games, focus on first item
                self.schedule_list.setCurrentRow(0)
        
        # Set focus to the list
        self.schedule_list.setFocus()
    
    def on_schedule_error(self, error_msg: str):
        """Handle schedule loading error"""
        self.schedule_list.clear()
        error_item = QListWidgetItem(f"Error loading schedule: {error_msg}")
        self.schedule_list.addItem(error_item)
    
    def on_game_selected(self, item):
        """Handle game selection"""
        game_data = item.data(Qt.ItemDataRole.UserRole)
        if not game_data:
            return
        
        game_id = game_data.get('game_id')
        if game_id:
            # Open game details in a new dialog
            try:
                detail_dialog = GameDetailsDialog(game_id, self.league, self)
                detail_dialog.exec()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open game details: {str(e)}")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        super().keyPressEvent(event)


class TeamScheduleLoader(QThread):
    """Background thread for loading team schedule data"""
    data_loaded = pyqtSignal(list, str, str)  # schedule_data, team_name, league
    error_occurred = pyqtSignal(str)
    loading_progress = pyqtSignal(str)  # progress message
    
    def __init__(self, team_id: str, team_name: str, league: str, season=None):
        super().__init__()
        self.team_id = team_id
        self.team_name = team_name
        self.league = league
        self.season = season
    
    def run(self):
        try:
            self.loading_progress.emit("Loading schedule...")
            
            # Load team schedule using the optimized API
            schedule_data = ApiService.get_team_schedule(self.league, self.team_id, season=self.season)
            
            self.loading_progress.emit(f"Loaded {len(schedule_data)} games")
            self.data_loaded.emit(schedule_data, self.team_name, self.league)
        except Exception as e:
            self.error_occurred.emit(f"Failed to load schedule: {str(e)}")


# Caching system for improved performance
class DataCache:
    """Simple cache for standings and team data"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.standings_cache = {}
            cls._instance.schedule_cache = {}
            cls._instance.cache_timeout = 300  # 5 minutes
        return cls._instance
    
    def get_standings(self, league: str):
        """Get cached standings data"""
        key = f"standings_{league}"
        if key in self.standings_cache:
            data, timestamp = self.standings_cache[key]
            if time.time() - timestamp < self.cache_timeout:
                return data
        return None
    
    def set_standings(self, league: str, data):
        """Cache standings data"""
        key = f"standings_{league}"
        self.standings_cache[key] = (data, time.time())
    
    def get_schedule(self, team_id: str):
        """Get cached schedule data"""
        key = f"schedule_{team_id}"
        if key in self.schedule_cache:
            data, timestamp = self.schedule_cache[key]
            if time.time() - timestamp < self.cache_timeout:
                return data
        return None
    
    def set_schedule(self, team_id: str, data):
        """Cache schedule data"""
        key = f"schedule_{team_id}"
        self.schedule_cache[key] = (data, time.time())


class StandingsDialog(QDialog):
    """Dialog for displaying team standings (invoked from league view)"""
    
    def __init__(self, standings_data: List, league: str, parent=None):
        super().__init__(parent)
        self.standings_data = StandingsData(standings_data)
        self.league = league
        self.setWindowTitle(f"{league} Standings")
        self.resize(STANDINGS_DIALOG_WIDTH, STANDINGS_DIALOG_HEIGHT)
        self.tab_widget: QTabWidget | None = None
        self.single_table: StandingsTable | None = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        if not self.standings_data.teams:
            layout.addWidget(QLabel(f"No standings data available for {self.league}."))
        else:
            has_divisions = len(self.standings_data.divisions) > 1 or any(
                d != "League" for d in self.standings_data.divisions
            )
            if has_divisions and self.league in ["MLB", "NFL"]:
                self._build_division_tabs(layout)
            else:
                self.single_table = self._create_single_standings_table(self.standings_data.teams)
                layout.addWidget(QLabel(f"Current {self.league} Standings:"))
                layout.addWidget(self.single_table)
                self.single_table.setFocus()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)
    
    def _build_division_tabs(self, layout: QVBoxLayout):
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Division Standings")
        self.tab_widget.setAccessibleDescription("Team standings by division, use arrow keys to navigate between divisions")
        
        if self.league == "MLB":
            division_order = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West", "League"]
        elif self.league == "NFL":
            division_order = ["AFC East", "AFC North", "AFC South", "AFC West", 
                            "NFC East", "NFC North", "NFC South", "NFC West", "League"]
        else:
            division_order = ["League"]
            
        ordered: List[tuple[str, List[Dict]]] = []
        for name in division_order:
            if name in self.standings_data.divisions:
                ordered.append((name, self.standings_data.divisions[name]))
        for name, teams in self.standings_data.divisions.items():
            if name not in division_order:
                ordered.append((name, teams))
        for name, teams in ordered:
            if teams:
                tab = self._create_division_table(name, teams)
                self.tab_widget.addTab(tab, name)
        layout.addWidget(self.tab_widget)
        if self.tab_widget.count():
            first = self.tab_widget.widget(0)
            if hasattr(first, "table"):
                first.table.setFocus()  # type: ignore[attr-defined]
    
    def _create_division_table(self, division_name: str, teams: List[Dict]) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        table = StandingsTable(parent=self, division_name=division_name)
        table.populate_standings(teams, set_focus=True)
        layout.addWidget(table)
        widget.setLayout(layout)
        widget.table = table  # type: ignore[attr-defined]
        return widget
    
    def _create_single_standings_table(self, teams: List[Dict]) -> StandingsTable:
        table = StandingsTable(parent=self)
        table.populate_standings(teams, set_focus=True)
        return table
    
    def _configure_table(self, table: QTableWidget):
        """Configure table appearance and behavior"""
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)  # Allow cell selection
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Enable keyboard navigation
        table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        table.setTabKeyNavigation(True)
        
        # Enable accessibility features
        table.setAccessibleName("Standings Table")
        table.setAccessibleDescription("Team standings with arrow key navigation. Use arrow keys to navigate cells, Tab to enter/exit table.")
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        if table.columnCount() > 1:
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Team name stretches

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        if self.tab_widget:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if event.key() == Qt.Key.Key_Tab:
                    i = (self.tab_widget.currentIndex() + 1) % self.tab_widget.count()
                    self.tab_widget.setCurrentIndex(i)
                    w = self.tab_widget.widget(i)
                    if hasattr(w, "table"):
                        w.table.setFocus()  # type: ignore[attr-defined]
                    event.accept(); return
                if event.key() == Qt.Key.Key_Backtab:
                    i = (self.tab_widget.currentIndex() - 1) % self.tab_widget.count()
                    self.tab_widget.setCurrentIndex(i)
                    w = self.tab_widget.widget(i)
                    if hasattr(w, "table"):
                        w.table.setFocus()  # type: ignore[attr-defined]
                    event.accept(); return
        super().keyPressEvent(event)


class SimpleTeamsDialog(QDialog):
    """Simple teams dialog with tabs for divisions"""
    
    def __init__(self, teams_data: List, league: str, parent=None):
        super().__init__(parent)
        self.teams_data = teams_data
        self.league = league
        self.setWindowTitle(f"{league} Teams")
        self.resize(600, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Team Information")
        self.tab_widget.setAccessibleDescription("Team information by division, use arrow keys to navigate between divisions")
        self.tab_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tab_widget.setUsesScrollButtons(False)  # Disable scroll buttons as requested
        
        # Group teams by division
        divisions = {}
        for team in self.teams_data:
            div = team.get('division', 'Other')
            if div == 'League':  # Skip generic league designation
                continue
            if div not in divisions:
                divisions[div] = []
            divisions[div].append(team)
        
        # Create tabs for each division
        if self.league == "MLB":
            division_order = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West"]
        elif self.league == "NFL":
            division_order = ["AFC East", "AFC North", "AFC South", "AFC West", 
                            "NFC East", "NFC North", "NFC South", "NFC West"]
        elif self.league == "NBA":
            division_order = ["Atlantic", "Central", "Southeast", "Northwest", "Pacific", "Southwest"]
        elif self.league == "NCAAF":
            # Use actual ESPN conference names
            division_order = ["Southeastern Conference", "Big Ten Conference", "Big 12 Conference", 
                            "Atlantic Coast Conference", "Pac-12 Conference", "American Conference", 
                            "Conference USA", "Mid-American Conference", "Mountain West Conference", 
                            "FBS Independents"]
        else:
            division_order = []
        
        # Add tabs in order
        for div_name in division_order:
            if div_name in divisions:
                self.create_division_tab(div_name, divisions[div_name])
        
        # Add any remaining divisions not in the standard order
        for div_name, teams in divisions.items():
            if div_name not in division_order:
                self.create_division_tab(div_name, teams)
        
        layout.addWidget(self.tab_widget)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Set focus on first tab
        if self.tab_widget.count() > 0:
            first_widget = self.tab_widget.widget(0)
            if hasattr(first_widget, 'teams_table'):
                first_widget.teams_table.setFocus()
    
    def keyPressEvent(self, event):
        """Handle key press events to keep focus in tab widget for left/right arrows"""
        key = event.key()
        
        # Handle left/right arrows to stay in tab widget
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            # Ensure focus stays on tab widget navigation
            self.tab_widget.setFocus()
            current_index = self.tab_widget.currentIndex()
            
            if key == Qt.Key.Key_Left:
                new_index = current_index - 1 if current_index > 0 else self.tab_widget.count() - 1
            else:  # Right arrow
                new_index = current_index + 1 if current_index < self.tab_widget.count() - 1 else 0
            
            self.tab_widget.setCurrentIndex(new_index)
            return
        
        # For all other keys, use default behavior
        super().keyPressEvent(event)
    
    def create_division_tab(self, division_name: str, teams: List):
        """Create a tab for a division with team table"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Create accessible table instead of list widget
        teams_table = AccessibleTable(
            parent=self,
            accessible_name=f"{division_name} Teams Table",
            accessible_description=f"Teams in {division_name} division with wins, losses, and other statistics"
        )
        
        # Set up table headers
        headers = ["Team", "Wins", "Losses", "Win %"]
        teams_table.setColumnCount(len(headers))
        teams_table.setHorizontalHeaderLabels(headers)
        
        # Sort teams by wins (descending), then by name (ascending) - ensure stable sort
        def sort_key(team):
            wins = team.get('wins', 0)
            name = team.get('team_name', 'Unknown Team')
            team_id = team.get('team_id', '')  # Add team_id for stable sorting
            # Return negative wins for descending order, then name for ascending, then ID for stability
            return (-wins, name, team_id)
        
        sorted_teams = sorted(teams, key=sort_key)
        
        # Set table row count
        teams_table.setRowCount(len(sorted_teams))
        
        # Populate table with team data
        for row, team in enumerate(sorted_teams):
            name = team.get('team_name', 'Unknown Team')
            wins = team.get('wins', 0)
            losses = team.get('losses', 0)
            
            # Calculate win percentage
            total_games = wins + losses
            win_pct = wins / total_games if total_games > 0 else 0.0
            
            # Create table items
            name_item = QTableWidgetItem(name)
            wins_item = QTableWidgetItem(str(wins))
            losses_item = QTableWidgetItem(str(losses))
            win_pct_item = QTableWidgetItem(f"{win_pct:.3f}")
            
            # Store team data in the name item for potential future use
            name_item.setData(Qt.ItemDataRole.UserRole, team)
            
            # Set items in table
            teams_table.setItem(row, 0, name_item)
            teams_table.setItem(row, 1, wins_item)
            teams_table.setItem(row, 2, losses_item)
            teams_table.setItem(row, 3, win_pct_item)
        
        # Configure table appearance
        header = teams_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Team name stretches
        
        # Set focus to first cell when table is created
        if teams_table.rowCount() > 0:
            teams_table.setCurrentCell(0, 0)
        
        # Connect table activation signal for team selection
        teams_table.itemActivated.connect(self.on_team_selected)
        
        layout.addWidget(teams_table)
        widget.setLayout(layout)
        
        # Store reference to table for focus management
        widget.teams_table = teams_table
        
        self.tab_widget.addTab(widget, division_name)
    
    def on_team_selected(self, item):
        """Handle team selection - open schedule view"""
        team_data = item.data(Qt.ItemDataRole.UserRole)
        if not team_data:
            return
            
        team_name = team_data.get('team_name', 'Unknown Team')
        
        # Open schedule dialog
        schedule_dialog = TeamScheduleDialog(team_data, self.league, self)
        schedule_dialog.exec()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        super().keyPressEvent(event)


class SportsScoresApp(QWidget):
    """Main application class using QStackedWidget for better view management"""
    
    def __init__(self, startup_params=None):
        super().__init__()
        self.setWindowTitle("Sports Scores")
        
        # Set proper window sizing behavior
        self.setMinimumSize(500, 300)  # Minimum usable size
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)  # Initial size
        
        # Enable proper window controls and resizing
        self.setWindowFlags(Qt.WindowType.Window | 
                           Qt.WindowType.WindowMinimizeButtonHint | 
                           Qt.WindowType.WindowMaximizeButtonHint | 
                           Qt.WindowType.WindowCloseButtonHint)
        
        # Allow the window to be resizable
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Application state
        self.config = {}
        self.view_stack = []  # Stack for navigation history
        self.startup_params = startup_params
        
        # Initialize configuration
        self._init_config()
        
        # Setup UI with stacked widget
        self.setup_ui()
        
        # Handle startup navigation
        self._handle_startup_navigation()
        self.show()
    
    def _init_config(self):
        try:
            leagues = ApiService.get_leagues()
            for league in leagues:
                # Start with a minimal default config (can be expanded later)
                self.config[league] = ["standings", "leaders", "boxscore", "injuries", "news"]
        except Exception as e:
            print(f"[WARNING] Failed to initialize config: {e}")

    def setup_ui(self):
        """Setup the main UI with QStackedWidget"""
        layout = QVBoxLayout()
        
        # Create stacked widget for view management
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        self.setLayout(layout)
    
    def show_home(self):
        """Show the home view"""
        try:
            home_view = HomeView(self)
            home_view.setup_ui()
            self._switch_to_view(home_view, "home", None)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show home view: {str(e)}")
    
    def show_live_scores(self):
        """Show the live scores view"""
        try:
            live_scores_view = LiveScoresView(self)
            self._switch_to_view(live_scores_view, "live_scores", None)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show live scores view: {str(e)}")
    
    def open_league(self, league: str):
        """Open a league view"""
        try:
            self._push_to_stack("home", None)
            league_view = LeagueView(self, league)
            self._switch_to_view(league_view, "league", league)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open league: {e}")

    def open_live_scores(self):
        """Open live scores view"""
        try:
            self._push_to_stack("home", None)
            live_scores_view = LiveScoresView(self)
            self._switch_to_view(live_scores_view, "live_scores", None)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open live scores: {e}")

    def open_game_details(self, game_id: str, from_live_scores=False):
        """Open game details view"""
        try:
            # Track where we came from for proper navigation
            if from_live_scores:
                self._push_to_stack("live_scores", None)
            else:
                self._push_to_stack("league", self.current_league if hasattr(self, 'current_league') else None)
            gdv = GameDetailsView(self, getattr(self, 'current_league', None), game_id)
            self._switch_to_view(gdv, "game", game_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open game details: {e}")
    
    def open_team_schedule(self, team_id: str, team_name: str, league: str):
        """Open team schedule view"""
        try:
            QMessageBox.information(self, "Team Schedule", 
                                  f"Schedule for {team_name} in {league} would be displayed here.\n"
                                  f"Team ID: {team_id}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open team schedule: {e}")

    def open_teams_directly(self, league: str):
        """Open teams view directly for a specific league"""
        try:
            # Set current league and navigate to teams
            self.current_league = league
            self._show_teams_dialog_directly(league)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open teams for {league}: {e}")

    def open_standings_directly(self, league: str):
        """Open standings view directly for a specific league"""
        try:
            # Set current league and navigate to standings  
            self.current_league = league
            self._show_standings_dialog_directly(league)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open standings for {league}: {e}")

    def _show_teams_dialog_directly(self, league: str):
        """Show teams dialog directly without being in a league view"""
        try:
            standings_data = ApiService.get_standings(league)
            if not standings_data:
                QMessageBox.information(self, "Teams", 
                                      f"No teams data available for {league}.")
                return
            
            # Filter data by league to avoid mixing
            filtered_data = [team for team in standings_data 
                           if self._is_team_for_league(team, league)]
            
            dialog = SimpleTeamsDialog(filtered_data, league, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show teams: {str(e)}")

    def _show_standings_dialog_directly(self, league: str):
        """Show standings dialog directly without being in a league view"""
        try:
            standings_data = ApiService.get_standings(league)
            if not standings_data:
                QMessageBox.information(self, "Standings", 
                                      f"No standings data available for {league}.")
                return
            
            dialog = StandingsDialog(standings_data, league, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show standings: {str(e)}")

    def _is_team_for_league(self, team_data: Dict, league: str) -> bool:
        """Check if team belongs to the specified league"""
        # This is a helper method that should already exist in LeagueView
        # We'll implement a simple version here
        try:
            # Look for league indicators in team data
            team_league = team_data.get('league', {}).get('abbreviation', '').upper()
            if team_league == league:
                return True
            
            # Fallback: check parent group info
            parent = team_data.get('parent', {})
            if parent:
                parent_name = parent.get('name', '').upper()
                return league in parent_name
            
            return True  # Default to include if we can't determine
        except:
            return True  # Default to include on error

    def _handle_startup_navigation(self):
        """Handle navigation based on startup parameters"""
        if not self.startup_params:
            # Default: show home view
            self.show_home()
            return
        
        action = self.startup_params.get('action')
        league = self.startup_params.get('league')
        
        if not action:
            self.show_home()
            return
        
        # For actions that don't require a league (like live_scores)
        if action not in ['live_scores'] and not league:
            self.show_home()
            return
        
        try:
            if action == 'live_scores':
                # Navigate directly to Live Scores view
                self.show_live_scores()
            elif action == 'league':
                # Navigate directly to league games view
                self.open_league(league)
            elif action == 'teams':
                # Show home first, then open teams dialog
                self.show_home()
                QTimer.singleShot(100, lambda: self.open_teams_directly(league))
            elif action == 'standings':
                # Show home first, then open standings dialog
                self.show_home()
                QTimer.singleShot(100, lambda: self.open_standings_directly(league))
            else:
                self.show_home()
        except Exception as e:
            QMessageBox.critical(self, "Startup Error", 
                               f"Failed to navigate to {action} for {league}: {str(e)}")
            self.show_home()

    def go_back(self):
        if not self.view_stack:
            return
        try:
            prev = self.view_stack.pop()
            vtype, data = prev.get('type'), prev.get('data')
            if vtype == "home":
                self.show_home(); return
            if vtype == "live_scores":
                self.show_live_scores(); return
            if vtype == "league" and data:
                self._show_league_view(data); return
            if vtype == "teams" and data:
                # Going back from team details -> league (simplified)
                self._show_league_view(data); return
            if vtype == "game" and data:
                # Going back from game details -> league
                if hasattr(self, 'current_league') and self.current_league:
                    self._show_league_view(self.current_league)
                else:
                    self.show_home()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to go back: {e}")

    def _show_league_view(self, data):
        """Helper method to show league view"""
        league_view = LeagueView(self, data)
        self._switch_to_view(league_view, "league", data)

    def _switch_to_view(self, view: BaseView, view_type: str, data: Any):
        # Clear existing widgets
        while self.stacked_widget.count():
            w = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(w)
            w.deleteLater()
        self.stacked_widget.addWidget(view)
        self.stacked_widget.setCurrentWidget(view)
        # Track current league
        if view_type == "league" and data:
            self.current_league = data
        if hasattr(view, 'on_show'):
            view.on_show()

    def _push_to_stack(self, view_type: str, data: Any):
        self.view_stack.append({"type": view_type, "data": data})

    def keyPressEvent(self, event):
        # Global back shortcut
        if event.modifiers() == Qt.KeyboardModifier.AltModifier and event.key() == Qt.Key.Key_B:
            self.go_back(); event.accept(); return
        # Escape key also goes back
        elif event.key() == Qt.Key.Key_Escape:
            self.go_back(); event.accept(); return
        super().keyPressEvent(event)

    def resizeEvent(self, event):
        """Handle window resize events to ensure proper content scaling"""
        super().resizeEvent(event)
        # Ensure the stacked widget takes full advantage of available space
        if hasattr(self, 'stacked_widget'):
            self.stacked_widget.resize(event.size())
            # Notify current view of resize if it has a resize handler
            current_widget = self.stacked_widget.currentWidget()
            if current_widget and hasattr(current_widget, 'handle_resize'):
                current_widget.handle_resize(event.size())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SportsScoresApp()
    sys.exit(app.exec())
