"""
Scores - Sports Analysis Application
A comprehensive sports analysis application supporting MLB and NFL
"""

# Import version from centralized location
try:
    from version import __version__, get_version
except ImportError:
    __version__ = "0.55.0"
    def get_version(): return __version__

__author__ = "Kelly Ford"
__description__ = "Sports Analysis Application with ESPN API integration"

import sys
import argparse
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
from services.venue_service import venue_service
from models.game import GameData
from models.news import NewsData
from models.standings import StandingsData
from accessible_table import AccessibleTable, StandingsTable, LeadersTable, BoxscoreTable, InjuryTable

# Text processing utilities
try:
    from text_utils import text_processor
except ImportError:
    text_processor = None
from timezone_utils import convert_espn_time_to_local
from windows_notifications import WindowsNotificationHelper

# Audio system for pitch mapping
try:
    from simple_audio_mapper import SimpleAudioPitchMapper as AudioPitchMapper
    from pitch_exploration_dialog import PitchExplorationDialog
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    AudioPitchMapper = None

# Football audio system for drive audio playback
try:
    from football_audio_mapper import FootballAudioMapper, FootballDrivePlayer
    from audio_player import AudioPlayer
    FOOTBALL_AUDIO_AVAILABLE = True
except ImportError:
    FOOTBALL_AUDIO_AVAILABLE = False
    FootballAudioMapper = None
    FootballDrivePlayer = None
    AudioPlayer = None

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
        
        # Add separator before Audio Tutorial
        separator_item2 = QListWidgetItem("─" * 30)
        separator_item2.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-selectable
        self.league_list.addItem(separator_item2)
        
        # Add Audio Tutorial section as last item
        audio_tutorial_item = QListWidgetItem("🎵 Audio Tutorial")
        audio_tutorial_item.setData(Qt.ItemDataRole.UserRole, "__audio_tutorial__")
        self.league_list.addItem(audio_tutorial_item)
        
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
            return
        elif user_data == "__audio_tutorial__":
            # Open Audio Tutorial view
            if self.parent_app:
                self.parent_app.open_audio_tutorial()
            return

        # For NFL/NCAAF, determine current week and show those games
        if league in ("NFL", "NCAAF"):
            try:
                from services.football_calendar import get_current_football_week
                today = datetime.now().date()
                week = get_current_football_week(league, today=today)
                if week is not None and self.parent_app:
                    self.parent_app.open_league(league, week=week)
                    return
            except Exception as e:
                print(f"Failed to get current week for {league}: {e}")
                # Fallback to default
        if self.parent_app:
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
        # Update window title for home view
        if self.parent_app:
            self.parent_app.update_window_title()
    
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
        self.current_date = datetime.now().date()  # Add date tracking
        
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
        
        # Setup auto-refresh timer for live updates (create before setup_ui)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_live_scores)
        
        self.setup_ui()
        
        # Start the timer after UI is set up
        self._update_refresh_timer()
    
    def setup_ui(self):
        # Header with current time
        self.time_label = QLabel()
        self.layout.addWidget(self.time_label)
        
        # Date navigation controls
        date_layout = QHBoxLayout()
        
        # Previous day button
        self.prev_day_btn = QPushButton("< Previous Day")
        self.prev_day_btn.clicked.connect(self._previous_day)
        self.prev_day_btn.setAccessibleName("Previous Day")
        self.prev_day_btn.setAccessibleDescription("Go to previous day")
        date_layout.addWidget(self.prev_day_btn)
        
        # Current date label  
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("font-weight: bold;")
        date_layout.addWidget(self.date_label)
        
        # Next day button
        self.next_day_btn = QPushButton("Next Day >")
        self.next_day_btn.clicked.connect(self._next_day)
        self.next_day_btn.setAccessibleName("Next Day")
        self.next_day_btn.setAccessibleDescription("Go to next day")
        date_layout.addWidget(self.next_day_btn)
        
        self.layout.addLayout(date_layout)
        
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
        
        # Instructions for manual refresh and navigation
        info_label = QLabel("Press 'F5' to refresh manually • Use ← → arrow keys, buttons, or Alt+P/Alt+N to navigate dates")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        self.layout.addWidget(info_label)
        
        self.live_scores_list = QListWidget()
        self.live_scores_list.setAccessibleName("Live Scores List")
        self.live_scores_list.setAccessibleDescription("List of currently live games from all sports. Press Alt+M to monitor a game for notifications.")
        self.live_scores_list.itemActivated.connect(self._on_game_selected)
        self.layout.addWidget(self.live_scores_list)
        
        self._add_nav_buttons()
        self._update_date_display()
        self.load_live_scores()
    
    def _update_date_display(self):
        """Update the date label and refresh controls based on current date"""
        from datetime import datetime
        
        today = datetime.now().date()
        date_str = self.current_date.strftime("%A, %B %d, %Y")
        
        if self.current_date == today:
            self.date_label.setText(f"Today - {date_str}")
            self.date_label.setStyleSheet("font-weight: bold; color: green;")
            # Enable auto-refresh for today
            self.refresh_combo.setEnabled(True)
            self._update_refresh_timer()
        else:
            self.date_label.setText(f"{date_str}")
            self.date_label.setStyleSheet("font-weight: bold; color: #666;")
            # Disable auto-refresh for other dates
            self.refresh_timer.stop()
            self.refresh_combo.setEnabled(False)
    
    def _previous_day(self):
        """Navigate to previous day"""
        from datetime import timedelta
        self.current_date -= timedelta(days=1)
        self._update_date_display()
        self.load_live_scores()
    
    def _next_day(self):
        """Navigate to next day"""
        from datetime import timedelta
        self.current_date += timedelta(days=1)
        self._update_date_display()
        self.load_live_scores()

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.modifiers() == Qt.KeyboardModifier.AltModifier and event.key() == Qt.Key.Key_M:
            self._toggle_monitoring()
        elif event.modifiers() == Qt.KeyboardModifier.AltModifier and event.key() == Qt.Key.Key_P:
            # Navigate to previous day (Alt+P)
            self._previous_day()
        elif event.modifiers() == Qt.KeyboardModifier.AltModifier and event.key() == Qt.Key.Key_N:
            # Navigate to next day (Alt+N)
            self._next_day()
        elif event.key() == Qt.Key.Key_F5:
            # Provide feedback for manual refresh
            if hasattr(self, 'refresh_combo') and self.refresh_combo.currentText() == "Manual (F5 only)":
                self.notification_helper.announce("Refreshing live scores manually")
            self.refresh_live_scores()
        elif event.key() == Qt.Key.Key_Left:
            # Navigate to previous day
            self._previous_day()
        elif event.key() == Qt.Key.Key_Right:
            # Navigate to next day
            self._next_day()
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
        """Update the refresh timer based on current interval and date"""
        from datetime import datetime
        
        self.refresh_timer.stop()
        
        # Only enable auto-refresh if viewing today's date
        today = datetime.now().date()
        if self.current_date == today and self.current_refresh_interval > 0:
            self.refresh_timer.start(self.current_refresh_interval)
        # If interval is 0 (manual mode) or not viewing today, timer stays stopped
    
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
        """Load and display live, upcoming, and completed games from all sports."""
        from datetime import datetime
        
        self.live_scores_list.clear()
        self.game_data.clear()
        self._update_time_label()
        
        try:
            today = datetime.now().date()
            is_today = (self.current_date == today)
            
            # Get live games only if viewing today
            live_games = []
            if is_today:
                live_games = ApiService.get_live_scores_all_sports()
            
            # Get all games for the current date to find upcoming and completed ones
            current_date_games = self._get_today_games_all_sports()
            
            # Categorize games
            live_games_dict = {game.get('id', ''): game for game in live_games}
            upcoming_games = []
            completed_games = []
            
            for game in current_date_games:
                game_id = game.get('game_id', '')
                if game_id not in live_games_dict:
                    # Check if game is upcoming or completed
                    state = game.get('state', '')
                    if state == 'upcoming':
                        upcoming_games.append(game)
                    elif state == 'completed':
                        completed_games.append(game)
            
            # Sort upcoming games by start time (closest first)
            upcoming_games.sort(key=lambda g: g.get('start_time', ''))
            
            total_games = len(live_games) + len(upcoming_games) + len(completed_games)
            
            if total_games == 0:
                date_desc = "today" if is_today else self.current_date.strftime("%B %d, %Y")
                self.live_scores_list.addItem(f"No games on {date_desc}.")
                return
            
            # Section 1: Live Games (only show if viewing today)
            if live_games and is_today:
                section_header = QListWidgetItem("=== LIVE GAMES ===")
                section_header.setBackground(QColor(200, 255, 200))  # Light green background
                self.live_scores_list.addItem(section_header)
                
                # Group live games by league for better organization
                games_by_league = {}
                for game in live_games:
                    league = game.get("league", "Unknown")
                    if league not in games_by_league:
                        games_by_league[league] = []
                    games_by_league[league].append(game)
                
                for league in sorted(games_by_league.keys()):
                    # Add league header
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
                        
                        # Build display text (keeping existing live game formatting)
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
                                # Enhanced baseball display with base runners, count, and batter info
                                display_text = self._format_enhanced_baseball(game_name, teams, status, recent_play, game_id)
                            else:
                                display_text += f" | {recent_play[:50]}"  # Truncate long plays for other sports
                        else:
                            # Standard format for games without enhanced play info
                            if status:
                                display_text += f" ({status})"
                        
                        item = QListWidgetItem(display_text)
                        item.setData(Qt.ItemDataRole.UserRole, game)  # Store full game data
                        self.live_scores_list.addItem(item)
                        
                        # Store game data for monitoring
                        if game_id:
                            self.game_data[game_id] = game
                
                # Add spacing after live games
                self.live_scores_list.addItem("")
            
            # Section 2: Upcoming Games
            if upcoming_games:
                section_header = QListWidgetItem("=== UPCOMING GAMES ===")
                section_header.setBackground(QColor(255, 255, 200))  # Light yellow background
                self.live_scores_list.addItem(section_header)
                
                # Group upcoming games by league
                upcoming_by_league = {}
                for game in upcoming_games:
                    league = game.get('league', 'Unknown')
                    if league not in upcoming_by_league:
                        upcoming_by_league[league] = []
                    upcoming_by_league[league].append(game)
                
                for league in sorted(upcoming_by_league.keys()):
                    # Add league header
                    league_item = QListWidgetItem(f"--- {league} ---")
                    league_item.setBackground(QColor(240, 240, 240))
                    self.live_scores_list.addItem(league_item)
                    
                    for game in upcoming_by_league[league]:
                        display_text = self._format_game_display(game)
                        item = QListWidgetItem(display_text)
                        # Prepare game data in format expected by _on_game_selected
                        game_data = game.get('raw_data', game)
                        if 'game_id' in game and 'id' not in game_data:
                            # Add id field if missing
                            game_data = dict(game_data) if isinstance(game_data, dict) else {}
                            game_data['id'] = game.get('game_id')
                            game_data['league'] = game.get('league')
                        item.setData(Qt.ItemDataRole.UserRole, game_data)
                        self.live_scores_list.addItem(item)
                
                # Add spacing after upcoming games
                self.live_scores_list.addItem("")
            
            # Section 3: Completed Games
            if completed_games:
                section_header = QListWidgetItem("=== COMPLETED GAMES ===")
                section_header.setBackground(QColor(220, 220, 220))  # Light gray background
                self.live_scores_list.addItem(section_header)
                
                # Group completed games by league
                completed_by_league = {}
                for game in completed_games:
                    league = game.get('league', 'Unknown')
                    if league not in completed_by_league:
                        completed_by_league[league] = []
                    completed_by_league[league].append(game)
                
                for league in sorted(completed_by_league.keys()):
                    # Add league header
                    league_item = QListWidgetItem(f"--- {league} ---")
                    league_item.setBackground(QColor(240, 240, 240))
                    self.live_scores_list.addItem(league_item)
                    
                    for game in completed_by_league[league]:
                        display_text = self._format_game_display(game)
                        item = QListWidgetItem(display_text)
                        # Prepare game data in format expected by _on_game_selected
                        game_data = game.get('raw_data', game)
                        if 'game_id' in game and 'id' not in game_data:
                            # Add id field if missing
                            game_data = dict(game_data) if isinstance(game_data, dict) else {}
                            game_data['id'] = game.get('game_id')
                            game_data['league'] = game.get('league')
                        item.setData(Qt.ItemDataRole.UserRole, game_data)
                        self.live_scores_list.addItem(item)
                
        except Exception as e:
            self._show_api_error(f"Failed to load live scores: {str(e)}")
    
    def refresh_live_scores(self):
        """Refresh live scores and check for changes in monitored games"""
        from datetime import datetime
        
        # Only allow refresh if viewing today's date
        today = datetime.now().date()
        if self.current_date != today:
            # For non-today dates, just reload the static data
            self.load_live_scores()
            return
        
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
    
    def _get_today_games_all_sports(self):
        """Get all games for the current date from all sports"""
        from models.game import GameData
        
        all_games = []
        
        # List of supported leagues  
        leagues = ["NFL", "NBA", "MLB", "NHL", "NCAAF", "NCAAM", "WNBA", "NCAAWB"]
        
        for league in leagues:
            try:
                # Get scores for current date for this league
                scores_data = ApiService.get_scores(league, self.current_date)
                for game_raw in scores_data:
                    # Create GameData object for consistent formatting
                    game = GameData(game_raw, league)
                    # Convert to format expected by live scores view
                    game_dict = {
                        'game_id': game_raw.get('id', ''),
                        'league': league,
                        'name': game.name,
                        'teams': game.teams,
                        'status': game.status,
                        'start_time': game.start_time,
                        'display_text': game.get_display_text(),
                        'raw_data': game_raw,
                        'game_data': game  # Keep reference to GameData object
                    }
                    
                    # Determine game state for categorization
                    status_lower = game.status.lower() if game.status else ''
                    if status_lower in ['in progress', 'live']:
                        game_dict['state'] = 'live'
                    elif status_lower in ['final', 'completed']:
                        game_dict['state'] = 'completed'
                    elif status_lower in ['scheduled', 'upcoming']:
                        game_dict['state'] = 'upcoming'
                    else:
                        # Try to determine from raw data
                        raw_status = game_raw.get('status', {})
                        if isinstance(raw_status, dict):
                            type_info = raw_status.get('type', {})
                            state = type_info.get('state', '').lower()
                            if state == 'in':
                                game_dict['state'] = 'live'
                            elif state == 'post':
                                game_dict['state'] = 'completed'
                            elif state == 'pre':
                                game_dict['state'] = 'upcoming'
                            else:
                                game_dict['state'] = 'unknown'
                        else:
                            game_dict['state'] = 'unknown'
                    
                    all_games.append(game_dict)
            except Exception as e:
                print(f"Error fetching {league} games: {e}")
                continue
        
        return all_games

    def _format_game_display(self, game):
        """Format a game for display in the list using GameData if available"""
        try:
            # Use the pre-formatted display text if available
            if 'display_text' in game and game['display_text']:
                return game['display_text']
            
            # Use GameData object if available
            if 'game_data' in game and game['game_data']:
                return game['game_data'].get_display_text()
            
            # Fallback to manual formatting
            home_team = game.get('home_team', {})
            away_team = game.get('away_team', {})
            home_score = game.get('home_score', '')
            away_score = game.get('away_score', '')
            status = game.get('status', '')
            clock = game.get('clock', '')
            period = game.get('period', '')
            
            # Build team display
            home_name = home_team.get('name', home_team.get('abbreviation', 'TBD'))
            away_name = away_team.get('name', away_team.get('abbreviation', 'TBD'))
            
            # Format scores if available
            if home_score and away_score:
                team_display = f"{away_name} {away_score} vs {home_name} {home_score}"
            else:
                team_display = f"{away_name} vs {home_name}"
            
            # Add status/timing info
            if status and clock:
                if period:
                    status_display = f"[{period} - {clock}]"
                else:
                    status_display = f"[{status} - {clock}]"
            elif status:
                status_display = f"[{status}]"
            else:
                status_display = ""
            
            return f"{team_display} {status_display}".strip()
        except Exception as e:
            print(f"Error formatting game display: {e}")
            return str(game)
    
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
        # Update window title for live scores view
        if self.parent_app:
            self.parent_app.update_window_title(["Live Scores"])
    
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

    def _format_enhanced_baseball(self, game_name, teams, status, recent_play, game_id):
        """Format enhanced baseball display with base runners, count, and batter info"""
        try:
            # The recent_play contains the enhanced format with newline separation
            # Line 1: Team names with scores
            # Line 2: Base situation | Count | At bat: Player
            # Line 3: Last: Play description
            lines = recent_play.split('\n')
            
            if len(lines) >= 3:
                # Three-line format: use all lines
                team_line = lines[0]
                situation_line = lines[1]
                last_play_line = lines[2]
                
                # Add status if available (inning info)
                if status and status not in situation_line:
                    team_line += f" ({status})"
                
                display_text = f"{team_line}\n{situation_line}\n{last_play_line}"
            elif len(lines) >= 2:
                # Two-line fallback
                team_line = lines[0]
                situation_line = lines[1]
                
                if status:
                    team_line += f" ({status})"
                
                display_text = f"{team_line}\n{situation_line}"
            else:
                # Single line fallback
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

class AudioTutorialView(BaseView):
    """View showing audio tutorial with sample plays for baseball and football"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        self.layout.addWidget(QLabel("🎵 Audio Tutorial"))
        
        # Add description
        description = QLabel(
            "Learn how the audio system works with sample plays from baseball and football.\n"
            "Each sport uses audio to represent different aspects of the game:\n\n"
            "⚾ Baseball: Pitch types, locations, and strike zone positioning\n"
            "🏈 Football: Play types, yardage, and field position (left to right stereo)"
        )
        description.setWordWrap(True)
        description.setStyleSheet("margin: 10px 0; color: #666;")
        self.layout.addWidget(description)
        
        # Create tutorial selection list
        self.tutorial_list = QListWidget()
        self.tutorial_list.setAccessibleName("Audio Tutorial Selection")
        self.tutorial_list.setAccessibleDescription("Select a sport to learn about its audio features")
        
        # Add baseball tutorial
        baseball_item = QListWidgetItem("⚾ Baseball Audio Tutorial")
        baseball_item.setData(Qt.ItemDataRole.UserRole, "baseball")
        self.tutorial_list.addItem(baseball_item)
        
        # Add football tutorial
        football_item = QListWidgetItem("🏈 Football Audio Tutorial")
        football_item.setData(Qt.ItemDataRole.UserRole, "football")
        self.tutorial_list.addItem(football_item)
        
        self.tutorial_list.itemActivated.connect(self._on_tutorial_selected)
        self.layout.addWidget(self.tutorial_list)
        
        # Add back button
        back_btn = QPushButton("Back to Main Menu (Escape)")
        back_btn.clicked.connect(lambda: self.parent_app.go_back() if self.parent_app else None)
        self.layout.addWidget(back_btn)
    
    def _on_tutorial_selected(self, item):
        """Handle tutorial selection"""
        tutorial_type = item.data(Qt.ItemDataRole.UserRole)
        
        if tutorial_type == "baseball":
            if self.parent_app:
                self.parent_app.open_baseball_audio_tutorial()
        elif tutorial_type == "football":
            if self.parent_app:
                self.parent_app.open_football_audio_tutorial()

class BaseballAudioTutorialView(BaseView):
    """Baseball audio tutorial with sample pitches and explanations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        self.layout.addWidget(QLabel("⚾ Baseball Audio Tutorial"))
        
        # Add description
        description = QLabel(
            "Baseball audio maps pitch characteristics to sound:\n\n"
            "🎯 Pitch Location: Stereo positioning represents strike zone location\n"
            "🎵 Pitch Type: Different wave forms (fastball=square, curve=sine, etc.)\n"
            "📏 Velocity: Higher velocity = higher pitch frequency\n"
            "⚾ Outcome: Strikes, balls, hits have distinct audio signatures"
        )
        description.setWordWrap(True)
        description.setStyleSheet("margin: 10px 0; color: #666;")
        self.layout.addWidget(description)
        
        # Create sample pitches list
        if AUDIO_AVAILABLE:
            self.pitches_list = QListWidget()
            self.pitches_list.setAccessibleName("Sample Baseball Pitches")
            self.pitches_list.setAccessibleDescription("Sample pitches demonstrating different audio characteristics. Press Enter to play.")
            
            # Add sample pitches
            samples = [
                ("Strike - Fastball Center", "95 mph fastball down the middle", "fastball", "center", "strike"),
                ("Ball - Curveball Low", "78 mph curveball below the zone", "curveball", "low", "ball"),
                ("Hit - Slider Outside", "84 mph slider hit for single", "slider", "outside", "hit"),
                ("Strike - Changeup Corner", "82 mph changeup on the corner", "changeup", "corner", "strike"),
                ("Ball - Fastball High", "97 mph fastball above the zone", "fastball", "high", "ball")
            ]
            
            for title, description, pitch_type, location, outcome in samples:
                item = QListWidgetItem(f"{title}\n   {description}")
                item.setData(Qt.ItemDataRole.UserRole, {
                    'pitch_type': pitch_type,
                    'location': location,
                    'outcome': outcome,
                    'description': description
                })
                self.pitches_list.addItem(item)
            
            self.pitches_list.itemActivated.connect(self._play_sample_pitch)
            self.layout.addWidget(self.pitches_list)
            
            # Add instructions
            instructions = QLabel("💡 Press Enter on any pitch to hear its audio representation")
            instructions.setStyleSheet("color: #0066cc; font-style: italic; margin: 10px 0;")
            self.layout.addWidget(instructions)
        else:
            no_audio_label = QLabel("❌ Audio system not available")
            no_audio_label.setStyleSheet("color: #cc0000; font-weight: bold;")
            self.layout.addWidget(no_audio_label)
        
        # Add back button
        back_btn = QPushButton("Back to Audio Tutorial (Escape)")
        back_btn.clicked.connect(lambda: self.parent_app.go_back() if self.parent_app else None)
        self.layout.addWidget(back_btn)
    
    def _play_sample_pitch(self, item):
        """Play audio for a sample pitch"""
        if not AUDIO_AVAILABLE:
            return
            
        pitch_data = item.data(Qt.ItemDataRole.UserRole)
        print(f"Playing sample pitch: {pitch_data['description']}")
        
        # Create a simple pitch audio demonstration
        # (This would integrate with the existing pitch audio system)
        try:
            # For now, just provide feedback
            title = self.parent().windowTitle() if self.parent() else "Tutorial"
            if hasattr(self.parent(), 'setWindowTitle'):
                original_title = self.parent().windowTitle()
                self.parent().setWindowTitle(f"[Audio] {pitch_data['description']}")
                QTimer.singleShot(2000, lambda: self.parent().setWindowTitle(original_title))
            
            print(f"Pitch audio demo: {pitch_data['pitch_type']} at {pitch_data['location']} ({pitch_data['outcome']})")
        except Exception as e:
            print(f"Sample pitch audio error: {e}")

class FootballAudioTutorialView(BaseView):
    """Football audio tutorial with sample drives and explanations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        self.layout.addWidget(QLabel("🏈 Football Audio Tutorial"))
        
        # Add description
        description = QLabel(
            "Football audio maps drive progression to sound:\n\n"
            "📍 Field Position: Left speaker = own endzone, Right speaker = opponent endzone\n"
            "🎵 Play Type: Rush=square wave, Pass=sine wave, Scoring=sawtooth\n"
            "📏 Yardage: Bigger gains = higher pitch frequencies\n"
            "🏈 Drive Flow: Audio pans left-to-right as team moves down field"
        )
        description.setWordWrap(True)
        description.setStyleSheet("margin: 10px 0; color: #666;")
        self.layout.addWidget(description)
        
        # Create sample drives list
        if FOOTBALL_AUDIO_AVAILABLE:
            self.drives_list = QListWidget()
            self.drives_list.setAccessibleName("Sample Football Drives")
            self.drives_list.setAccessibleDescription("Sample drives demonstrating different audio characteristics. Press Enter to play.")
            
            # Add sample drives
            samples = [
                ("Touchdown Drive", "7 plays, 75 yards - demonstrates field progression", "touchdown"),
                ("Short Drive - Field Goal", "4 plays, 18 yards ending in field goal", "field_goal"),
                ("Failed Drive - Punt", "3 plays, 8 yards ending in punt", "punt"),
                ("Big Play Drive", "2 plays, 65 yards with long pass", "big_play"),
                ("Turnover Drive", "5 plays ending in interception", "turnover")
            ]
            
            for title, description, drive_type in samples:
                item = QListWidgetItem(f"{title}\n   {description}")
                item.setData(Qt.ItemDataRole.UserRole, {
                    'drive_type': drive_type,
                    'description': description
                })
                self.drives_list.addItem(item)
            
            self.drives_list.itemActivated.connect(self._play_sample_drive)
            self.layout.addWidget(self.drives_list)
            
            # Add instructions
            instructions = QLabel("💡 Press Enter on any drive to hear its audio representation")
            instructions.setStyleSheet("color: #0066cc; font-style: italic; margin: 10px 0;")
            self.layout.addWidget(instructions)
        else:
            no_audio_label = QLabel("❌ Football audio system not available")
            no_audio_label.setStyleSheet("color: #cc0000; font-weight: bold;")
            self.layout.addWidget(no_audio_label)
        
        # Add back button
        back_btn = QPushButton("Back to Audio Tutorial (Escape)")
        back_btn.clicked.connect(lambda: self.parent_app.go_back() if self.parent_app else None)
        self.layout.addWidget(back_btn)
    
    def _play_sample_drive(self, item):
        """Play audio for a sample drive"""
        if not FOOTBALL_AUDIO_AVAILABLE:
            return
            
        drive_data = item.data(Qt.ItemDataRole.UserRole)
        print(f"Playing sample drive: {drive_data['description']}")
        
        # Create sample drive audio using the actual football audio system
        try:
            # Create sample drive data based on drive type
            sample_drive = self._create_sample_drive(drive_data['drive_type'])
            
            # Use the actual football audio mapper
            from football_audio_mapper import FootballAudioMapper
            from audio_player import AudioPlayer
            
            mapper = FootballAudioMapper()
            player = AudioPlayer()
            
            # Generate and play the audio
            audio_sequence = mapper.map_drive_to_audio_sequence(sample_drive)
            if audio_sequence:
                # Extract field positions
                field_positions = [config.field_position for config in audio_sequence if config.field_position is not None]
                if len(field_positions) == len(audio_sequence):
                    field_positions_param = field_positions
                else:
                    field_positions_param = None
                
                # Provide user feedback
                if hasattr(self.parent(), 'setWindowTitle'):
                    original_title = self.parent().windowTitle()
                    self.parent().setWindowTitle(f"[Audio] {drive_data['description']}")
                    QTimer.singleShot(3000, lambda: self.parent().setWindowTitle(original_title))
                
                # Play the audio
                player.play_audio_sequence(audio_sequence, silence_between=0.1, field_positions=field_positions_param)
                print(f"Sample drive audio complete: {len(audio_sequence)} plays")
        except Exception as e:
            print(f"Sample drive audio error: {e}")
    
    def _create_sample_drive(self, drive_type):
        """Create sample drive data for demonstration"""
        if drive_type == "touchdown":
            return {
                "team": {"displayName": "Tutorial Team"},
                "description": "7 plays, 75 yards, TOUCHDOWN",
                "plays": [
                    {"text": "QB pass short right for 12 yards", "statYardage": 12, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 75}},
                    {"text": "RB rush up middle for 5 yards", "statYardage": 5, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 63}},
                    {"text": "QB pass deep left for 25 yards", "statYardage": 25, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 58}},
                    {"text": "RB rush right end for 8 yards", "statYardage": 8, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 33}},
                    {"text": "QB pass short middle for 7 yards", "statYardage": 7, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 25}},
                    {"text": "RB rush left tackle for 3 yards", "statYardage": 3, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 18}},
                    {"text": "QB pass right corner for 15 yards TOUCHDOWN", "statYardage": 15, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 15}, "scoringPlay": True}
                ]
            }
        elif drive_type == "field_goal":
            return {
                "team": {"displayName": "Tutorial Team"},
                "description": "4 plays, 18 yards, FIELD GOAL",
                "plays": [
                    {"text": "RB rush up middle for 4 yards", "statYardage": 4, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 35}},
                    {"text": "QB pass short right for 8 yards", "statYardage": 8, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 31}},
                    {"text": "RB rush left end for 6 yards", "statYardage": 6, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 23}},
                    {"text": "25-yard field goal GOOD", "statYardage": 0, "type": {"text": "Field Goal Good"}, "start": {"yardsToEndzone": 17}, "scoringPlay": True}
                ]
            }
        elif drive_type == "big_play":
            return {
                "team": {"displayName": "Tutorial Team"},
                "description": "2 plays, 65 yards, TOUCHDOWN",
                "plays": [
                    {"text": "QB pass deep middle for 45 yards", "statYardage": 45, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 65}},
                    {"text": "RB rush right end for 20 yards TOUCHDOWN", "statYardage": 20, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 20}, "scoringPlay": True}
                ]
            }
        else:
            # Default short drive
            return {
                "team": {"displayName": "Tutorial Team"},
                "description": "3 plays, 8 yards, PUNT",
                "plays": [
                    {"text": "RB rush up middle for 3 yards", "statYardage": 3, "type": {"text": "Rush"}, "start": {"yardsToEndzone": 75}},
                    {"text": "QB pass incomplete", "statYardage": 0, "type": {"text": "Pass Incompletion"}, "start": {"yardsToEndzone": 72}},
                    {"text": "QB pass short right for 5 yards", "statYardage": 5, "type": {"text": "Pass Reception"}, "start": {"yardsToEndzone": 72}}
                ]
            }

class LeagueView(BaseView):
    """View showing scores for a specific league"""
    
    def __init__(self, parent=None, league=None, week=None):
        super().__init__(parent)
        self.league = league
        self.news_headlines = []
        
        # For football leagues, ensure we have a week
        if self.is_football_league():
            if week is not None:
                self.current_week = week
            else:
                # Auto-determine current week for football
                try:
                    from services.football_calendar import get_current_football_week
                    self.current_week = get_current_football_week(league)
                except Exception:
                    self.current_week = 1  # Default to week 1
            self.current_date = None
        else:
            self.current_week = None
            self.current_date = datetime.now().date()
        
        self.setup_ui()

    def is_football_league(self):
        return self.league in ["NFL", "NCAAF"]
    
    def setup_ui(self):
        # Navigation label (date or week)
        self.date_label = QLabel()
        self.layout.addWidget(self.date_label)

        self.layout.addWidget(QLabel(f"Scores for {self.league}:"))

        self.scores_list = QListWidget()
        self.scores_list.setAccessibleName("Scores List")
        self.scores_list.setAccessibleDescription("List of games and scores for the selected date or week")
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
        if data == "__statistics__":
            self._show_statistics_dialog(); return
        if data == "__teams__":
            self._show_teams_dialog(); return
        if data == "__venues__":
            self._show_venues_dialog(); return
        if data and isinstance(data, str) and self.parent_app:
            self.parent_app.open_game_details(data)

    def load_scores(self):
        """Load scores for the current date or week"""
        self.scores_list.clear()
        if self.is_football_league() and self.current_week is not None:
            self.date_label.setText(f"Week: {self.current_week}")
            try:
                scores_data = ApiService.get_scores(self.league, week=self.current_week)
                self.news_headlines = ApiService.get_news(self.league)
                if not scores_data:
                    self.scores_list.addItem("No games found for this week.")
                else:
                    for game_raw in scores_data:
                        game = GameData(game_raw, self.league)
                        item_text = game.get_display_text()
                        self.scores_list.addItem(item_text)
                        list_item = self.scores_list.item(self.scores_list.count()-1)
                        if list_item:
                            list_item.setData(Qt.ItemDataRole.UserRole, game_raw.get("id"))
                if self.news_headlines:
                    self.scores_list.addItem("--- News Headlines ---")
                    news_item = self.scores_list.item(self.scores_list.count()-1)
                    news_item.setData(Qt.ItemDataRole.UserRole, "__news__")
                self._add_common_sections()
            except Exception as e:
                self._show_api_error(f"Failed to load scores: {str(e)}")
        else:
            date_str = self.current_date.strftime("%A, %B %d, %Y")
            self.date_label.setText(f"Date: {date_str}")
            try:
                scores_data = ApiService.get_scores(self.league, self.current_date)
                self.news_headlines = ApiService.get_news(self.league)
                if not scores_data:
                    self.scores_list.addItem("No games found for this date.")
                else:
                    for game_raw in scores_data:
                        game = GameData(game_raw, self.league)
                        item_text = game.get_display_text()
                        self.scores_list.addItem(item_text)
                        list_item = self.scores_list.item(self.scores_list.count()-1)
                        if list_item:
                            list_item.setData(Qt.ItemDataRole.UserRole, game_raw.get("id"))
                if self.news_headlines:
                    self.scores_list.addItem("--- News Headlines ---")
                    news_item = self.scores_list.item(self.scores_list.count()-1)
                    news_item.setData(Qt.ItemDataRole.UserRole, "__news__")
                self._add_common_sections()
            except Exception as e:
                self._show_api_error(f"Failed to load scores: {str(e)}")

    def _add_common_sections(self):
        if self.league in ["MLB", "NFL", "NBA", "WNBA", "NHL", "NCAAF", "NCAAM", "NCAAWB"]:
            self.scores_list.addItem("--- Standings ---")
            standings_item = self.scores_list.item(self.scores_list.count()-1)
            standings_item.setData(Qt.ItemDataRole.UserRole, "__standings__")
            self.scores_list.addItem("--- Statistics ---")
            statistics_item = self.scores_list.item(self.scores_list.count()-1)
            statistics_item.setData(Qt.ItemDataRole.UserRole, "__statistics__")
            self.scores_list.addItem("--- Teams ---")
            teams_item = self.scores_list.item(self.scores_list.count()-1)
            teams_item.setData(Qt.ItemDataRole.UserRole, "__teams__")
            self.scores_list.addItem("--- Venues ---")
            venues_item = self.scores_list.item(self.scores_list.count()-1)
            venues_item.setData(Qt.ItemDataRole.UserRole, "__venues__")

    def _show_news_dialog(self):
        """Show news dialog"""
        try:
            # Update window title to show we're viewing news
            if self.parent_app:
                self.parent_app.update_window_title(["News", self.league])
            
            dialog = NewsDialog(self.news_headlines, self.league, self)
            dialog.exec()
            
            # Restore original title when dialog closes
            if self.parent_app:
                self.parent_app.update_window_title([self.league])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show news: {str(e)}")
            # Restore original title on error
            if self.parent_app:
                self.parent_app.update_window_title([self.league])
    
    def _show_standings_dialog(self):
        """Show standings dialog with caching and fast background loading"""
        try:
            # Update window title to show we're viewing standings
            if self.parent_app:
                self.parent_app.update_window_title(["Standings", self.league])
            
            # Check cache first
            cache = DataCache()
            cached_data = cache.get_standings(self.league)
            
            if cached_data:
                # Use cached data immediately
                dialog = StandingsDialog(cached_data, self.league, self)
                dialog.exec()
                # Restore original title when dialog closes
                if self.parent_app:
                    self.parent_app.update_window_title([self.league])
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
            # Restore original title when dialog closes
            if self.parent_app:
                self.parent_app.update_window_title([self.league])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display standings: {str(e)}")
    
    def _show_statistics_dialog(self):
        """Show statistics dialog with new flow: choose team/player → select stat → view results"""
        try:
            print(f"DEBUG: Starting _show_statistics_dialog for league: {self.league}")
            
            # Update window title to show we're viewing statistics
            if self.parent_app:
                self.parent_app.update_window_title(["Statistics", self.league])
            
            # Loop to allow returning to choice dialog
            while True:
                # First dialog: Choose between Team or Player statistics
                choice_dialog = StatisticsChoiceDialog(self.league, self)
                print(f"DEBUG: Created StatisticsChoiceDialog")
                
                if choice_dialog.exec() == QDialog.DialogCode.Accepted:
                    print(f"DEBUG: StatisticsChoiceDialog accepted")
                    choice = choice_dialog.get_choice()
                    print(f"DEBUG: Got choice: {choice}")
                    
                    if choice:
                        # Second dialog: Select specific statistic and view results
                        print(f"DEBUG: Creating StatisticsViewDialog with league={self.league}, choice={choice}")
                        stats_dialog = StatisticsViewDialog(self.league, choice, self)
                        print(f"DEBUG: About to show StatisticsViewDialog")
                        result = stats_dialog.exec()
                        print(f"DEBUG: StatisticsViewDialog returned with result: {result}")
                        
                        # If the user clicked OK or closed normally, exit the loop
                        # If they pressed Escape (result == 0), continue the loop to show choice again
                        if result == QDialog.DialogCode.Accepted:
                            break  # Exit statistics completely
                        # If result == QDialog.DialogCode.Rejected (Escape), loop continues
                    else:
                        print(f"DEBUG: No choice received from StatisticsChoiceDialog")
                        break  # Exit if no choice
                else:
                    print(f"DEBUG: StatisticsChoiceDialog was not accepted")
                    break  # Exit if choice dialog was cancelled
            
            # Restore original title when dialog closes
            if self.parent_app:
                self.parent_app.update_window_title([self.league])
                    
        except Exception as e:
            print(f"DEBUG: Exception in _show_statistics_dialog: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to display statistics: {str(e)}")
            # Restore original title on error
            if self.parent_app:
                self.parent_app.update_window_title([self.league])
    
    def _on_standings_data_error(self, error_message):
        """Handle standings data loading error"""
        QMessageBox.warning(self, "Standings", error_message)
    
    def _show_teams_dialog(self):
        """Show teams dialog with simple tabbed interface"""
        try:
            # Update window title to show we're viewing teams
            if self.parent_app:
                self.parent_app.update_window_title(["Teams", self.league])
            
            standings_data = ApiService.get_standings(self.league)
            if not standings_data:
                QMessageBox.information(self, "Teams", 
                                      f"No teams data available for {self.league}.")
                # Restore original title
                if self.parent_app:
                    self.parent_app.update_window_title([self.league])
                return
            
            # Filter data by league to avoid MLB/NFL mixing
            filtered_data = [team for team in standings_data 
                           if self._is_team_for_league(team, self.league)]
            
            dialog = SimpleTeamsDialog(filtered_data, self.league, self)
            dialog.exec()
            
            # Restore original title when dialog closes
            if self.parent_app:
                self.parent_app.update_window_title([self.league])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show teams: {str(e)}")
            # Restore original title on error
            if self.parent_app:
                self.parent_app.update_window_title([self.league])
    
    def _show_venues_dialog(self):
        """Show venues dialog for the current league"""
        try:
            # Update window title to show we're viewing venues
            if self.parent_app:
                self.parent_app.update_window_title(["Venues", self.league])
            
            # Convert league to lowercase for venue service
            league_key = self.league.lower()
            venues_data = venue_service.get_venues_for_league(league_key)
            if not venues_data:
                QMessageBox.information(self, "Venues", 
                                      f"No venue data available for {self.league}.")
                # Restore original title
                if self.parent_app:
                    self.parent_app.update_window_title([self.league])
                return
            
            dialog = VenuesDialog(venues_data, self.league, self)
            dialog.exec()
            
            # Restore original title when dialog closes
            if self.parent_app:
                self.parent_app.update_window_title([self.league])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show venues: {str(e)}")
            # Restore original title on error
            if self.parent_app:
                self.parent_app.update_window_title([self.league])
    
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

        if self.is_football_league():
            prev_week_btn = QPushButton("Previous Week (Alt+P)")
            prev_week_btn.setShortcut("Alt+P")
            prev_week_btn.clicked.connect(self.previous_week)
            btn_layout.addWidget(prev_week_btn)

            next_week_btn = QPushButton("Next Week (Alt+N)")
            next_week_btn.setShortcut("Alt+N")
            next_week_btn.clicked.connect(self.next_week)
            btn_layout.addWidget(next_week_btn)

        else:
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

    def previous_week(self):
        if self.current_week and self.current_week > 1:
            self.current_week -= 1
            self.load_scores()
            self.set_focus_and_select_first(self.scores_list)

    def next_week(self):
        if self.current_week:
            self.current_week += 1
            self.load_scores()
            self.set_focus_and_select_first(self.scores_list)
    
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
        # Update window title for league view
        if self.parent_app and self.league:
            self.parent_app.update_window_title([self.league])

class GameDetailsView(BaseView):
    """View showing detailed information for a specific game"""
    
    def __init__(self, parent=None, league=None, game_id=None, original_game_data=None):
        super().__init__(parent)
        self.league = league
        self.game_id = game_id
        self.original_game_data = original_game_data  # Store original game data with team IDs
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
        
        # Initialize football audio system for football leagues
        self.football_audio_mapper = None
        self.football_audio_player = None
        if FOOTBALL_AUDIO_AVAILABLE and league in ["NFL", "NCAAF"]:
            try:
                self.football_audio_mapper = FootballAudioMapper()
                self.football_audio_player = AudioPlayer()
                print(f"Debug: Football audio system initialized for {league}")
            except Exception as e:
                print(f"Debug: Failed to initialize football audio: {e}")
                self.football_audio_mapper = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Set focus policy to allow keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
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
    
    def keyPressEvent(self, event):
        """Handle key press events for game details view"""
        print(f"Debug: GameDetailsView keyPressEvent - key: {event.key()}, modifiers: {event.modifiers()}")
        print(f"Debug: Current focus widget: {self.focusWidget()}")
        
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            print("Debug: Enter/Return key detected")
            # If details list has focus and an item is selected, activate it
            if self.details_list.hasFocus():
                current_item = self.details_list.currentItem()
                if current_item:
                    self._on_detail_item_selected(current_item)
                    return
        else:
            print(f"Debug: Other key - key: {event.key()}, modifiers: {event.modifiers()}")
        
        # Call parent to handle other keys (F5, Escape, etc.)
        print("Debug: Calling parent keyPressEvent")
        super().keyPressEvent(event)
    
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
        
        if field_name == "team_schedule":
            # Handle team schedule navigation
            if not isinstance(field_data, dict):
                QMessageBox.warning(self, "Error", "Invalid team data.")
                return
                
            team_name = field_data.get("team_name", "Unknown Team")
            team_id = field_data.get("team_id")
            
            if not team_id:
                # Infrastructure solution: Try to find team ID through alternative means
                team_id = self._find_team_id_alternative(team_name)
                
            if not team_id:
                # Still no team ID - gracefully handle this
                QMessageBox.information(self, "Team Schedule", 
                    f"Schedule for {team_name} is temporarily unavailable.\n\n"
                    "You can access team schedules from the main league standings.")
                return
                
            # Create team data structure for TeamScheduleDialog
            team_data = {
                'team_id': team_id,
                'team_name': team_name,
                'wins': '',  # TeamScheduleDialog will load this
                'losses': '',
                'record': field_data.get('record', '')
            }
            
            try:
                dlg = TeamScheduleDialog(team_data, field_data.get('league', self.league), self)
                dlg.exec()
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                    f"Failed to load {team_name} schedule: {str(e)}\n\n"
                    "You can try accessing the team schedule from the main league standings.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(f"{field_name.title()} Details")
        dlg.resize(DIALOG_WIDTH, DIALOG_HEIGHT)
        layout = QVBoxLayout()        # Store reference to tab widget for F6 handling
        tab_widget_ref = None
        
        if field_name == "leaders" and isinstance(field_data, (list, dict)):
            try:
                self._add_leaders_data_to_layout(layout, field_data)
                # Find the tab widget that was just added for F6 handling
                for child in layout.children():
                    if hasattr(child, 'widget') and isinstance(child.widget(), QTabWidget):
                        tab_widget_ref = child.widget()
                        break
            except Exception as e:
                error_label = QLabel(f"Leaders display error: {str(e)}")
                layout.addWidget(error_label)
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
        elif field_name == "game_wrap_up":
            # Generate and display comprehensive game wrap-up
            self._generate_and_display_game_wrap_up(field_data)
            return  # Don't continue with dialog creation
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
            
            # Handle F6 for tabbed dialogs (boxscore and leaders)
            if event.key() == Qt.Key.Key_F6 and field_name in ["boxscore", "leaders"] and tab_widget_ref:
                # Cycle through: tab_bar -> first_table -> other_tables -> next_tab -> repeat
                current_tab_index = tab_widget_ref.currentIndex()
                current_widget = tab_widget_ref.widget(current_tab_index)
                
                if current_widget:
                    # Find tables based on field type
                    if field_name == "boxscore":
                        tables = current_widget.findChildren(BoxscoreTable)
                    else:  # leaders
                        tables = current_widget.findChildren(LeadersTable)
                    
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
        
        # Set focus to first table after dialog is shown (for tabbed dialogs)
        if field_name in ["boxscore", "leaders"]:
            def set_focus_to_table():
                # Find the tab widget in the dialog
                tab_widgets = dlg.findChildren(QTabWidget)
                if tab_widgets:
                    tab_widget = tab_widgets[0]
                    tab_widget.setFocus()
                    # Set focus to first table in first tab
                    first_widget = tab_widget.widget(0)
                    if first_widget:
                        if field_name == "boxscore":
                            tables = first_widget.findChildren(BoxscoreTable)
                        else:  # leaders
                            tables = first_widget.findChildren(LeadersTable)
                        if tables and tables[0].rowCount() > 0:
                            QTimer.singleShot(100, lambda: tables[0].setFocus())
                            QTimer.singleShot(100, lambda: tables[0].setCurrentCell(0, 0))
            
            QTimer.singleShot(FOCUS_DELAY_MS, set_focus_to_table)
        
        dlg.exec()
    
    def _play_drive_audio(self, drive=None):
        """Play audio for the currently focused drive (called from GameDetailsView)
        
        Args:
            drive: Optional drive data dict. If not provided, uses current/first previous drive.
        """
        try:
            # Write to debug log
            with open('drive_audio_debug.log', 'a') as log:
                import datetime
                log.write(f"\n{'='*60}\n")
                log.write(f"Drive Audio Call - {datetime.datetime.now()}\n")
                log.write(f"{'='*60}\n")
                
                print("Debug: GameDetailsView _play_drive_audio called")
                log.write("_play_drive_audio CALLED\n")
                
                # Check if we have football audio available
                if not self.football_audio_mapper or not self.football_audio_player:
                    print("Debug: Football audio not available or not initialized")
                    log.write("ERROR: Football audio not initialized\n")
                    return
                
                # Use provided drive or get from current_drives_data
                test_drive = drive
                if not test_drive:
                    # Get drives data from current_drives_data if available
                    if not hasattr(self, 'current_drives_data') or not self.current_drives_data:
                        print("Debug: No current_drives_data available")
                        log.write("ERROR: No current_drives_data\n")
                        return
                    
                    drives_data = self.current_drives_data
                    print(f"Debug: Found drives_data with keys: {list(drives_data.keys())}")
                    
                    # Get a drive to play (current or first previous)
                    current_drive = drives_data.get("current")
                    previous_drives = drives_data.get("previous", [])
                    
                    if current_drive:
                        test_drive = current_drive
                        print("Debug: Using current drive")
                        log.write("Using CURRENT drive\n")
                    elif previous_drives:
                        test_drive = previous_drives[0]
                        print(f"Debug: Using first of {len(previous_drives)} previous drives")
                        log.write(f"Using first of {len(previous_drives)} PREVIOUS drives\n")
                else:
                    print("Debug: Using provided drive data")
                    log.write("Using PROVIDED drive data\n")
                
                if not test_drive:
                    print("Debug: No drives available for audio")
                    log.write("ERROR: No drives available\n")
                    return
                
                # Get drive info for user feedback
                team_info = test_drive.get("team", {})
                team_name = team_info.get("displayName", "Unknown Team")
                description = test_drive.get("description", "Drive")
                print(f"Debug: Playing drive: {team_name} - {description}")
                log.write(f"Drive: {team_name} - {description}\n")
                
                # Check if drive has plays
                plays = test_drive.get('plays', [])
                if not plays:
                    print("Debug: Drive has no plays")
                    log.write("ERROR: Drive has no plays\n")
                    return
                
                print(f"Debug: Drive has {len(plays)} plays")
                log.write(f"Drive has {len(plays)} plays\n")
                
                # Log each play detail
                for i, play in enumerate(plays, 1):
                    play_text = play.get('text', 'Unknown')[:60]
                    yardage = play.get('statYardage', 'N/A')
                    start = play.get('start', {})
                    yards_to_endzone = start.get('yardsToEndzone', 'N/A')
                    log.write(f"  Play {i}: {play_text}\n")
                    log.write(f"    Yardage: {yardage}, YardsToEndzone: {yards_to_endzone}\n")
                
                # Generate and play audio
                audio_sequence = self.football_audio_mapper.map_drive_to_audio_sequence(test_drive)
                if not audio_sequence:
                    print("Debug: No audio sequence generated")
                    log.write("ERROR: No audio sequence generated\n")
                    return
                
                print(f"Debug: Generated {len(audio_sequence)} audio configs")
                log.write(f"Generated {len(audio_sequence)} audio configs\n")
                print(f"Playing {len(audio_sequence)} plays as a drive sequence...")
                
                # Extract field positions for stereo panning
                field_positions = [config.field_position for config in audio_sequence if config.field_position is not None]
                
                # Only use field positions if we have them for all plays
                if len(field_positions) == len(audio_sequence):
                    print(f"Debug: Using stereo field positioning for {len(field_positions)} plays")
                    log.write(f"Using stereo positioning for {len(field_positions)} plays:\n")
                    for i, pos in enumerate(field_positions):
                        print(f"Debug: Play {i+1} at field position {pos:.1f}")
                        log.write(f"  Play {i+1}: field_position={pos:.1f}\n")
                else:
                    print(f"Debug: No stereo positioning (only {len(field_positions)} of {len(audio_sequence)} plays have positions)")
                    log.write(f"No stereo positioning ({len(field_positions)}/{len(audio_sequence)} have positions)\n")
                    field_positions = None
                
                # Provide user feedback in window title
                if hasattr(self, 'parent') and hasattr(self.parent, 'setWindowTitle'):
                    original_title = self.parent.windowTitle()
                    stereo_text = " with stereo positioning" if field_positions else ""
                    self.parent.setWindowTitle(f"[Audio] Playing {team_name} drive{stereo_text}...")
                    
                    # Play the audio with field positions
                    log.write("CALLING play_audio_sequence\n")
                    self.football_audio_player.play_audio_sequence(audio_sequence, silence_between=0.1, field_positions=field_positions)
                    log.write("COMPLETED play_audio_sequence\n")
                    
                    # Restore title after a delay
                    QTimer.singleShot(3000, lambda: self.parent.setWindowTitle(original_title))
                else:
                    # Play without title feedback
                    log.write("CALLING play_audio_sequence (no title)\n")
                    self.football_audio_player.play_audio_sequence(audio_sequence, silence_between=0.1, field_positions=field_positions)
                    log.write("COMPLETED play_audio_sequence (no title)\n")
                
                print("Debug: Drive audio playback completed")
                log.write("Drive audio playback COMPLETED\n")
            
        except Exception as e:
            print(f"Debug: Drive audio error: {e}")
            import traceback
            traceback.print_exc()

    
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
            
            # Add Game Wrap Up option at the end
            self._add_game_wrap_up_option()
            
        except Exception as e:
            self._show_api_error(f"Failed to load game details: {str(e)}")
    
    def _get_team_id_from_original_data(self, team_name: str) -> str:
        """Get team ID from original game data (infrastructure-level solution)"""
        if not self.original_game_data:
            return ""
            
        # Look for team ID in the original game data structure
        competitors = []
        if 'competitions' in self.original_game_data:
            competitions = self.original_game_data.get('competitions', [])
            if competitions:
                competitors = competitions[0].get('competitors', [])
        elif 'competitors' in self.original_game_data:
            competitors = self.original_game_data.get('competitors', [])
            
        # Try to match team by name and get ID
        for competitor in competitors:
            team = competitor.get('team', {})
            team_names = [
                team.get('name', ''),
                team.get('displayName', ''),
                team.get('shortDisplayName', ''),
                team.get('location', ''),
                team.get('nickname', '')
            ]
            
            # Check for exact matches first
            for name in team_names:
                if name and name == team_name:
                    return str(team.get('id', ''))
                    
            # Check for partial matches (handles "Wisconsin Badgers" vs "Badgers")
            for name in team_names:
                if name and (team_name in name or name in team_name):
                    return str(team.get('id', ''))
                    
        return ""

    def _find_team_id_alternative(self, team_name: str) -> str:
        """Alternative method to find team ID when standard extraction fails"""
        # Known team ID mappings for major teams (interim solution)
        team_id_map = {
            'college-football': {
                'Wisconsin Badgers': '275',
                'Badgers': '275',
                'Wisconsin': '275',
                'Michigan Wolverines': '130',
                'Wolverines': '130',
                'Michigan': '130',
                'Ohio State Buckeyes': '194',
                'Buckeyes': '194',
                'Ohio State': '194',
                'Alabama Crimson Tide': '333',
                'Alabama': '333',
                'Crimson Tide': '333',
                # Add more as needed
            }
        }
        
        # Check hardcoded mappings first
        league_map = team_id_map.get(self.league, {})
        for known_name, team_id in league_map.items():
            if known_name.lower() == team_name.lower() or team_name.lower() in known_name.lower() or known_name.lower() in team_name.lower():
                return team_id
        
        try:
            # Try to get current league standings which contain team IDs
            standings_data = ApiService.get_standings(self.league)
            
            if standings_data:
                # Handle both dict format (with groups) and list format
                entries_to_check = []
                
                if isinstance(standings_data, dict):
                    # Look through standings for the team
                    for group in standings_data.get('groups', []):
                        standings = group.get('standings', {})
                        entries_to_check.extend(standings.get('entries', []))
                elif isinstance(standings_data, list):
                    # Direct list format
                    entries_to_check = standings_data
                
                for entry in entries_to_check:
                    team = entry.get('team', {})
                    team_names = [
                        team.get('name', ''),
                        team.get('displayName', ''),
                        team.get('shortDisplayName', ''),
                        team.get('location', ''),
                        team.get('nickname', '')
                    ]
                    
                    # Check for matches
                    for name in team_names:
                        if name and (name == team_name or team_name in name or name in team_name):
                            return str(team.get('id', ''))
        except Exception as e:
            pass  # Silently handle API errors
            
        return ""

    def _extract_team_id(self, team_info: Dict, raw_details: Dict) -> str:
        """Extract team ID from game details data"""
        if not raw_details:
            return ""
            
        # Look for team ID in the header.competitions.competitors
        header = raw_details.get('header', {})
        competitions = header.get('competitions', [])
        if not competitions:
            return ""
            
        competition = competitions[0]
        competitors = competition.get('competitors', [])
        
        # Get the team name we're looking for (from processed game info)
        team_name = team_info.get('name', '')
        
        # Try exact matches with all possible name fields
        for competitor in competitors:
            comp_team = competitor.get('team', {})
            comp_names = [
                comp_team.get('name', ''),
                comp_team.get('displayName', ''),
                comp_team.get('shortDisplayName', ''),
                comp_team.get('alternateDisplayName', '')
            ]
            
            for comp_name in comp_names:
                if comp_name and comp_name == team_name:
                    return str(comp_team.get('id', ''))
        
        # Enhanced fallback: try partial matches since processed names might be different from raw names
        for competitor in competitors:
            comp_team = competitor.get('team', {})
            comp_abbrev = comp_team.get('abbreviation', '')
            comp_location = comp_team.get('location', '')
            comp_nickname = comp_team.get('nickname', '')
            comp_name = comp_team.get('name', '')
            comp_display = comp_team.get('displayName', '')
            
            # Check if abbreviation matches
            if comp_abbrev and comp_abbrev in team_name:
                return str(comp_team.get('id', ''))
                
            # Check if any part of the processed name matches the raw name components
            if comp_location and comp_location in team_name:
                return str(comp_team.get('id', ''))
            if comp_nickname and comp_nickname in team_name:
                return str(comp_team.get('id', ''))
            if comp_name and comp_name in team_name:
                return str(comp_team.get('id', ''))
                
            # Reverse check: see if raw display name contains our processed name parts
            team_words = team_name.split()
            for word in team_words:
                if len(word) > 3:  # Skip short words like "at", "vs", etc.
                    if word in comp_display or word in comp_name or word in comp_location:
                        return str(comp_team.get('id', ''))
                
        return ""

    def _add_basic_game_info(self, details: Dict, raw_details: Dict = None):
        """Add basic game information to the details list"""
        # Extract game information for window title
        game_title_parts = []
        
        # Display teams and records with interactive team names
        if 'teams' in details:
            team_names = []
            for team in details['teams']:
                team_names.append(team['name'])
                home_away = " (Home)" if team['home_away'] == 'home' else " (Away)"
                
                # Use team_id directly from processed details (infrastructure fix)
                team_id = team.get('team_id', '')
                
                # Only use complex extraction if team_id is missing
                if not team_id:
                    # Infrastructure-level team ID resolution (fallback methods)
                    team_id = self._get_team_id_from_original_data(team['name'])
                    if not team_id:
                        team_id = self._extract_team_id(team, raw_details)
                
                # Create interactive team item  
                team_display = f"{team['name']}{home_away}"
                team_item = QListWidgetItem(team_display)
                team_item.setData(Qt.ItemDataRole.UserRole, {
                    "field": "team_schedule",
                    "data": {
                        "team_name": team['name'],
                        "team_id": team_id,
                        "league": self.league,
                        "record": team['record'],
                        "from_game_details": True  # Flag to indicate navigation source
                    }
                })
                self.details_list.addItem(team_item)
                self.details_list.addItem(f"  Record: {team['record']}")
            
            # Build game title with team names
            if len(team_names) >= 2:
                game_title_parts.append(f"{team_names[0]} vs {team_names[1]}")
            elif len(team_names) == 1:
                game_title_parts.append(team_names[0])
        
        # Add date/status information to title if available
        if 'status' in details and details['status']:
            # Only add non-generic status info
            status = details['status']
            if status not in ['Final', 'Scheduled', 'In Progress']:
                game_title_parts.append(status)
        
        # Update window title with game-specific information
        if self.parent_app and self.league:
            title_context = game_title_parts + [self.league] if game_title_parts else ["Game Details", self.league]
            self.parent_app.update_window_title(title_context)
        
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
    
    def _add_game_wrap_up_option(self):
        """Add Game Wrap Up option at the end of the details list"""
        if hasattr(self, 'current_raw_details') and self.current_raw_details:
            # Check if this is a completed game that might have wrap-up content
            header = self.current_raw_details.get('header', {})
            competitions = header.get('competitions', [])
            
            if competitions:
                competition = competitions[0]
                status = competition.get('status', {})
                status_type = status.get('type', {})
                
                # Only add wrap-up for completed games
                state = status_type.get('state', '').lower()
                if state in ['post', 'final']:
                    # Add only the wrap-up item, no heading
                    wrap_up_item = QListWidgetItem("🚧 Game Wrap Up")
                    wrap_up_item.setData(Qt.ItemDataRole.UserRole, {
                        "field": "game_wrap_up",
                        "data": self.current_raw_details
                    })
                    self.details_list.addItem(wrap_up_item)

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
        # Update window title with game context (will be set after game data loads)
        if self.parent_app and self.league:
            # Initial title while loading
            self.parent_app.update_window_title(["Game Details", self.league])
    
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
        """Add leaders data to layout using tabbed interface with one tab per team"""
        if not data:
            layout.addWidget(QLabel("No leaders data available."))
            return
        
        # Handle both list and dict formats for ESPN leaders data
        if isinstance(data, dict):
            # Convert dict format to list format for consistent processing
            if "teams" in data:
                data = data["teams"]
            elif isinstance(data, dict) and all(isinstance(v, (dict, list)) for v in data.values()):
                # Legacy dict format - convert to list structure
                data = [{"team": {"displayName": "Team"}, "leaders": [{"displayName": k, "leaders": [v] if isinstance(v, dict) else v} for k, v in data.items()]}]
        
        if not isinstance(data, list):
            layout.addWidget(QLabel("Leaders data format not recognized."))
            return
        
        # Filter out teams with no data
        valid_teams = []
        for team_data in data:
            if isinstance(team_data, dict) and team_data.get("leaders"):
                valid_teams.append(team_data)
        
        if not valid_teams:
            layout.addWidget(QLabel("No statistical leaders found in data."))
            return
        
        # Create tab widget for teams
        tab_widget = QTabWidget()
        tab_widget.setAccessibleName("Team Leaders")
        tab_widget.setAccessibleDescription("Statistical leaders by team. Use arrow keys to navigate between teams, Tab to enter table.")
        
        # Create a tab for each team
        for team_data in valid_teams:
            team_info = team_data.get("team", {})
            team_name = team_info.get("displayName", team_info.get("abbreviation", "Unknown Team"))
            
            # Create widget for this team's tab
            team_widget = QWidget()
            team_layout = QVBoxLayout()
            
            # Create leaders table for this team
            leaders_table = LeadersTable(parent=self)
            
            # Parse this team's statistical leaders
            team_leaders = team_data.get("leaders", [])
            rows = []
            
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
                        player_name,
                        display_value
                    ])
            
            if rows:
                # Use custom headers for individual team view (no team column needed)
                leaders_table.setColumnCount(3)
                leaders_table.setHorizontalHeaderLabels(["Category", "Player", "Value"])
                leaders_table.setRowCount(len(rows))
                
                for row, data_row in enumerate(rows):
                    for col, value in enumerate(data_row):
                        item = QTableWidgetItem(str(value))
                        leaders_table.setItem(row, col, item)
                
                # Configure table appearance
                leaders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                leaders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
                leaders_table.setAlternatingRowColors(True)
                leaders_table.verticalHeader().setVisible(False)
                
                # Resize columns
                header = leaders_table.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Player name stretches
                
                # Set accessibility
                leaders_table.setAccessibleName(f"{team_name} Statistical Leaders")
                leaders_table.setAccessibleDescription(f"Statistical leaders for {team_name}. Use arrow keys to navigate.")
                
                team_layout.addWidget(leaders_table)
            else:
                team_layout.addWidget(QLabel(f"No statistical leaders available for {team_name}."))
            
            team_widget.setLayout(team_layout)
            tab_widget.addTab(team_widget, team_name)
        
        # Add tab widget to main layout
        layout.addWidget(tab_widget)
        
        # Set focus to first tab initially
        if tab_widget.count() > 0:
            tab_widget.setCurrentIndex(0)
    
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
        # Prevent the button from taking focus away from the drives list
        export_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        header_layout.addWidget(export_btn)
        header_layout.addStretch()  # Push button to the left
        
        layout.addLayout(header_layout)
        
        # Add instruction for football audio if available
        if FOOTBALL_AUDIO_AVAILABLE and self.league in ["NFL", "NCAAF"]:
            audio_instruction = QLabel("💡 Select a drive and press Alt+P to play drive audio")
            audio_instruction.setStyleSheet("color: #666; font-style: italic; margin: 5px 0;")
            layout.addWidget(audio_instruction)
        
        # Create tree widget for drives
        drives_tree = QTreeWidget()
        sport_name = "NFL/NCAAF" if self.league in ["NFL", "NCAAF"] else "Football"
        drives_tree.setAccessibleName(f"{sport_name} Drives Tree")
        
        # Add audio instruction for football games
        audio_instruction = ""
        if FOOTBALL_AUDIO_AVAILABLE and self.league in ["NFL", "NCAAF"]:
            audio_instruction = " Press Alt+P to play drive audio."
        
        drives_tree.setAccessibleDescription(f"Hierarchical view of {sport_name} drives organized by quarter. Use up/down arrows to navigate, left/right to expand/collapse.{audio_instruction}")
        drives_tree.setHeaderLabels(["Drive Summary"])
        
        # Add custom keyPressEvent handler for drives tree (like baseball does for plays)
        def on_drives_key_press(event):
            print(f"Debug: Drives tree keyPressEvent - key: {event.key()}, modifiers: {event.modifiers()}")
            current_item = drives_tree.currentItem()
            
            if event.key() == Qt.Key.Key_P and event.modifiers() == Qt.KeyboardModifier.AltModifier:
                # Alt+P for drive audio (works on drive items)
                print(f"Debug: Alt+P detected! Current item: {current_item}")
                if current_item and FOOTBALL_AUDIO_AVAILABLE and self.league in ["NFL", "NCAAF"]:
                    # Get the drive data from the selected tree item
                    # If a play is selected, get the parent drive item
                    drive_item = current_item
                    drive_data = drive_item.data(0, Qt.ItemDataRole.UserRole)
                    
                    # If no data on current item, check if it's a child (play) and get parent (drive)
                    if not drive_data and drive_item.parent():
                        drive_item = drive_item.parent()
                        drive_data = drive_item.data(0, Qt.ItemDataRole.UserRole)
                        print(f"Debug: Trying parent for drive data")
                    
                    if drive_data:
                        print(f"Debug: Playing drive with {len(drive_data.get('plays', []))} plays")
                        self._play_drive_audio(drive_data)
                        event.accept()
                        return
                    else:
                        print("Debug: No drive data found")
            
            # Fall back to default behavior
            drives_tree.__class__.keyPressEvent(drives_tree, event)
        
        # Override the tree's keyPressEvent (same pattern as baseball audio)
        drives_tree.keyPressEvent = on_drives_key_press
        
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
                    
                    # Store the drive data for audio playback
                    drive_item.setData(0, Qt.ItemDataRole.UserRole, drive)
                    
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
        
        # Set focus to the drives tree for proper keyboard navigation and Alt+P functionality
        drives_tree.setFocus()
        # Ensure the tree can receive keyboard events
        drives_tree.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Select the first drive by default for better user experience
        if drives_tree.topLevelItemCount() > 0:
            first_quarter = drives_tree.topLevelItem(0)
            if first_quarter.childCount() > 0:
                first_drive = first_quarter.child(0)
                drives_tree.setCurrentItem(first_drive)
                # Expand the first quarter so users can see the drives
                first_quarter.setExpanded(True)
    
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
                # Need to differentiate between football and basketball quarters
                # Check for football-specific indicators
                if any(key in sample_play for key in ["driveNumber", "down", "distance", "yardsToEndzone"]):
                    return "NFL"
                else:
                    return "NBA"  # Default basketball for quarters without football indicators
            elif "period" in period_display.lower():
                return "NHL"
            elif "half" in period_display.lower() or "time" in period_display.lower():
                return "Soccer"
        
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
            
            # Show success message with custom dialog
            self._show_export_success_dialog(filename, file_path, app_dir)
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export game log:\n{str(e)}")
    
    def _show_export_success_dialog(self, filename, file_path, app_dir):
        """Show custom export success dialog with View Log and Close buttons"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Complete")
        dialog.setModal(True)
        dialog.resize(450, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Success message
        message = QLabel(f"Game log exported successfully!\n\nFile saved as:\n{filename}\n\nLocation: {app_dir}")
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # View Log button (Alt+G)
        view_button = QPushButton("&View Log")
        view_button.setAccessibleName("View Log Button")
        view_button.setAccessibleDescription("Open the exported game log file")
        view_button.clicked.connect(lambda: self._open_exported_file(file_path, dialog))
        button_layout.addWidget(view_button)
        
        # Close button
        close_button = QPushButton("&Close")
        close_button.setAccessibleName("Close Button") 
        close_button.setAccessibleDescription("Close this dialog and return to game details")
        close_button.clicked.connect(dialog.accept)
        close_button.setDefault(True)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Set focus to View Log button initially
        view_button.setFocus()
        
        dialog.exec()
    
    def _open_exported_file(self, file_path, dialog):
        """Open the exported file in the default application"""
        import os
        import subprocess
        import platform
        
        try:
            # Close the dialog first
            dialog.accept()
            
            # Open file based on platform
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux and others
                subprocess.call(["xdg-open", file_path])
                
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Open Error", 
                f"Could not open the exported file:\n{str(e)}\n\nFile location: {file_path}"
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
    
    def _generate_and_display_game_wrap_up(self, raw_game_data):
        """Generate comprehensive game wrap-up HTML and open in browser"""
        try:
            # Get game ID to fetch fresh data
            game_id = None
            header = raw_game_data.get('header', {})
            competitions = header.get('competitions', [])
            if competitions:
                game_id = competitions[0].get('id')
            
            # If we have a game ID, fetch fresh data directly from ESPN
            fresh_data = None
            if game_id:
                try:
                    import requests
                    url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        fresh_data = response.json()
                except Exception as e:
                    print(f"Could not fetch fresh data: {e}")
            
            # Use fresh data if available, otherwise fall back to processed data
            data_to_use = fresh_data if fresh_data else raw_game_data
            
            # Generate HTML content
            html_content = self._generate_game_wrap_up_html(data_to_use)
            
            # Create temporary HTML file
            import tempfile
            import os
            import webbrowser
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file_path = f.name
            
            # Open in default browser
            webbrowser.open(f'file://{temp_file_path}')
            
            # Show confirmation message
            QMessageBox.information(self, "Game Wrap Up", 
                "Game Wrap Up opened in your default web browser.")
                
        except Exception as e:
            QMessageBox.critical(self, "Wrap Up Error", 
                f"Failed to generate game wrap-up:\n{str(e)}")
    
    def _generate_game_wrap_up_html(self, raw_game_data):
        """Generate comprehensive HTML content for game wrap-up"""
        # Extract key information from raw game data
        header = raw_game_data.get('header', {})
        competitions = header.get('competitions', [])
        
        # Extract teams info and game details
        away_team = home_team = None
        away_score = home_score = "0"
        game_date = ""
        status = {}
        venue = {}
        
        if competitions:
            competition = competitions[0]
            competitors = competition.get('competitors', [])
            game_date = competition.get('date', '')
            status = competition.get('status', {})
            venue = competition.get('venue', {})
            
            for competitor in competitors:
                team_info = competitor.get('team', {})
                score = competitor.get('score', '0')
                
                if competitor.get('homeAway') == 'away':
                    away_team = team_info
                    away_score = score
                elif competitor.get('homeAway') == 'home':
                    home_team = team_info
                    home_score = score
        
        # Article content
        article = raw_game_data.get('article', {})
        
        # Process article text if text processor is available
        if article and text_processor:
            # Clean description (pass complete game data for player name extraction)
            if 'description' in article:
                article['description'] = text_processor.clean_description(article['description'], raw_game_data)
            # Clean story content (pass complete game data for player name extraction)
            if 'story' in article:
                article['story'] = text_processor.clean_description(article['story'], raw_game_data)
        
        # Leaders/statistics
        leaders = raw_game_data.get('leaders', [])
        
        # Boxscore data
        boxscore = raw_game_data.get('boxscore', {})
        
        # Scoring plays
        scoring_plays = raw_game_data.get('scoringPlays', [])
        
        # Drives (for football)
        drives = raw_game_data.get('drives', {})
        
        # HTML template
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Wrap Up - {away_team.get('displayName', 'Away')} vs {home_team.get('displayName', 'Home')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #1a472a 0%, #2e7d32 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .score-line {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 40px;
            margin: 20px 0;
            font-size: 24px;
            font-weight: bold;
        }}
        .team {{
            text-align: center;
            min-width: 200px;
        }}
        .team-name {{
            font-size: 18px;
            margin-bottom: 10px;
        }}
        .team-score {{
            font-size: 36px;
            font-weight: bold;
            color: #ffd700;
        }}
        .vs {{
            font-size: 20px;
            opacity: 0.8;
        }}
        .game-info {{
            text-align: center;
            margin-top: 15px;
            opacity: 0.9;
        }}
        .content-section {{
            background: white;
            margin-bottom: 30px;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section-title {{
            color: #2e7d32;
            border-bottom: 3px solid #2e7d32;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: bold;
        }}
        .article-content {{
            font-size: 16px;
            line-height: 1.8;
        }}
        .article-headline {{
            font-size: 28px;
            font-weight: bold;
            color: #1a472a;
            margin-bottom: 15px;
            line-height: 1.3;
        }}
        .article-description {{
            font-size: 18px;
            color: #555;
            font-style: italic;
            margin-bottom: 25px;
            border-left: 4px solid #2e7d32;
            padding-left: 20px;
        }}
        .leaders-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .leader-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #2e7d32;
        }}
        .leader-category {{
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 10px;
        }}
        .leader-stat {{
            margin: 5px 0;
        }}
        .scoring-plays {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }}
        .play {{
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #ff6b35;
        }}
        .quarter {{
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 5px;
        }}
        .boxscore-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .boxscore-table th,
        .boxscore-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .boxscore-table th {{
            background-color: #2e7d32;
            color: white;
            font-weight: bold;
        }}
        .boxscore-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .drive-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        .drive-table th,
        .drive-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        .drive-table th {{
            background-color: #f8f9fa;
            font-weight: bold;
            width: 30%;
        }}
        .drives-summary-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .drives-summary-table th,
        .drives-summary-table td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .drives-summary-table thead th {{
            background-color: #2e7d32;
            color: white;
            font-weight: bold;
        }}
        .drives-summary-table tbody th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .drives-summary-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .current-drive,
        .previous-drives {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            font-style: italic;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="score-line">
            <div class="team">
                <div class="team-name">{away_team.get('displayName', 'Away Team') if away_team else 'Away Team'}</div>
                <div class="team-score">{away_score}</div>
            </div>
            <div class="vs">@</div>
            <div class="team">
                <div class="team-name">{home_team.get('displayName', 'Home Team') if home_team else 'Home Team'}</div>
                <div class="team-score">{home_score}</div>
            </div>
        </div>
        <div class="game-info">
            {self._format_game_date(game_date)} • {venue.get('fullName', '')}
            <br>{status.get('type', {}).get('description', 'Final')}
        </div>
    </div>
"""
        
        # Add article content if available
        if article and article.get('headline'):
            # Clean description if text processor is available
            description = article.get('description', '')
            if text_processor:
                description = text_processor.clean_description(description, raw_game_data)
            
            html_content += f"""
    <div class="content-section">
        <h2 class="section-title">📰 Game Story</h2>
        <h1 class="article-headline">{article.get('headline', '')}</h1>
        <p class="article-description">{description}</p>
        <div class="article-content">
            {self._format_article_story(article.get('story', ''), raw_game_data)}
        </div>
    </div>
"""
        
        # Add key performers/leaders
        if leaders:
            html_content += f"""
    <div class="content-section">
        <h2 class="section-title">⭐ Key Performers</h2>
        <div class="leaders-grid">
            {self._format_leaders_html(leaders)}
        </div>
    </div>
"""
        
        # Add scoring plays if available
        if scoring_plays:
            html_content += f"""
    <div class="content-section">
        <h2 class="section-title">🎯 Scoring Summary</h2>
        <div class="scoring-plays">
            {self._format_scoring_plays_html(scoring_plays)}
        </div>
    </div>
"""
        
        # Add boxscore summary if available
        if boxscore and boxscore.get('teams'):
            html_content += f"""
    <div class="content-section">
        <h2 class="section-title">📊 Team Statistics</h2>
        {self._format_boxscore_html(boxscore)}
    </div>
"""
        
        # Add drives summary for football
        if drives and (drives.get('current') or drives.get('previous')):
            html_content += f"""
    <div class="content-section">
        <h2 class="section-title">🏈 Drive Summary</h2>
        {self._format_drives_html(drives)}
    </div>
"""
        
        # Close HTML
        html_content += f"""
    <div class="timestamp">
        Generated on {self._get_current_timestamp()}
    </div>
</body>
</html>
"""
        
        return html_content
    
    def _format_game_date(self, date_str):
        """Format game date for display"""
        try:
            from datetime import datetime
            if date_str:
                # Parse ISO date format
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime('%B %d, %Y')
        except:
            pass
        return date_str or ''
    
    def _format_article_story(self, story, game_data=None):
        """Format article story content for HTML display"""
        if not story:
            return ""
        
        # Use text processor if available to clean ESPN placeholders
        if text_processor:
            story = text_processor.clean_description(story, game_data or {})
        
        # Clean up HTML tags and format for better display
        import re
        
        # Handle broken or incomplete story content more gracefully
        # Look for sentences that start with missing content
        story = re.sub(r'^\s*—\s*\[Player\]', '[Player]', story, flags=re.MULTILINE)
        story = re.sub(r'^\s*—\s*\\\d+', '[Player]', story, flags=re.MULTILINE)
        
        # Clean up any remaining orphaned dashes from broken content
        story = re.sub(r'—\s*(?=\s*[A-Z])', '', story)
        
        # Replace HTML links with text only for now (keep the linked text but remove the link)
        story = re.sub(r'<a[^>]*>(.*?)</a>', r'\\1', story)
        
        # Replace headline tags with proper HTML
        story = re.sub(r'<hl2>(.*?)</hl2>', r'<h3 style="color: #2e7d32; margin: 20px 0 10px 0;">\\1</h3>', story)
        
        # Clean up extra whitespace and newlines
        story = re.sub(r'\n\s*\n', '\n\n', story)  # Normalize paragraph breaks
        story = re.sub(r'\r\n', '\n', story)  # Normalize line endings
        
        # Replace double newlines with paragraph breaks
        story = story.replace('\n\n', '</p><p>')
        
        # Clean up any remaining whitespace issues
        story = re.sub(r'\s+', ' ', story)  # Multiple spaces to single space
        story = story.strip()
        
        # Wrap in paragraphs
        if story:
            story = f'<p>{story}</p>'
        
        return story
    
    def _format_leaders_html(self, leaders):
        """Format leaders data for HTML display"""
        html = ""
        
        for team_leaders in leaders:
            team_name = team_leaders.get('team', {}).get('displayName', 'Team')
            html += f'<div style="margin-bottom: 20px;"><h4 style="color: #2e7d32;">{team_name}</h4>'
            
            team_leader_data = team_leaders.get('leaders', [])
            for category in team_leader_data:
                category_name = category.get('displayName', 'Category')
                html += f'<div class="leader-card">'
                html += f'<div class="leader-category">{category_name}</div>'
                
                for leader in category.get('leaders', []):
                    athlete = leader.get('athlete', {})
                    display_value = leader.get('displayValue', leader.get('value', ''))
                    html += f'<div class="leader-stat">{athlete.get("displayName", "Player")}: {display_value}</div>'
                
                html += '</div>'
            
            html += '</div>'
        
        return html
    
    def _format_scoring_plays_html(self, scoring_plays):
        """Format scoring plays for HTML display"""
        html = ""
        current_period = None
        
        for play in scoring_plays:
            period = play.get('period', {})
            period_number = period.get('number', 1)
            period_name = period.get('displayName', f'Period {period_number}')
            
            if current_period != period_number:
                html += f'<div class="quarter">{period_name}</div>'
                current_period = period_number
            
            team = play.get('team', {})
            clock = play.get('clock', {}).get('displayValue', '')
            text = play.get('text', '')
            
            html += f'<div class="play">'
            html += f'<strong>{team.get("displayName", "Team")}</strong> - {clock}<br>'
            html += f'{text}'
            html += '</div>'
        
        return html
    
    def _format_boxscore_html(self, boxscore):
        """Format boxscore data for HTML display - screen reader friendly"""
        teams = boxscore.get('teams', [])
        if not teams or len(teams) < 2:
            return "<p>No team statistics available.</p>"
        
        # Extract team names
        team1 = teams[0].get('team', {}).get('displayName', 'Team 1')
        team2 = teams[1].get('team', {}).get('displayName', 'Team 2')
        
        # Get all statistics from both teams
        team1_stats = teams[0].get('statistics', [])
        team2_stats = teams[1].get('statistics', [])
        
        # Create a map of all available statistics
        all_stats = {}
        
        # Process team 1 stats
        for stat in team1_stats:
            label = stat.get('label', '')
            value = stat.get('displayValue', stat.get('value', ''))
            if label:
                all_stats[label] = {'team1': value, 'team2': '-'}
        
        # Process team 2 stats  
        for stat in team2_stats:
            label = stat.get('label', '')
            value = stat.get('displayValue', stat.get('value', ''))
            if label:
                if label in all_stats:
                    all_stats[label]['team2'] = value
                else:
                    all_stats[label] = {'team1': '-', 'team2': value}
        
        if not all_stats:
            return "<p>No statistics available.</p>"
        
        # Create a clean, accessible 3-column table
        html = '''
        <table class="boxscore-table" role="table" aria-label="Team Statistics Comparison">
            <thead>
                <tr>
                    <th scope="col">Statistic</th>
                    <th scope="col">{team1}</th>
                    <th scope="col">{team2}</th>
                </tr>
            </thead>
            <tbody>
        '''.format(team1=team1, team2=team2)
        
        # Add each statistic row
        for stat_name, values in all_stats.items():
            html += f'''
                <tr>
                    <th scope="row">{stat_name}</th>
                    <td>{values['team1']}</td>
                    <td>{values['team2']}</td>
                </tr>
            '''
        
        html += '''
            </tbody>
        </table>
        '''
        
        return html
    
    def _format_drives_html(self, drives):
        """Format drives data for HTML display - screen reader friendly"""
        html = ""
        
        # Current drive
        current = drives.get('current')
        if current:
            team = current.get('team', {})
            team_name = team.get('displayName', 'Team')
            plays = current.get('plays', 0)
            yards = current.get('yards', 0)
            
            html += f'''
            <div class="current-drive">
                <h4>Current Drive</h4>
                <table class="drive-table" role="table" aria-label="Current Drive Information">
                    <tr><th scope="row">Team:</th><td>{team_name}</td></tr>
                    <tr><th scope="row">Plays:</th><td>{plays}</td></tr>
                    <tr><th scope="row">Yards:</th><td>{yards}</td></tr>
                </table>
            </div>
            '''
        
        # Previous drives summary
        previous = drives.get('previous', [])
        if previous:
            html += f'''
            <div class="previous-drives">
                <h4>Recent Drives ({len(previous)} total)</h4>
                <table class="drives-summary-table" role="table" aria-label="Recent Drives Summary">
                    <thead>
                        <tr>
                            <th scope="col">Team</th>
                            <th scope="col">Plays</th>
                            <th scope="col">Yards</th>
                            <th scope="col">Result</th>
                        </tr>
                    </thead>
                    <tbody>
            '''
            
            # Show last 5 drives for readability
            for drive in previous[-5:]:
                team = drive.get('team', {})
                team_name = team.get('displayName', 'Team')
                result = drive.get('result', 'No result')
                plays = drive.get('plays', 0)
                yards = drive.get('yards', 0)
                
                html += f'''
                    <tr>
                        <th scope="row">{team_name}</th>
                        <td>{plays}</td>
                        <td>{yards}</td>
                        <td>{result}</td>
                    </tr>
                '''
            
            html += '''
                    </tbody>
                </table>
            </div>
            '''
        
        if not html:
            html = "<p>No drive information available.</p>"
            
        return html
    
    def _get_current_timestamp(self):
        """Get current timestamp for wrap-up generation"""
        from datetime import datetime
        return datetime.now().strftime('%B %d, %Y at %I:%M %p')

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
        elif sport_type in ("NFL", "Football", "NCAAF"):
            if has_drives:
                html += self._generate_football_drives_html()
            else:
                html += self._generate_football_html()
        elif sport_type in ("NBA", "WNBA", "NCAAM"):
            html += self._generate_basketball_html()
        elif sport_type == "NHL":
            html += self._generate_hockey_html()
        elif sport_type == "Soccer":
            html += self._generate_soccer_html()
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
        # Check if we have plays data
        if not hasattr(self, 'current_plays_data') or not self.current_plays_data:
            return '<div class="period"><div class="period-header">No baseball data available for export</div></div>'
        
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
        # Check if we have plays data
        if not hasattr(self, 'current_plays_data') or not self.current_plays_data:
            return '<div class="period"><div class="period-header">No football play data available for export</div></div>'
        
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
        
        # Check if we have plays data
        if hasattr(self, 'current_plays_data') and self.current_plays_data:
            for i, play in enumerate(self.current_plays_data, 1):
                play_text = play.get("text", f"Play {i}")
                html += f'<div class="play">{play_text}</div>'
        else:
            html += '<div class="play">No play data available for export.</div>'
        
        html += '</div>'
        return html

    def _generate_basketball_html(self):
        """Generate HTML for basketball game log"""
        # Check if we have plays data
        if not hasattr(self, 'current_plays_data') or not self.current_plays_data:
            return '<div class="period"><div class="period-header">No basketball data available for export</div></div>'
        
        # Group by quarter
        quarter_groups = {}
        for play in self.current_plays_data:
            period_info = play.get("period", {})
            period_display = period_info.get("displayValue", f"{period_info.get('number', 1)}Q")
            
            if period_display not in quarter_groups:
                quarter_groups[period_display] = []
            quarter_groups[period_display].append(play)
        
        html = ""
        for period_display in sorted(quarter_groups.keys(), key=lambda x: int(x.replace('Q', '')) if x.replace('Q', '').isdigit() else 999):
            html += f'<div class="period">'
            html += f'<div class="period-header">{period_display}</div>'
            
            for play in quarter_groups[period_display]:
                play_text = play.get("text", "Play")
                score_value = play.get("scoreValue", 0)
                css_class = "play scoring" if score_value > 0 else "play"
                html += f'<div class="{css_class}">{play_text}</div>'
            
            html += '</div>'
        
        return html

    def _generate_hockey_html(self):
        """Generate HTML for hockey game log"""
        # Check if we have plays data
        if not hasattr(self, 'current_plays_data') or not self.current_plays_data:
            return '<div class="period"><div class="period-header">No hockey data available for export</div></div>'
        
        # Group by period
        period_groups = {}
        for play in self.current_plays_data:
            period_info = play.get("period", {})
            period_display = period_info.get("displayValue", f"Period {period_info.get('number', 1)}")
            
            if period_display not in period_groups:
                period_groups[period_display] = []
            period_groups[period_display].append(play)
        
        html = ""
        for period_display in sorted(period_groups.keys()):
            html += f'<div class="period">'
            html += f'<div class="period-header">{period_display}</div>'
            
            for play in period_groups[period_display]:
                play_text = play.get("text", "Play")
                score_value = play.get("scoreValue", 0)
                css_class = "play scoring" if score_value > 0 else "play"
                html += f'<div class="{css_class}">{play_text}</div>'
            
            html += '</div>'
        
        return html

    def _generate_soccer_html(self):
        """Generate HTML for soccer game log"""
        # Check if we have plays data
        if not hasattr(self, 'current_plays_data') or not self.current_plays_data:
            return '<div class="period"><div class="period-header">No soccer data available for export</div></div>'
        
        # Group by half
        half_groups = {}
        for play in self.current_plays_data:
            period_info = play.get("period", {})
            period_display = period_info.get("displayValue", f"Half {period_info.get('number', 1)}")
            
            if period_display not in half_groups:
                half_groups[period_display] = []
            half_groups[period_display].append(play)
        
        html = ""
        for period_display in sorted(half_groups.keys()):
            html += f'<div class="period">'
            html += f'<div class="period-header">{period_display}</div>'
            
            for play in half_groups[period_display]:
                play_text = play.get("text", "Play")
                # Soccer events like goals, cards, substitutions
                event_type = play.get("type", {}).get("text", "")
                css_class = "play scoring" if "goal" in event_type.lower() else "play"
                html += f'<div class="{css_class}">{play_text}</div>'
            
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
    
    def __init__(self, game_id: str, league: str, parent=None, original_game_data=None):
        super().__init__(parent)
        self.game_id = game_id
        self.league = league
        self.original_game_data = original_game_data
        
        # Add config attribute that GameDetailsView expects
        self.config = {league: ["standings", "leaders", "boxscore", "injuries", "news"]}
        
        # Initialize football audio system if available
        self.audio_mapper = None
        self.audio_player = None
        self.drive_player = None
        if FOOTBALL_AUDIO_AVAILABLE and league in ["NFL", "NCAAF"]:
            try:
                self.audio_mapper = FootballAudioMapper()
                self.audio_player = AudioPlayer()
                self.drive_player = FootballDrivePlayer()  # FootballDrivePlayer doesn't take parameters
            except Exception as e:
                print(f"Failed to initialize football audio: {e}")
                self.audio_mapper = None
        
        self.setWindowTitle(f"Game Details - {league}")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create game details view
        self.game_details_view = GameDetailsView(self, league, game_id, original_game_data)
        layout.addWidget(self.game_details_view)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("&Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_window_title(self, context_parts=None):
        """Update dialog window title with context information"""
        if context_parts:
            # Build title from context parts
            title = " - ".join(str(part) for part in context_parts)
            self.setWindowTitle(title)
        else:
            # Default title
            self.setWindowTitle(f"Game Details - {self.league}")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        elif (event.modifiers() == Qt.KeyboardModifier.AltModifier and 
              event.key() == Qt.Key.Key_P and 
              self.drive_player and 
              self.league in ["NFL", "NCAAF"]):
            self._play_focused_drive_audio()
            return
        super().keyPressEvent(event)
    
    def _play_focused_drive_audio(self):
        """Play audio for the currently focused drive"""
        try:
            self._show_audio_message("Attempting to play drive audio...")
            print("Debug: Starting drive audio playback")
            
            # Check if audio system is available
            if not self.audio_mapper or not self.audio_player:
                self._show_audio_message("Audio system not available")
                print("Debug: Audio system not initialized")
                return
            
            # Get the currently focused drive data
            current_drive = self._get_focused_drive_data()
            if not current_drive:
                self._show_audio_message("No drive data found")
                print("Debug: No drive data available")
                return
            
            print(f"Debug: Found drive data: {current_drive.get('team', {}).get('displayName', 'Unknown')} - {current_drive.get('description', 'No description')}")
            
            # Get drive summary for user feedback
            drive_summary = self._get_drive_summary(current_drive)
            self._show_audio_message(f"Playing drive audio: {drive_summary}")
            print(f"Debug: Drive summary: {drive_summary}")
            
            # Check if drive has plays
            plays = current_drive.get('plays', [])
            if not plays:
                self._show_audio_message("No plays found in drive")
                print("Debug: Drive has no plays")
                return
            
            print(f"Debug: Drive has {len(plays)} plays")
            
            # Generate the audio sequence for the drive
            audio_sequence = self.audio_mapper.map_drive_to_audio_sequence(current_drive)
            
            if not audio_sequence:
                self._show_audio_message("No audio data generated for this drive")
                print("Debug: Audio mapper returned empty sequence")
                return
            
            print(f"Debug: Generated {len(audio_sequence)} audio configs")
            
            # Play the entire audio sequence at once (with proper stereo positioning)
            print(f"Playing {len(audio_sequence)} plays as a drive sequence...")
            self._show_audio_message(f"Playing {len(audio_sequence)} plays...")
            
            self.audio_player.play_audio_sequence(audio_sequence, silence_between=0.1)
            
            self._show_audio_message("Drive audio playback completed")
            print("Debug: Audio playback completed successfully")
            
        except Exception as e:
            self._show_audio_message(f"Audio playback error: {str(e)}")
            print(f"Debug: Full error: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_focused_drive_data(self):
        """Extract drive data from currently focused item in the drives tree"""
        print("Debug: Attempting to get focused drive data")
        
        # Get the drives data from the game details view
        if not hasattr(self.game_details_view, 'current_drives_data'):
            print("Debug: Game details view has no current_drives_data attribute")
            return None
        
        drives_data = self.game_details_view.current_drives_data
        if not drives_data:
            print("Debug: current_drives_data is empty")
            return None
        
        print(f"Debug: Found drives_data with keys: {list(drives_data.keys())}")
        
        # Find the drives tree widget
        drives_tree = None
        all_trees = self.game_details_view.findChildren(QTreeWidget)
        print(f"Debug: Found {len(all_trees)} QTreeWidget children")
        
        for i, widget in enumerate(all_trees):
            accessible_name = widget.accessibleName()
            print(f"Debug: Tree {i}: accessibleName = '{accessible_name}'")
            if "drives" in accessible_name.lower():
                drives_tree = widget
                print(f"Debug: Selected drives tree: {accessible_name}")
                break
        
        if not drives_tree:
            print("Debug: No drives tree found, using fallback")
            # Fallback: return the first available drive
            current_drive = drives_data.get("current")
            if current_drive:
                print("Debug: Fallback - returning current drive")
                return current_drive
            previous_drives = drives_data.get("previous", [])
            if previous_drives:
                print(f"Debug: Fallback - returning first of {len(previous_drives)} previous drives")
                return previous_drives[0]
            print("Debug: Fallback - no drives available")
            return None
        
        # Get currently selected item from the tree
        current_item = drives_tree.currentItem()
        if not current_item:
            print("Debug: No item currently selected in drives tree")
            # No item selected, return first available drive
            current_drive = drives_data.get("current")
            if current_drive:
                print("Debug: No selection - returning current drive")
                return current_drive
            previous_drives = drives_data.get("previous", [])
            if previous_drives:
                print(f"Debug: No selection - returning first of {len(previous_drives)} previous drives")
                return previous_drives[0]
            print("Debug: No selection - no drives available")
            return None
        
        print(f"Debug: Current item text: '{current_item.text(0)}'")
        
        # Try to get drive data from the tree item
        drive_data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if drive_data:
            print("Debug: Found drive data in current item")
            return drive_data
        
        # Check parent item (in case a play is selected under a drive)
        parent_item = current_item.parent()
        if parent_item:
            print(f"Debug: Checking parent item: '{parent_item.text(0)}'")
            parent_drive_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
            if parent_drive_data:
                print("Debug: Found drive data in parent item")
                return parent_drive_data
        
        print("Debug: No drive data in selected item or parent, using fallback")
        # Fallback: return first available drive
        current_drive = drives_data.get("current")
        if current_drive:
            print("Debug: Final fallback - returning current drive")
            return current_drive
        previous_drives = drives_data.get("previous", [])
        if previous_drives:
            print(f"Debug: Final fallback - returning first of {len(previous_drives)} previous drives")
            return previous_drives[0]
        print("Debug: Final fallback - no drives available")
        return None
        return None
    
    def _get_drive_summary(self, drive):
        """Get a brief summary of the drive for user feedback"""
        team_info = drive.get("team", {})
        team_name = team_info.get("displayName", "Unknown Team")
        description = drive.get("description", "Drive")
        return f"{team_name} - {description}"
    
    def _show_audio_message(self, message):
        """Show temporary message about audio playback"""
        print(f"Football Audio: {message}")
        # Also try to show in window title temporarily
        original_title = self.windowTitle()
        self.setWindowTitle(f"[Audio] {message}")
        QTimer.singleShot(3000, lambda: self.setWindowTitle(original_title))


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
                detail_dialog = GameDetailsDialog(game_id, self.league, self, game_data)
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
        self.expanded_view = False
        self.division_tables: List[StandingsTable] = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Always use expanded view (no user toggle to prevent issues)
        self.expanded_view = True
        
        if not self.standings_data.teams:
            layout.addWidget(QLabel(f"No standings data available for {self.league}."))
        else:
            has_divisions = len(self.standings_data.divisions) > 1 or any(
                d != "League" for d in self.standings_data.divisions
            )
            if has_divisions and self.league in ["MLB", "NFL", "NBA", "NHL", "NCAAF", "NCAAM", "NCAAWB", "WNBA"]:
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
    
    def _on_view_changed(self, index):
        """Handle combo box selection change"""
        expanded = index == 1  # 1 = expanded view
        self._toggle_view(expanded)
    
    def _toggle_view(self, expanded: bool):
        """Toggle between basic and expanded standings view"""
        if self.expanded_view == expanded:
            return
            
        self.expanded_view = expanded
        
        # Update tables
        if self.single_table:
            self.single_table.set_expanded_view(expanded)
            self.single_table.populate_standings(self.standings_data.teams, set_focus=True)
        
        # Update division tables through tab widget
        if self.tab_widget:
            current_tab_index = self.tab_widget.currentIndex()
            for i in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(i)
                if hasattr(widget, 'table'):
                    table = widget.table
                    table.set_expanded_view(expanded)
                    # Repopulate with the table's division data
                    division_name = table.division_name
                    if division_name in self.standings_data.divisions:
                        # Set focus on the currently visible tab's table
                        should_focus = (i == current_tab_index)
                        table.populate_standings(self.standings_data.divisions[division_name], set_focus=should_focus)
            
            # Ensure focus is properly restored after toggle with a slight delay
            from PyQt6.QtCore import QTimer
            def restore_focus():
                if current_tab_index < self.tab_widget.count():
                    current_widget = self.tab_widget.widget(current_tab_index)
                    if hasattr(current_widget, 'table'):
                        current_widget.table.setFocus()
                        current_widget.table.setCurrentCell(0, 0)
            
            QTimer.singleShot(50, restore_focus)
    
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
        table = StandingsTable(parent=self, division_name=division_name, league=self.league, expanded=self.expanded_view)
        table.populate_standings(teams, set_focus=True)
        layout.addWidget(table)
        widget.setLayout(layout)
        widget.table = table  # type: ignore[attr-defined]
        return widget
    
    def _create_single_standings_table(self, teams: List[Dict]) -> StandingsTable:
        table = StandingsTable(parent=self, league=self.league, expanded=self.expanded_view)
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


class StatisticsChoiceDialog(QDialog):
    """First dialog for statistics: Choose between Team or Player statistics"""
    
    def __init__(self, league: str, parent=None):
        super().__init__(parent)
        self.league = league
        self.choice = None
        self.setWindowTitle(f"{league} Statistics")
        self.resize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"Choose Statistics Type for {self.league}")
        title.setAccessibleName(f"{self.league} Statistics Selection")
        layout.addWidget(title)
        
        # Choice list (consistent with rest of app)
        self.choice_list = QListWidget()
        self.choice_list.setAccessibleName("Statistics Type List")
        self.choice_list.setAccessibleDescription("Choose between team or player statistics. Press Enter to select.")
        
        # Add options
        team_item = QListWidgetItem("Team Statistics")
        team_item.setData(Qt.ItemDataRole.UserRole, "team")
        team_item.setToolTip("View statistics for all teams in the league")
        self.choice_list.addItem(team_item)
        
        player_item = QListWidgetItem("Player Statistics")
        player_item.setData(Qt.ItemDataRole.UserRole, "player") 
        player_item.setToolTip("View statistics for individual players")
        self.choice_list.addItem(player_item)
        
        # Connect selection events
        self.choice_list.itemActivated.connect(self._on_choice_activated)
        self.choice_list.itemDoubleClicked.connect(self._on_choice_activated)
        
        layout.addWidget(self.choice_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("Select")
        select_btn.setDefault(True)
        select_btn.clicked.connect(self._on_select_clicked)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(select_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus to list
        self.choice_list.setFocus()
        self.choice_list.setCurrentRow(0)
    
    def _on_choice_activated(self, item):
        """Handle item activation (Enter or double-click)"""
        choice_type = item.data(Qt.ItemDataRole.UserRole)
        if choice_type:
            self.choice = choice_type
            self.accept()
    
    def _on_select_clicked(self):
        """Handle Select button click"""
        current_item = self.choice_list.currentItem()
        if current_item:
            self._on_choice_activated(current_item)
    
    def get_choice(self):
        return self.choice


class StatisticsViewDialog(QDialog):
    """Second dialog for statistics: Select stat and view results table"""
    
    def __init__(self, league: str, stat_type: str, parent=None):
        super().__init__(parent)
        print(f"DEBUG: StatisticsViewDialog.__init__ called with league={league}, stat_type={stat_type}")
        self.league = league
        self.stat_type = stat_type  # "team" or "player"
        self.setWindowTitle(f"{league} {stat_type.title()} Statistics")
        self.resize(1000, 700)
        self.statistics_data = None
        print(f"DEBUG: About to call setup_ui")
        self.setup_ui()
        print(f"DEBUG: setup_ui completed")
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"{self.league} {self.stat_type.title()} Statistics")
        layout.addWidget(title)
        
        # Load statistics data IMMEDIATELY and show available stats
        try:
            print(f"DEBUG: Loading {self.stat_type} statistics data for {self.league}")
            
            # Only load the specific type of statistics we need
            if self.stat_type == "player":
                self.statistics_data = ApiService.get_player_statistics(self.league)
            else:  # team
                self.statistics_data = ApiService.get_team_statistics(self.league)
            
            if self.statistics_data:
                available_stats = self._get_available_statistics()
                print(f"DEBUG: Got {len(available_stats)} available stats")
                
                if available_stats:
                    self._create_working_statistics_interface(layout, available_stats)
                else:
                    no_data_label = QLabel(f"No {self.stat_type} statistics available for {self.league}")
                    layout.addWidget(no_data_label)
            else:
                no_data_label = QLabel(f"Unable to load statistics data for {self.league}")
                layout.addWidget(no_data_label)
                
        except Exception as e:
            print(f"DEBUG: Exception in setup_ui: {str(e)}")
            import traceback
            traceback.print_exc()
            error_label = QLabel(f"Error loading statistics: {str(e)}")
            layout.addWidget(error_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setAutoDefault(False)  # Prevent auto-activation
        close_btn.setDefault(False)      # Not the default button
        close_btn.clicked.connect(lambda: self._debug_accept("Main close button"))
        layout.addWidget(close_btn)

        self.setLayout(layout)
    
    def _debug_accept(self, reason):
        """Debug wrapper for accept() to track why dialog is closing"""
        print(f"DEBUG: StatisticsViewDialog.accept() called - reason: {reason}")
        self.accept()
    
    def keyPressEvent(self, event):
        """Handle key press events for navigation"""
        if event.key() == Qt.Key.Key_F6:
            # Cycle between stats list and results list
            current_focus = self.focusWidget()
            if hasattr(self, 'stats_list') and hasattr(self, 'results_list'):
                if current_focus == self.stats_list:
                    # Move to results list if visible
                    if self.results_list.isVisible():
                        self.results_list.setFocus()
                    else:
                        # If no results visible, stay on stats list
                        self.stats_list.setFocus()
                else:
                    # Move back to stats list
                    self.stats_list.setFocus()
            event.accept()
        elif event.key() == Qt.Key.Key_D and event.modifiers() == Qt.KeyboardModifier.AltModifier:
            # Alt+D: Show stat definitions
            self._show_stat_definitions()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def _switch_to_player_stats(self):
        """Switch to player statistics"""
        self.stat_type = "player"
        self.setWindowTitle(f"{self.league} {self.stat_type.title()} Statistics")
        
        # Clear layout and rebuild
        layout = self.layout()
        self._clear_layout(layout)
        self.setup_ui()
    
    def _switch_to_team_stats(self):
        """Switch to team statistics"""
        self.stat_type = "team"
        self.setWindowTitle(f"{self.league} {self.stat_type.title()} Statistics")
        
        # Clear layout and rebuild
        layout = self.layout()
        self._clear_layout(layout)
        self.setup_ui()
    
    def _clear_layout(self, layout):
        """Clear all widgets from layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _create_working_statistics_interface(self, layout, available_stats):
        """Create working statistics interface with immediate data display"""
        
        # Split layout: Left side for stat selection, right side for results
        h_layout = QHBoxLayout()
        
        # Left side: Statistics list
        left_widget = QWidget()
        left_widget.setMaximumWidth(300)
        left_layout = QVBoxLayout()
        
        stats_label = QLabel("Select a Statistic:")
        left_layout.addWidget(stats_label)
        
        # Add note about data timeframe  
        if self.league.upper() == "MLB":
            note_label = QLabel("📊 Full Season Statistics")
            note_label.setStyleSheet("color: #0066cc; font-weight: bold; font-size: 9pt;")
        else:
            note_label = QLabel("📊 Note: Shows recent performance leaders")
            note_label.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        note_label.setWordWrap(True)
        left_layout.addWidget(note_label)
        
        self.stats_list = QListWidget()
        self.stats_list.setAccessibleName(f"{self.stat_type.title()} Statistics List")
        self.stats_list.setAccessibleDescription(f"List of available {self.stat_type} statistics. Select one to view rankings.")
        
        # Populate statistics list with ACTUAL available stats (not categories)
        for stat_info in available_stats:
            stat_name = stat_info.get('name', 'Unknown')
            item = QListWidgetItem(stat_name)
            item.setData(Qt.ItemDataRole.UserRole, stat_info)  # Store the actual stat data
            self.stats_list.addItem(item)
        
        # Connect selection events
        self.stats_list.itemActivated.connect(self._on_working_stat_selected)
        self.stats_list.itemClicked.connect(self._on_working_stat_selected)
        
        left_layout.addWidget(self.stats_list)
        left_widget.setLayout(left_layout)
        
        # Right side: Results display
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        self.results_label = QLabel("Select a statistic to view rankings")
        right_layout.addWidget(self.results_label)
        
        # Results list (concatenated format: rank team value)
        self.results_list = QListWidget()
        self.results_list.setAccessibleName("Statistics Results List")
        self.results_list.setAccessibleDescription("List showing rankings for the selected statistic")
        self.results_list.hide()  # Hide until stat is selected
        right_layout.addWidget(self.results_list)
        
        right_widget.setLayout(right_layout)
        
        # Add to horizontal layout
        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        
        layout.addLayout(h_layout)
        
        # Set the main layout
        self.setLayout(layout)
    
    def _on_working_stat_selected(self, item):
        """Handle stat selection with working approach - data is already loaded"""
        print(f"DEBUG: _on_working_stat_selected called")
        if item:
            stat_info = item.data(Qt.ItemDataRole.UserRole)
            if stat_info:
                print(f"DEBUG: Displaying results for: {stat_info.get('name')}")
                self._display_stat_results(stat_info)
            else:
                print(f"DEBUG: No stat_info in item data")
        else:
            print(f"DEBUG: _on_working_stat_selected called with None item")
    
    def _display_stat_results(self, stat_info):
        """Display results in concatenated list format for the selected statistic"""
        try:
            stat_name = stat_info.get('stat_name', 'Unknown')
            stat_type = stat_info.get('type', 'unknown')
            data = stat_info.get('data', [])
            
            # Update results label with data context
            if stat_type == "player":
                if self.league.upper() == "MLB":
                    header_text = f"Season Leaders: {stat_info.get('name', stat_name)}"
                else:
                    header_text = f"Recent Performance Leaders: {stat_info.get('name', stat_name)}"
            else:
                header_text = f"Top Rankings: {stat_info.get('name', stat_name)}"
            
            self.results_label.setText(header_text)
            
            # Clear and show results list
            self.results_list.clear()
            self.results_list.show()
            
            # Display in concatenated list format
            if stat_type == "player":
                self._setup_player_results_list(data, stat_name)
            elif stat_type == "team":
                self._setup_team_results_list(data, stat_name)
            
        except Exception as e:
            print(f"ERROR in _display_stat_results: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _setup_player_results_list(self, data, stat_name):
        """Setup concatenated list view for player statistics results"""
        
        def safe_float_convert(value):
            """Safely convert value to float for sorting"""
            try:
                if isinstance(value, (int, float)):
                    return float(value)
                
                value_str = str(value).strip()
                if not value_str or value_str.lower() in ['none', 'n/a', '']:
                    return 0.0
                
                # Handle fraction format like "1-1"
                if '-' in value_str and value_str.count('-') == 1:
                    parts = value_str.split('-')
                    if len(parts) == 2:
                        try:
                            return float(parts[0]) / max(1, float(parts[1]))
                        except (ValueError, ZeroDivisionError):
                            return 0.0
                
                return float(value_str)
            except (ValueError, TypeError):
                return 0.0
        
        # Convert data to proper format with numeric sorting
        converted_data = []
        for item in data:
            player_name = item.get('player_name', 'Unknown')
            team = item.get('team', '')
            value = item.get('value', '')
            
            numeric_value = safe_float_convert(value)
            converted_data.append({
                'name': f"{player_name} ({team})" if team else player_name,
                'value': numeric_value,
                'display_value': str(value)
            })
        
        # Sort by numeric value (descending for most stats)
        converted_data.sort(key=lambda x: x['value'], reverse=True)
        
        # Populate the list with rank
        for rank, item in enumerate(converted_data, 1):
            list_text = f"{rank} {item['name']} {item['display_value']}"
            list_item = QListWidgetItem(list_text)
            self.results_list.addItem(list_item)
        
        # Set focus to first item in results list
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)
            self.results_list.setFocus()  # Move focus to results list
    
    def _setup_team_results_list(self, data, stat_name):
        """Setup concatenated list view for team statistics results"""
        
        # Sort data by numeric value (descending for most stats)
        sorted_data = sorted(data, key=lambda x: x.get('value', 0), reverse=True)
        
        # Populate the list with rank
        for rank, item in enumerate(sorted_data, 1):
            team_name = item.get('name', 'Unknown')
            display_value = item.get('displayValue', str(item.get('value', '')))
            list_text = f"{rank} {team_name} {display_value}"
            list_item = QListWidgetItem(list_text)
            self.results_list.addItem(list_item)
        
        # Set focus to first item in results list
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)
            self.results_list.setFocus()  # Move focus to results list
    
    def _get_stat_categories(self):
        """Get available stat categories without loading full data"""
        # Return actual individual statistics that users want to see
        if self.league.upper() == "MLB":
            if self.stat_type == "team":
                # Show actual team stats available across all categories
                return [
                    "Batting Average", "Home Runs", "RBIs", "Runs", "Hits", "Doubles", "Triples",
                    "ERA", "Wins", "Strikeouts", "WHIP", "Saves", "Innings Pitched",
                    "Fielding Percentage", "Errors", "Double Plays"
                ]
            else:  # player
                # Based on actual ESPN player stats structure
                return [
                    "Batting Average", "Home Runs", "RBIs", "Runs", "OPS", "On Base Percentage", "Slugging Percentage",
                    "ERA", "Wins", "Strikeouts", "WHIP", "Saves", "Quality Starts", "Opponent Batting Average",
                    "Stolen Bases", "Hits", "Holds", "MLB Rating", "Average Game Score", "Wins Above Replacement"
                ]
        elif self.league.upper() == "NFL":
            if self.stat_type == "team":
                return [
                    "Total Yards", "Passing Yards", "Rushing Yards", "Points For", "Points Against",
                    "Turnovers", "Third Down Efficiency", "Red Zone Efficiency"
                ]
            else:  # player
                return [
                    "Passing Yards", "Passing TDs", "Rushing Yards", "Rushing TDs",
                    "Receiving Yards", "Receiving TDs", "Tackles", "Sacks", "Interceptions"
                ]
        elif self.league.upper() == "NBA":
            if self.stat_type == "team":
                return [
                    "Points Per Game", "Field Goal %", "Three Point %", "Free Throw %",
                    "Rebounds", "Assists", "Steals", "Blocks", "Turnovers"
                ]
            else:  # player
                return [
                    "Points Per Game", "Field Goal %", "Three Point %", "Free Throw %",
                    "Rebounds", "Assists", "Steals", "Blocks", "Minutes"
                ]
        else:
            # Generic categories for other leagues
            return ["Points", "Wins", "Goals", "Assists"] if self.stat_type == "team" else ["Points", "Goals", "Assists", "Games"]
    
    def _get_available_statistics(self):
        """Extract available statistics from the data"""
        print(f"DEBUG: _get_available_statistics called for {self.stat_type}")
        
        if not self.statistics_data:
            print(f"DEBUG: No statistics_data available")
            return []
        
        available_stats = []
        
        if self.stat_type == "player":
            player_stats = self.statistics_data.get("player_stats", [])
            print(f"DEBUG: Found {len(player_stats)} player stat categories")
            
            # Handle new MLB API format vs old ESPN format
            for i, category in enumerate(player_stats):
                # Check if this is the new MLB API format
                if 'leaders' in category and 'name' in category:
                    # New MLB API format
                    stat_name = category.get('name', 'Unknown')
                    leaders = category.get('leaders', [])
                    
                    print(f"DEBUG: MLB Category {i}: {stat_name} with {len(leaders)} leaders")
                    
                    # Convert MLB format to expected format
                    converted_leaders = []
                    for leader in leaders:
                        converted_leaders.append({
                            'player_name': leader.get('name', 'Unknown'),
                            'stat_value': leader.get('value', 0),
                            'value': leader.get('value', 0),  # Also add 'value' key for compatibility
                            'team': leader.get('team', 'N/A'),
                            'position': leader.get('position', None)
                        })
                    
                    available_stats.append({
                        'name': stat_name,
                        'category': 'MLB Stats',
                        'stat_name': stat_name,
                        'data': converted_leaders,
                        'type': 'player'
                    })
                    print(f"DEBUG: Added MLB stat: {stat_name} with {len(converted_leaders)} players")
                    
                else:
                    # Old ESPN API format
                    category_name = category.get("category", "Unknown")
                    stats_list = category.get("stats", [])
                    print(f"DEBUG: ESPN Category {i}: {category_name} with {len(stats_list)} stats")
                    
                    # Group by stat types
                    stat_types = {}
                    for stat in stats_list:
                        stat_name = stat.get("stat_name", "Unknown")
                        if stat_name not in stat_types:
                            stat_types[stat_name] = []
                        stat_types[stat_name].append(stat)
                    
                    # Add each unique stat type
                    for stat_name, stats in stat_types.items():
                        # Avoid duplicate names when category and stat name are the same
                        if stat_name.lower() == category_name.lower():
                            display_name = stat_name  # Just use the stat name
                        else:
                            display_name = f"{stat_name} ({category_name})"  # Include category for clarity
                        
                        available_stats.append({
                            'name': display_name,
                            'category': category_name,
                            'stat_name': stat_name,
                            'data': stats,
                            'type': 'player'
                        })
                        print(f"DEBUG: Added ESPN stat: {display_name} with {len(stats)} players")
        
        elif self.stat_type == "team":
            team_stats = self.statistics_data.get("team_stats", [])
            print(f"DEBUG: Found {len(team_stats)} team stat categories")
            for category in team_stats:
                category_name = category.get("category", "Unknown")
                teams_list = category.get("stats", [])
                
                if teams_list:
                    # Get all stat names from first team
                    first_team = teams_list[0]
                    team_stats_dict = first_team.get("stats", {})
                    
                    for stat_name in team_stats_dict.keys():
                        # Process the teams data for this specific stat
                        teams_data = []
                        for team_info in teams_list:
                            team_name = team_info.get("team_name", "Unknown")
                            team_stats_dict = team_info.get("stats", {})
                            
                            if stat_name in team_stats_dict:
                                stat_value = team_stats_dict[stat_name]
                                
                                # Try to convert to numeric for sorting
                                numeric_value = 0
                                try:
                                    numeric_value = float(stat_value)
                                except (ValueError, TypeError):
                                    pass
                                
                                teams_data.append({
                                    "name": team_name,
                                    "value": numeric_value,
                                    "displayValue": str(stat_value)
                                })
                        
                        # Sort teams by value (descending for most stats)
                        teams_data.sort(key=lambda x: x["value"], reverse=True)
                        
                        available_stats.append({
                            'name': f"{stat_name} ({category_name})",
                            'category': category_name,
                            'stat_name': stat_name,
                            'data': teams_data,  # Pre-processed data ready for display
                            'type': 'team'
                        })
                        print(f"DEBUG: Added team stat: {stat_name} ({category_name}) with {len(teams_data)} teams")
        
        print(f"DEBUG: Total available stats: {len(available_stats)}")
        return available_stats
    
    def _on_stat_selected(self, item):
        """Handle when a statistic is clicked (mouse click)"""
        print(f"DEBUG: _on_stat_selected called with item: {item}")
        if item:
            category_info = item.data(Qt.ItemDataRole.UserRole)
            print(f"DEBUG: category_info: {category_info}")
            if category_info:
                print(f"DEBUG: About to load data for category: {category_info.get('category')}")
                try:
                    # Load data on demand
                    stat_info = self._load_stat_data_for_category(category_info.get('category'))
                    if stat_info:
                        self._display_stat_results(stat_info)
                        print(f"DEBUG: _display_stat_results completed successfully")
                    else:
                        print(f"DEBUG: No stat_info returned for category")
                except Exception as e:
                    print(f"DEBUG: Exception in _on_stat_selected: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"DEBUG: No category_info found in item data")
        else:
            print(f"DEBUG: _on_stat_selected called with None item")
    
    def _on_stat_activated(self, item):
        """Handle when a statistic is activated (Enter key or double-click)"""
        print(f"DEBUG: _on_stat_activated called")
        self._on_stat_selected(item)  # Use same logic
    
    def _load_stat_data_for_category(self, category):
        """Load statistics data for a specific category on demand"""
        # Show loading message
        if hasattr(self, 'results_label'):
            self.results_label.setText(f"Loading {category}...")
        
        # Load full data if not already loaded
        if not self.statistics_data:
            try:
                print(f"DEBUG: Loading statistics data for {self.league}")
                self.statistics_data = ApiService.get_statistics(self.league)
            except Exception as e:
                print(f"DEBUG: Exception loading statistics data: {str(e)}")
                if hasattr(self, 'results_label'):
                    self.results_label.setText(f"Error loading data: {str(e)}")
                return None
        
        if not self.statistics_data:
            print(f"DEBUG: No statistics data available")
            if hasattr(self, 'results_label'):
                self.results_label.setText("No statistics data available")
            return None
        
        # Find matching statistics for the category
        return self._find_stat_for_category(category)
    
    def _find_stat_for_category(self, category):
        """Find the best matching statistic for a given category"""
        if self.stat_type == "team":
            team_stats = self.statistics_data.get("team_stats", [])
            
            # Search across all team stat categories for the specific stat
            for stat_category in team_stats:
                category_name = stat_category.get("category", "")
                teams_in_category = stat_category.get("stats", [])
                
                if teams_in_category:
                    # Get the first team's stats to see what's available
                    first_team = teams_in_category[0]
                    team_stats_dict = first_team.get("stats", {})
                    
                    # Look for the exact stat name the user wants
                    best_stat_name = None
                    
                    # Direct match
                    if category in team_stats_dict:
                        best_stat_name = category
                    else:
                        # Fuzzy matching
                        for stat_name in team_stats_dict.keys():
                            if (category.lower() in stat_name.lower() or
                                self._is_category_match(category, stat_name, stat_name)):
                                best_stat_name = stat_name
                                break
                    
                    if best_stat_name:
                        # Collect all teams' data for this stat
                        teams_data = []
                        for team_info in teams_in_category:
                            team_name = team_info.get("team_name", "Unknown")
                            team_stats_dict = team_info.get("stats", {})
                            
                            if best_stat_name in team_stats_dict:
                                stat_value = team_stats_dict[best_stat_name]
                                
                                # Try to convert to numeric for sorting
                                numeric_value = 0
                                try:
                                    numeric_value = float(stat_value)
                                except (ValueError, TypeError):
                                    # Keep as string, use 0 for sorting
                                    pass
                                
                                teams_data.append({
                                    "name": team_name,
                                    "value": numeric_value,
                                    "displayValue": str(stat_value)
                                })
                        
                        if teams_data:
                            # Sort teams by value (descending for most stats)
                            teams_data.sort(key=lambda x: x["value"], reverse=True)
                            
                            return {
                                'name': f"{best_stat_name}",
                                'category': category,
                                'stat_name': best_stat_name,
                                'data': teams_data,
                                'type': 'team'
                            }
        
        else:  # player stats
            player_stats = self.statistics_data.get("player_stats", [])
            
            # Player stats structure: [{'category': name, 'stats': [{'player_name': name, 'team': team, 'value': value, 'stat_name': stat}]}]
            for stat_category in player_stats:
                category_name = stat_category.get("category", "")
                stats_list = stat_category.get("stats", [])
                
                if not stats_list:
                    continue
                
                # Check if this category matches what we're looking for
                if (category.lower() in category_name.lower() or
                    self._is_category_match(category, category_name, category_name)):
                    
                    # All stats in this category should be the same stat type
                    # Just use the data as-is since it's already in the right format
                    players_data = []
                    for stat in stats_list:
                        player_name = stat.get("player_name", "Unknown")
                        stat_value = stat.get("value", "")
                        
                        # Try to convert to numeric for sorting
                        numeric_value = 0
                        try:
                            # Handle fraction format like "1-1" 
                            if '-' in str(stat_value) and str(stat_value).count('-') == 1:
                                parts = str(stat_value).split('-')
                                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                                    numeric_value = int(parts[0]) / max(1, int(parts[1]))  # Avoid division by zero
                                else:
                                    numeric_value = float(stat_value)
                            else:
                                numeric_value = float(stat_value)
                        except (ValueError, TypeError):
                            # Keep as 0 for sorting if can't convert
                            pass
                        
                        players_data.append({
                            "name": f"{player_name} ({stat.get('team', 'N/A')})",
                            "value": numeric_value,
                            "displayValue": str(stat_value)
                        })
                    
                    if players_data:
                        # Sort players by value (descending for most stats)
                        players_data.sort(key=lambda x: x["value"], reverse=True)
                        
                        return {
                            'name': f"{category_name}",
                            'category': category,
                            'stat_name': category_name,
                            'data': players_data,
                            'type': 'player'
                        }
        
        # If no exact match found, return None
        print(f"DEBUG: No matching stat found for category: {category}")
        return None
    
    def _is_category_match(self, category, stat_name, stat_display_name):
        """Check if a category matches a statistic using fuzzy matching"""
        category_lower = category.lower()
        stat_name_lower = stat_name.lower()
        stat_display_lower = stat_display_name.lower()
        
        # Define mapping for common statistics
        category_mappings = {
            "batting average": ["avg", "average", "batting"],
            "home runs": ["hr", "homerun", "home run"],
            "rbis": ["rbi", "runs batted in"],
            "runs": ["run", "r"],
            "hits": ["hit", "h"],
            "stolen bases": ["sb", "steal", "stolen"],
            "era": ["era", "earned run average"],
            "wins": ["win", "w"],
            "strikeouts": ["so", "k", "strikeout"],
            "whip": ["whip", "walks hits innings"],
            "saves": ["save", "sv"],
            "innings pitched": ["ip", "inning"],
            "passing yards": ["passing", "pass yards"],
            "rushing yards": ["rushing", "rush yards"],
            "receiving yards": ["receiving", "rec yards"],
            "touchdowns": ["td", "touchdown"],
            "points per game": ["ppg", "points"],
            "field goal": ["fg", "field goal"],
            "assists": ["ast", "assist"],
            "rebounds": ["reb", "rebound"],
            "steals": ["stl", "steal"],
            "blocks": ["blk", "block"]
        }
        
        # Check if category has specific mappings
        if category_lower in category_mappings:
            for mapping in category_mappings[category_lower]:
                if mapping in stat_name_lower or mapping in stat_display_lower:
                    return True
        
        return False
    
    def _show_stat_definitions(self):
        """Show statistics definitions dialog"""
        definitions_dialog = StatDefinitionsDialog(self.league, self)
        definitions_dialog.exec()

class StatDefinitionsDialog(QDialog):
    """Dialog showing definitions of statistics for different leagues"""
    
    def __init__(self, league, parent=None):
        super().__init__(parent)
        self.league = league
        self.setWindowTitle(f"{league} Statistics Definitions")
        self.resize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"{self.league} Statistics Definitions")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Browse definitions for statistical categories:")
        layout.addWidget(instructions)
        
        # Definitions list
        self.definitions_list = QListWidget()
        self.definitions_list.setAccessibleName("Statistics Definitions")
        
        # Populate definitions
        definitions = self._get_stat_definitions()
        for stat_name, definition in definitions.items():
            item_text = f"{stat_name}: {definition}"
            item = QListWidgetItem(item_text)
            self.definitions_list.addItem(item)
        
        layout.addWidget(self.definitions_list)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def _get_stat_definitions(self):
        """Get statistics definitions for the current league"""
        if self.league.upper() == "MLB":
            return {
                "AVG (Batting Average)": "Hits divided by at bats. Measures how often a batter gets a hit.",
                "HR (Home Runs)": "Number of hits that allow the batter to circle all bases and score.",
                "RBI (Runs Batted In)": "Number of runs that scored as a result of the batter's action.",
                "R (Runs)": "Number of times a player crosses home plate to score.",
                "H (Hits)": "Number of times a batter safely reaches base via a hit.",
                "SB (Stolen Bases)": "Number of bases stolen by advancing while the ball is in play.",
                "ERA (Earned Run Average)": "Average number of earned runs allowed per 9 innings pitched.",
                "W (Wins)": "Number of games won by a pitcher (must be pitcher of record).",
                "K/SO (Strikeouts)": "Number of batters struck out by a pitcher.",
                "WHIP": "Walks plus hits divided by innings pitched. Lower is better.",
                "SV (Saves)": "Number of times a relief pitcher preserved a lead for the win.",
                "IP (Innings Pitched)": "Number of complete innings pitched (outs divided by 3).",
                "OBP (On-Base %)": "Percentage of plate appearances reaching base safely.",
                "SLG (Slugging %)": "Total bases divided by at bats. Measures power hitting.",
                "OPS": "On-base percentage plus slugging percentage. Overall offensive measure."
            }
        elif self.league.upper() == "NFL":
            return {
                "Passing Yards": "Total yards gained through forward passes.",
                "Passing TDs": "Number of touchdown passes thrown by a quarterback.",
                "Rushing Yards": "Total yards gained by running with the football.",
                "Rushing TDs": "Number of touchdowns scored by running the ball.",
                "Receiving Yards": "Total yards gained from catching passes.",
                "Receiving TDs": "Number of touchdowns scored by catching passes.",
                "Tackles": "Number of times a defensive player brings down the ball carrier.",
                "Sacks": "Number of times the quarterback is tackled behind the line.",
                "Interceptions": "Number of passes caught by the opposing defense.",
                "Completion %": "Percentage of pass attempts that were completed.",
                "QBR (Quarterback Rating)": "Composite statistic measuring quarterback performance.",
                "Total Yards": "Combined offensive yards (passing + rushing).",
                "Points For": "Total points scored by a team.",
                "Points Against": "Total points allowed by a team's defense.",
                "Turnovers": "Number of times possession was lost (fumbles + interceptions).",
                "3rd Down %": "Percentage of third down attempts converted for first downs."
            }
        elif self.league.upper() == "NBA":
            return {
                "PPG (Points Per Game)": "Average number of points scored per game.",
                "FG% (Field Goal %)": "Percentage of field goal attempts made.",
                "3P% (Three Point %)": "Percentage of three-point attempts made.",
                "FT% (Free Throw %)": "Percentage of free throw attempts made.",
                "RPG (Rebounds Per Game)": "Average number of rebounds per game.",
                "APG (Assists Per Game)": "Average number of assists per game.",
                "SPG (Steals Per Game)": "Average number of steals per game.",
                "BPG (Blocks Per Game)": "Average number of blocks per game.",
                "TOV (Turnovers)": "Number of times possession was lost.",
                "MPG (Minutes Per Game)": "Average playing time per game.",
                "PER (Player Efficiency Rating)": "Overall player productivity rating.",
                "TS% (True Shooting %)": "Shooting efficiency including free throws and 3-pointers.",
                "USG% (Usage Rate)": "Percentage of team plays used by a player.",
                "ORtg (Offensive Rating)": "Points produced per 100 possessions.",
                "DRtg (Defensive Rating)": "Points allowed per 100 possessions."
            }
        else:
            return {
                "Points": "Total points scored by team or individual player.",
                "Wins": "Number of games or matches won.",
                "Goals": "Number of goals scored (varies by sport).",
                "Assists": "Number of assists made to help teammates score.",
                "Games": "Number of games or matches played.",
                "Average": "Mean value across all games or attempts."
            }
    
    def keyPressEvent(self, event):
        """Handle Escape key to close dialog"""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)


class StatisticsDialog(QDialog):
    """Dialog for displaying league statistics with player and team stats"""
    
    def __init__(self, statistics_data: Dict, league: str, parent=None):
        super().__init__(parent)
        self.statistics_data = statistics_data
        self.league = league
        self.setWindowTitle(f"{league} Statistics")
        self.resize(900, 600)
        self.tab_widget: QTabWidget | None = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        player_stats = self.statistics_data.get("player_stats", [])
        team_stats = self.statistics_data.get("team_stats", [])
        
        if not player_stats and not team_stats:
            layout.addWidget(QLabel(f"No statistics data available for {self.league}."))
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.accept)
            layout.addWidget(close_btn)
            self.setLayout(layout)
            return
        
        # Create tab widget for Player/Team separation
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Statistics")
        self.tab_widget.setAccessibleDescription("Statistics data with player and team tabs. Use Left/Right arrow keys to navigate tabs.")
        self.tab_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Add Player Statistics tab
        if player_stats:
            player_widget = self._create_player_stats_widget(player_stats)
            self.tab_widget.addTab(player_widget, "Player Statistics")
        
        # Add Team Statistics tab  
        if team_stats:
            team_widget = self._create_team_stats_widget(team_stats)
            self.tab_widget.addTab(team_widget, "Team Statistics")
        
        layout.addWidget(self.tab_widget)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Set focus
        QTimer.singleShot(100, lambda: self.tab_widget.setFocus())
    
    def _create_player_stats_widget(self, player_stats: List) -> QWidget:
        """Create widget for player statistics using accessible tables"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        if not player_stats:
            layout.addWidget(QLabel("No player statistics available."))
            widget.setLayout(layout)
            return widget
        
        # Create a tab widget for different player stat categories
        category_tabs = QTabWidget()
        category_tabs.setAccessibleName("Player Statistics Categories")
        category_tabs.setAccessibleDescription("Statistics organized by category. Use Ctrl+Tab to switch between categories.")
        
        for category in player_stats:
            category_name = category.get("category", "Unknown")
            stats_list = category.get("stats", [])
            
            if not stats_list:
                continue
            
            # Create table for this category
            table = QTableWidget()
            table.setAccessibleName(f"{category_name} Statistics Table")
            table.setAccessibleDescription(f"Table showing {category_name} statistics. Use arrow keys to navigate cells.")
            
            # Set up table structure
            table.setRowCount(len(stats_list))
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Player", "Team", "Statistic", "Value"])
            
            # Enable sorting and selection
            table.setSortingEnabled(True)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setAlternatingRowColors(True)
            
            # Populate table data
            for row, stat in enumerate(stats_list):
                player_name = stat.get("player_name", "Unknown")
                team = stat.get("team", "")
                stat_name = stat.get("stat_name", "")
                value = str(stat.get("value", ""))
                
                # Create table items with accessibility info
                player_item = QTableWidgetItem(player_name)
                player_item.setToolTip(f"Player: {player_name}")
                
                team_item = QTableWidgetItem(team)
                team_item.setToolTip(f"Team: {team}")
                
                stat_item = QTableWidgetItem(stat_name)
                stat_item.setToolTip(f"Statistic: {stat_name}")
                
                value_item = QTableWidgetItem(value)
                value_item.setToolTip(f"Value: {value}")
                
                table.setItem(row, 0, player_item)
                table.setItem(row, 1, team_item)
                table.setItem(row, 2, stat_item)
                table.setItem(row, 3, value_item)
            
            # Auto-resize columns to content
            table.resizeColumnsToContents()
            
            # Add table to category tabs
            category_tabs.addTab(table, category_name)
        
        layout.addWidget(category_tabs)
        widget.setLayout(layout)
        return widget
    
    def _create_team_stats_widget(self, team_stats: List) -> QWidget:
        """Create widget for team statistics using accessible tables"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        if not team_stats:
            layout.addWidget(QLabel("Team statistics not available yet."))
            layout.addWidget(QLabel("(Feature will be enhanced in future updates)"))
            widget.setLayout(layout)
            return widget
        
        # Create a tab widget for different team stat categories
        category_tabs = QTabWidget()
        category_tabs.setAccessibleName("Team Statistics Categories")
        category_tabs.setAccessibleDescription("Team statistics organized by category. Use Ctrl+Tab to switch between categories.")
        
        for category in team_stats:
            category_name = category.get("category", "Unknown")
            teams_list = category.get("stats", [])
            
            if not teams_list:
                continue
            
            # Get all unique stat names across all teams in this category
            all_stat_names = set()
            for team_data in teams_list:
                team_stats_dict = team_data.get("stats", {})
                all_stat_names.update(team_stats_dict.keys())
            
            stat_names = sorted(list(all_stat_names))
            
            # Create table for this category
            table = QTableWidget()
            table.setAccessibleName(f"{category_name} Team Statistics Table")
            table.setAccessibleDescription(f"Table showing team {category_name} statistics. Use arrow keys to navigate cells.")
            
            # Set up table structure: Team name + all stat columns
            table.setRowCount(len(teams_list))
            table.setColumnCount(1 + len(stat_names))
            
            headers = ["Team"] + stat_names
            table.setHorizontalHeaderLabels(headers)
            
            # Enable sorting and selection
            table.setSortingEnabled(True)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setAlternatingRowColors(True)
            
            # Populate table data
            for row, team_data in enumerate(teams_list):
                team_name = team_data.get("team_name", "Unknown Team")
                team_stats_dict = team_data.get("stats", {})
                
                # Set team name in first column
                team_item = QTableWidgetItem(team_name)
                team_item.setToolTip(f"Team: {team_name}")
                table.setItem(row, 0, team_item)
                
                # Set stat values in subsequent columns
                for col, stat_name in enumerate(stat_names, 1):
                    stat_value = team_stats_dict.get(stat_name, "N/A")
                    
                    stat_item = QTableWidgetItem(str(stat_value))
                    stat_item.setToolTip(f"{team_name} {stat_name}: {stat_value}")
                    table.setItem(row, col, stat_item)
            
            # Auto-resize columns to content
            table.resizeColumnsToContents()
            
            # Add table to category tabs
            category_tabs.addTab(table, category_name)
        
        layout.addWidget(category_tabs)
        widget.setLayout(layout)
        return widget
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
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
        elif self.league in ["NCAAB", "NCAAM", "NCAAW"]:
            # College basketball conferences (major conferences first)
            division_order = ["Southeastern Conference", "Big Ten Conference", "Big 12 Conference",
                            "Atlantic Coast Conference", "Pac-12 Conference", "Big East Conference",
                            "American Conference", "Conference USA", "Mid-American Conference",
                            "Mountain West Conference", "Atlantic 10 Conference", "Missouri Valley Conference",
                            "West Coast Conference", "Ivy League", "Colonial Conference", 
                            "Southern Conference", "Ohio Valley Conference", "Big Sky Conference"]
        elif self.league == "WNBA":
            # WNBA has Eastern and Western conferences
            division_order = ["Eastern Conference", "Western Conference"]
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


class VenuesDialog(QDialog):
    """Dialog for browsing stadiums and venues by league"""
    
    def __init__(self, venues_data: Dict, league: str, parent=None):
        super().__init__(parent)
        self.venues_data = venues_data
        self.league = league
        self.setWindowTitle(f"{league} Venues")
        self.resize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header with venue count
        venue_count = len(self.venues_data)
        header_label = QLabel(f"{self.league} Stadiums and Venues ({venue_count} total)")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
        layout.addWidget(header_label)
        
        # Create list widget for venues
        self.venues_list = QListWidget()
        self.venues_list.setAccessibleName(f"{self.league} Venues List")
        self.venues_list.setAccessibleDescription(f"List of {self.league} stadiums and venues. Press Enter for detailed information.")
        self.venues_list.itemActivated.connect(self.on_venue_selected)
        
        # Sort venues by name for easier browsing
        sorted_venues = sorted(self.venues_data.values(), key=lambda x: x.get('name', ''))
        
        # Add venues to list with summary info
        for venue in sorted_venues:
            venue_name = venue.get('name', 'Unknown Venue')
            city = venue.get('city', 'Unknown')
            state = venue.get('state', 'Unknown')
            
            # Add visual indicators for venue characteristics
            indicators = []
            if venue.get('indoor'):
                indicators.append("Indoor")
            else:
                indicators.append("Outdoor")
            
            if venue.get('grass') is True:
                indicators.append("Grass")
            elif venue.get('grass') is False:
                indicators.append("Turf")
            else:
                indicators.append("Unknown Surface")
            
            # Show home teams if available
            home_teams = venue.get('home_teams', [])
            team_info = ""
            if home_teams:
                if len(home_teams) == 1:
                    team_info = f" - {home_teams[0].get('name', 'Unknown Team')}"
                else:
                    team_info = f" - {len(home_teams)} teams"
            
            # Format: "Stadium Name (City, State) [Indoor, Grass] - Team Name" 
            surface_info = " | ".join(indicators)
            display_text = f"{venue_name} ({city}, {state}) [{surface_info}]{team_info}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, venue)
            self.venues_list.addItem(item)
        
        layout.addWidget(self.venues_list)
        
        # Add close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        
        layout.addLayout(close_layout)
        self.setLayout(layout)
        
        # Set focus to venues list
        self.venues_list.setFocus()
        if self.venues_list.count() > 0:
            self.venues_list.setCurrentRow(0)
    
    def on_venue_selected(self, item):
        """Show detailed venue information dialog"""
        venue_data = item.data(Qt.ItemDataRole.UserRole)
        if not venue_data:
            return
        
        # Get detailed venue information
        venue_id = venue_data.get('id')
        league_key = self.league.lower()
        venue_details = venue_service.get_venue_details(venue_id, league_key)
        
        if not venue_details:
            QMessageBox.information(self, "Venue Details", "No detailed information available for this venue.")
            return
        
        # Show venue details dialog
        details_dialog = VenueDetailsDialog(venue_details, self)
        details_dialog.exec()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        super().keyPressEvent(event)


class VenueDetailsDialog(QDialog):
    """Dialog showing detailed information about a specific venue"""
    
    def __init__(self, venue_details: Dict, parent=None):
        super().__init__(parent)
        self.venue_details = venue_details
        basic_info = venue_details.get('basic_info', {})
        venue_name = basic_info.get('name', 'Unknown Venue')
        self.setWindowTitle(f"{venue_name} - Details")
        self.resize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create list widget for venue details
        self.details_list = QListWidget()
        
        # Get venue information sections
        basic_info = self.venue_details.get('basic_info', {})
        characteristics = self.venue_details.get('characteristics', {})
        home_teams = self.venue_details.get('home_teams', [])
        interesting_facts = self.venue_details.get('interesting_facts', [])
        media = self.venue_details.get('media', {})
        images = media.get('images', [])
        
        # Venue name header
        venue_name = basic_info.get('name', 'Unknown Venue')
        self.details_list.addItem(QListWidgetItem(f"=== {venue_name} ==="))
        self.details_list.addItem(QListWidgetItem(""))
        
        # Basic Information Section
        self.details_list.addItem(QListWidgetItem("--- Basic Information ---"))
        if basic_info.get('city') and basic_info.get('state'):
            self.details_list.addItem(QListWidgetItem(f"Location: {basic_info['city']}, {basic_info['state']}"))
        if basic_info.get('league'):
            self.details_list.addItem(QListWidgetItem(f"League: {basic_info['league']}"))
        if basic_info.get('zip_code'):
            self.details_list.addItem(QListWidgetItem(f"ZIP Code: {basic_info['zip_code']}"))
        self.details_list.addItem(QListWidgetItem(""))
        
        # Characteristics Section
        if characteristics:
            self.details_list.addItem(QListWidgetItem("--- Stadium Characteristics ---"))
            if characteristics.get('indoor') is not None:
                venue_type = "Indoor stadium" if characteristics['indoor'] else "Outdoor stadium"
                self.details_list.addItem(QListWidgetItem(f"Type: {venue_type}"))
            
            if characteristics.get('grass') is not None:
                if characteristics['grass']:
                    self.details_list.addItem(QListWidgetItem("Playing Surface: Natural grass"))
                else:
                    self.details_list.addItem(QListWidgetItem("Playing Surface: Artificial turf"))
            
            if characteristics.get('capacity'):
                try:
                    capacity = int(characteristics['capacity'])
                    self.details_list.addItem(QListWidgetItem(f"Capacity: {capacity:,} fans"))
                except (ValueError, TypeError):
                    self.details_list.addItem(QListWidgetItem(f"Capacity: {characteristics['capacity']}"))
            self.details_list.addItem(QListWidgetItem(""))
        
        # Home Teams Section
        if home_teams:
            self.details_list.addItem(QListWidgetItem("--- Home Teams ---"))
            for team in home_teams:
                team_name = team.get('name', 'Unknown Team')
                team_abbrev = team.get('abbreviation', '')
                if team_abbrev:
                    self.details_list.addItem(QListWidgetItem(f"{team_name} ({team_abbrev})"))
                else:
                    self.details_list.addItem(QListWidgetItem(team_name))
            self.details_list.addItem(QListWidgetItem(""))
        
        # Interesting Facts Section
        if interesting_facts:
            self.details_list.addItem(QListWidgetItem("--- Interesting Facts ---"))
            for fact in interesting_facts:
                self.details_list.addItem(QListWidgetItem(f"• {fact}"))
            self.details_list.addItem(QListWidgetItem(""))
        
        # Images Section
        if images:
            self.details_list.addItem(QListWidgetItem("--- Available Media ---"))
            self.details_list.addItem(QListWidgetItem(f"{len(images)} high-quality images available"))
            # Show first few image types for information
            for i, img in enumerate(images[:3]):
                rel_info = ", ".join(img.get('rel', []))
                if rel_info:
                    self.details_list.addItem(QListWidgetItem(f"  • {rel_info.title()} view"))
            
            if len(images) > 3:
                self.details_list.addItem(QListWidgetItem(f"  • ... and {len(images) - 3} more"))
        
        layout.addWidget(self.details_list)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        
        layout.addLayout(close_layout)
        self.setLayout(layout)
    
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
        
        # Initialize window title tracking
        self.base_title = "Sports Scores"
        self.current_context = []  # Stack for building breadcrumb-style titles
        
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
    
    def open_league(self, league: str, week: int = None):
        """Open a league view, optionally for a specific week (football)"""
        try:
            self._push_to_stack("home", None)
            league_view = LeagueView(self, league, week=week)
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

    def open_audio_tutorial(self):
        """Open audio tutorial view"""
        try:
            self._push_to_stack("home", None)
            audio_tutorial_view = AudioTutorialView(self)
            self._switch_to_view(audio_tutorial_view, "audio_tutorial", None)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open audio tutorial: {e}")

    def open_baseball_audio_tutorial(self):
        """Open baseball audio tutorial view"""
        try:
            self._push_to_stack("audio_tutorial", None)
            baseball_tutorial_view = BaseballAudioTutorialView(self)
            self._switch_to_view(baseball_tutorial_view, "baseball_tutorial", None)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open baseball audio tutorial: {e}")

    def open_football_audio_tutorial(self):
        """Open football audio tutorial view"""
        try:
            self._push_to_stack("audio_tutorial", None)
            football_tutorial_view = FootballAudioTutorialView(self)
            self._switch_to_view(football_tutorial_view, "football_tutorial", None)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open football audio tutorial: {e}")

    def open_game_details(self, game_id: str, from_live_scores=False):
        """Open game details view"""
        try:
            # Track where we came from for proper navigation
            if from_live_scores:
                self._push_to_stack("live_scores", None)
            else:
                self._push_to_stack("league", self.current_league if hasattr(self, 'current_league') else None)
            gdv = GameDetailsView(self, getattr(self, 'current_league', None), game_id, None)
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

    def update_window_title(self, context_items=None):
        """Update window title with breadcrumb-style context for accessibility
        
        Args:
            context_items: List of context items from most specific to most general
                          e.g., ["Standings", "MLB"] -> "MLB, Standings - Sports Scores"
                          e.g., ["Yankees vs Red Sox", "MLB"] -> "Yankees vs Red Sox - MLB - Sports Scores"
        """
        if not context_items:
            # Just show base title
            self.setWindowTitle(self.base_title)
            return
            
        # Build title following the pattern: most specific, then general context, then base
        if len(context_items) == 1:
            # Single context item: "{Context} - Sports Scores"
            title = f"{context_items[0]} - {self.base_title}"
        else:
            # Multiple context items: reverse order for breadcrumb
            # Most specific first, then increasingly general
            breadcrumb_parts = list(reversed(context_items))
            title = f"{', '.join(breadcrumb_parts)} - {self.base_title}"
            
        self.setWindowTitle(title)

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
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Sports Scores Application - View live scores, standings, and team information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scores                    Launch home screen
  scores --live             Launch directly to Live Scores view (shorthand)
  scores --live-scores      Launch directly to Live Scores view (all sports)
  scores --mlb              Launch directly to MLB games
  scores --nfl              Launch directly to NFL games  
  scores --mlb-teams        Launch directly to MLB teams view
  scores --nfl-standings    Launch directly to NFL standings view
        """)
    
    # Create mutually exclusive group for sports
    sports_group = parser.add_mutually_exclusive_group()
    
    # Live Scores view (all sports)
    sports_group.add_argument('--live-scores', action='store_true', help='Launch directly to Live Scores view (all sports)')
    sports_group.add_argument('--live', action='store_true', help='Launch directly to Live Scores view (shorthand for --live-scores)')
    
    # Sports game views
    sports_group.add_argument('--mlb', action='store_true', help='Launch to MLB games view')
    sports_group.add_argument('--nfl', action='store_true', help='Launch to NFL games view') 
    sports_group.add_argument('--nba', action='store_true', help='Launch to NBA games view')
    sports_group.add_argument('--wnba', action='store_true', help='Launch to WNBA games view')
    sports_group.add_argument('--nhl', action='store_true', help='Launch to NHL games view')
    sports_group.add_argument('--ncaaf', action='store_true', help='Launch to NCAA Football games view')
    sports_group.add_argument('--ncaam', action='store_true', help='Launch to NCAA Men\'s Basketball games view')
    sports_group.add_argument('--ncaawb', action='store_true', help='Launch to NCAA Women\'s Basketball games view')
    
    # Teams views
    sports_group.add_argument('--mlb-teams', action='store_true', help='Launch to MLB teams view')
    sports_group.add_argument('--nfl-teams', action='store_true', help='Launch to NFL teams view')
    sports_group.add_argument('--nba-teams', action='store_true', help='Launch to NBA teams view')
    sports_group.add_argument('--wnba-teams', action='store_true', help='Launch to WNBA teams view')
    sports_group.add_argument('--nhl-teams', action='store_true', help='Launch to NHL teams view')
    sports_group.add_argument('--ncaaf-teams', action='store_true', help='Launch to NCAA Football teams view')
    sports_group.add_argument('--ncaam-teams', action='store_true', help='Launch to NCAA Men\'s Basketball teams view')
    sports_group.add_argument('--ncaawb-teams', action='store_true', help='Launch to NCAA Women\'s Basketball teams view')
    
    # Standings views
    sports_group.add_argument('--mlb-standings', action='store_true', help='Launch to MLB standings view')
    sports_group.add_argument('--nfl-standings', action='store_true', help='Launch to NFL standings view')
    sports_group.add_argument('--nba-standings', action='store_true', help='Launch to NBA standings view')
    sports_group.add_argument('--wnba-standings', action='store_true', help='Launch to WNBA standings view')
    sports_group.add_argument('--nhl-standings', action='store_true', help='Launch to NHL standings view')
    sports_group.add_argument('--ncaaf-standings', action='store_true', help='Launch to NCAA Football standings view')
    sports_group.add_argument('--ncaam-standings', action='store_true', help='Launch to NCAA Men\'s Basketball standings view')
    sports_group.add_argument('--ncaawb-standings', action='store_true', help='Launch to NCAA Women\'s Basketball standings view')
    
    args = parser.parse_args()
    
    # Determine startup parameters
    startup_params = None
    
    # Check for live scores view (both --live-scores and --live)
    if getattr(args, 'live_scores', False) or getattr(args, 'live', False):
        startup_params = {'action': 'live_scores'}
    
    # Check for league game views
    for sport in ['mlb', 'nfl', 'nba', 'wnba', 'nhl', 'ncaaf', 'ncaam', 'ncaawb']:
        if getattr(args, sport, False):
            startup_params = {'action': 'league', 'league': sport.upper()}
            break
    
    # Check for teams views
    if not startup_params:
        for sport in ['mlb', 'nfl', 'nba', 'wnba', 'nhl', 'ncaaf', 'ncaam', 'ncaawb']:
            if getattr(args, f'{sport}_teams', False):
                startup_params = {'action': 'teams', 'league': sport.upper()}
                break
    
    # Check for standings views  
    if not startup_params:
        for sport in ['mlb', 'nfl', 'nba', 'wnba', 'nhl', 'ncaaf', 'ncaam', 'ncaawb']:
            if getattr(args, f'{sport}_standings', False):
                startup_params = {'action': 'standings', 'league': sport.upper()}
                break
    
    # Launch the application
    app = QApplication(sys.argv)
    window = SportsScoresApp(startup_params=startup_params)
    sys.exit(app.exec())
