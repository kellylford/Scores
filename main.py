import sys
import webbrowser
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
    QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer

# New separated modules
from exceptions import ApiError, DataModelError
from services.api_service import ApiService
from models.game import GameData
from models.news import NewsData
from models.standings import StandingsData
from accessible_table import AccessibleTable, StandingsTable, LeadersTable, BoxscoreTable

# Constants
DETAIL_FIELDS = ["boxscore", "leaders", "standings", "odds", "injuries", "broadcasts", "news", "gameInfo"]
BASEBALL_STAT_HEADERS = ["Player", "Position", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
STANDINGS_HEADERS = ["Rank", "Team", "Wins", "Losses", "Win %", "GB", "Streak", "Record"]
TEAM_SUMMARY_HEADERS = ["Team", "Statistic", "Value"]
INJURY_HEADERS = ["Player", "Position", "Team", "Status", "Details"]
LEADERS_HEADERS = ["Category/Player", "Team", "Statistic", "Value"]
FOCUS_DELAY_MS = 50
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
DIALOG_WIDTH = 800
DIALOG_HEIGHT = 600
NEWS_DIALOG_WIDTH = 700
NEWS_DIALOG_HEIGHT = 500
STANDINGS_DIALOG_WIDTH = 900
STANDINGS_DIALOG_HEIGHT = 600

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

class BaseView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
    def setup_ui(self):
        pass
    def on_show(self):
        pass
    def set_focus_with_delay(self, w):
        QTimer.singleShot(FOCUS_DELAY_MS, lambda: w.setFocus())

class HomeView(BaseView):
    """Home view showing league selection"""
    
    def setup_ui(self):
        self.layout.addWidget(QLabel("Select a League:"))
        
        self.league_list = QListWidget()
        self.league_list.setAccessibleName("League Selection List")
        self.league_list.setAccessibleDescription("List of available sports leagues")
        
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
        self.set_focus_with_delay(self.league_list)

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
            if self.league == "MLB":
                self.scores_list.addItem("--- Standings ---")
                standings_item = self.scores_list.item(self.scores_list.count()-1)
                standings_item.setData(Qt.ItemDataRole.UserRole, "__standings__")  # type: ignore
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
        """Show standings dialog"""
        try:
            standings_data = ApiService.get_standings(self.league)
            if not standings_data:
                QMessageBox.information(self, "Standings", 
                                      f"No standings data available for {self.league}.")
                return
            
            dialog = StandingsDialog(standings_data, self.league, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show standings: {str(e)}")
    
    def previous_day(self):
        """Navigate to previous day"""
        self.current_date -= timedelta(days=1)
        self.load_scores()
        self.set_focus_with_delay(self.scores_list)
    
    def next_day(self):
        """Navigate to next day"""
        self.current_date += timedelta(days=1)
        self.load_scores()
        self.set_focus_with_delay(self.scores_list)
    
    def refresh(self):
        """Refresh the current view"""
        self.load_scores()
        self.set_focus_with_delay(self.scores_list)
    
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
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(refresh_btn)
        
        self.layout.addLayout(btn_layout)
    
    def _show_api_error(self, message: str):
        """Show API error message"""
        self.scores_list.clear()
        error_item = self.scores_list.addItem(f"Error: {message}")
        QMessageBox.warning(self, "API Error", message)
    
    def on_show(self):
        self.set_focus_with_delay(self.scores_list)

class GameDetailsView(BaseView):
    """View showing detailed information for a specific game"""
    
    def __init__(self, parent=None, league=None, game_id=None):
        super().__init__(parent)
        self.league = league
        self.game_id = game_id
        self.config = parent.config if parent else {}
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
        if field_name == "standings" and isinstance(field_data, list):
            # Use special standings dialog with keyboard navigation
            dlg = StandingsDetailDialog(field_data, self.league, self)
            dlg.exec()
            return
        
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{field_name.title()} Details")
        dlg.resize(DIALOG_WIDTH, DIALOG_HEIGHT)
        layout = QVBoxLayout()
        
        if field_name == "leaders" and isinstance(field_data, dict):
            self._add_leaders_data_to_layout(layout, field_data)
        elif field_name == "boxscore" and isinstance(field_data, dict):
            self._add_boxscore_data_to_layout(layout, field_data)
        elif field_name == "injuries" and isinstance(field_data, list):
            self._add_injuries_list_to_layout(layout, field_data)
        elif field_name == "news" and isinstance(field_data, list):
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
        
        # Set focus to first table after dialog is shown (for boxscore)
        if field_name == "boxscore":
            def set_focus_to_table():
                # Find all tables in the dialog
                tables = dlg.findChildren(BoxscoreTable)
                debug_items = []
                debug_items.append(f"Found {len(tables)} BoxscoreTable widgets")
                
                if tables:
                    first_table = tables[0]
                    debug_items.append(f"Setting focus to table: {first_table.accessible_name}")
                    debug_items.append(f"Table has {first_table.rowCount()} rows, {first_table.columnCount()} columns")
                    
                    first_table.setFocus()
                    if first_table.rowCount() > 0:
                        first_table.setCurrentCell(0, 0)
                        debug_items.append("Focus and cell selection set successfully")
                    else:
                        debug_items.append("Table has no rows - no data to display")
                else:
                    debug_items.append("No BoxscoreTable found - checking all QTableWidget")
                    all_tables = dlg.findChildren(QTableWidget)
                    debug_items.append(f"Found {len(all_tables)} QTableWidget total")
                
                # Show debug info in accessible list widget dialog
                debug_dlg = QDialog(dlg)
                debug_dlg.setWindowTitle("Boxscore Debug Information")
                debug_dlg.resize(500, 300)
                debug_layout = QVBoxLayout()
                
                debug_list = QListWidget()
                debug_list.setAccessibleName("Debug Information")
                debug_list.setAccessibleDescription("Debug information about boxscore table creation and focus")
                
                for item in debug_items:
                    debug_list.addItem(item)
                
                debug_layout.addWidget(debug_list)
                
                # Add copy button
                copy_debug_btn = QPushButton("Copy Debug Info")
                def copy_debug_info():
                    clipboard = QApplication.clipboard()
                    debug_text = "\n".join(debug_items)
                    clipboard.setText(debug_text)
                    copy_debug_btn.setText("Copied!")
                    QTimer.singleShot(2000, lambda: copy_debug_btn.setText("Copy Debug Info"))
                
                copy_debug_btn.clicked.connect(copy_debug_info)
                debug_layout.addWidget(copy_debug_btn)
                
                close_debug_btn = QPushButton("Close Debug")
                close_debug_btn.clicked.connect(debug_dlg.accept)
                debug_layout.addWidget(close_debug_btn)
                
                debug_dlg.setLayout(debug_layout)
                debug_list.setFocus()
                debug_dlg.exec()
            
            # Use a longer delay to ensure dialog is fully rendered
            QTimer.singleShot(300, set_focus_to_table)
        
        dlg.exec()
    
    def load_game_details(self):
        """Load detailed game information"""
        self.details_list.clear()
        
        try:
            raw_details = ApiService.get_game_details(self.league, self.game_id)
            details = ApiService.extract_meaningful_game_info(raw_details)
            
            # Display basic game information
            self._add_basic_game_info(details)
            
            # Show configurable details
            self._add_configurable_details(raw_details)
            
        except Exception as e:
            self._show_api_error(f"Failed to load game details: {str(e)}")
    
    def _add_basic_game_info(self, details: Dict):
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
        
        # Weather
        if 'weather' in details:
            weather_display = details['weather']
            if 'temperature' in details:
                weather_display += f", {details['temperature']}"
            self.details_list.addItem(f"Weather: {weather_display}")
        
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
        """Add configurable detail fields"""
        config_fields = self.config.get(self.league, [])
        config_fields = [field for field in config_fields if field in DETAIL_FIELDS]
        
        if config_fields:
            self.details_list.addItem("--- Additional Details ---")
            for field in config_fields:
                value = raw_details.get(field, "N/A")
                if value == "N/A" or not value:
                    self.details_list.addItem(f"{field}: No data available")
                else:
                    self._add_configurable_field(field, value)
    
    def _add_configurable_field(self, field: str, value: Any):
        """Add a configurable field to the details list"""
        navigable_fields = ["standings", "leaders", "boxscore", "injuries", "news"]
        
        if field in navigable_fields:
            has_data = self._check_field_has_data(field, value)
            
            if has_data:
                item_text = f"{field.title()}: Press Enter to view details"
                self.details_list.addItem(item_text)
                list_item_widget = self.details_list.item(self.details_list.count() - 1)
                if list_item_widget:
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
            return len(value) > 0 if isinstance(value, list) else bool(value.get("entries"))
        elif field == "leaders" and isinstance(value, dict):
            return len(value) > 0
        elif field == "boxscore" and isinstance(value, dict):
            return bool(value.get("teams") or value.get("players"))
        elif field == "injuries" and isinstance(value, list):
            return len(value) > 0
        elif field == "news" and isinstance(value, (list, dict)):
            return len(value) > 0 if isinstance(value, list) else bool(value.get("articles"))
        return False
    
    def open_config(self):
        """Open configuration dialog"""
        selected = self.config.get(self.league, [])
        selected = [field for field in selected if field in DETAIL_FIELDS]
        dlg = ConfigDialog(DETAIL_FIELDS, selected, self)
        if dlg.exec():
            self.config[self.league] = dlg.get_selected()
            if self.parent_app:
                self.parent_app.config = self.config
            self.load_game_details()
    
    def refresh(self):
        """Refresh the game details"""
        self.load_game_details()
        self.set_focus_with_delay(self.details_list)
    
    def _add_nav_buttons(self):
        btn_layout = QHBoxLayout()
        
        back_btn = QPushButton("Back (Alt+B)")
        back_btn.setShortcut("Alt+B")
        back_btn.clicked.connect(lambda: self.parent_app.go_back() if self.parent_app else None)
        btn_layout.addWidget(back_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(refresh_btn)
        
        config_btn = QPushButton("Config")
        config_btn.clicked.connect(self.open_config)
        btn_layout.addWidget(config_btn)
        
        self.layout.addLayout(btn_layout)
    
    def _show_api_error(self, message: str):
        """Show API error message"""
        self.details_list.clear()
        error_item = self.details_list.addItem(f"Error: {message}")
        QMessageBox.warning(self, "API Error", message)
    
    def on_show(self):
        self.set_focus_with_delay(self.details_list)
    
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
        """Add leaders data to layout"""
        if not data:
            layout.addWidget(QLabel("No leaders data available."))
            return
        
        # Create table for leaders
        table = QTableWidget()
        table.setColumnCount(len(LEADERS_HEADERS))
        table.setHorizontalHeaderLabels(LEADERS_HEADERS)
        
        # Flatten leaders data into rows
        rows = []
        for category, leaders in data.items():
            if isinstance(leaders, list):
                for leader in leaders:
                    if isinstance(leader, dict):
                        rows.append([
                            category,
                            leader.get("team", ""),
                            leader.get("name", ""),
                            leader.get("value", "")
                        ])
            elif isinstance(leaders, dict):
                rows.append([
                    category,
                    leaders.get("team", ""),
                    leaders.get("name", ""),
                    leaders.get("value", "")
                ])
        
        table.setRowCount(len(rows))
        for row, row_data in enumerate(rows):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                table.setItem(row, col, item)
        
        # Configure table
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Player name stretches
        
        layout.addWidget(table)
    
    def _add_boxscore_data_to_layout(self, layout, data):
        """Add boxscore data to layout using accessible tables"""
        if not data:
            layout.addWidget(QLabel("No boxscore data available."))
            return
        
        # Debug: Add information about what data we received
        debug_label = QLabel(f"Boxscore data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        debug_label.setStyleSheet("color: blue; font-style: italic;")
        layout.addWidget(debug_label)
        
        # Create tab widget for organized boxscore display
        tab_widget = QTabWidget()
        tab_widget.setAccessibleName("Boxscore Tabs")
        tab_widget.setAccessibleDescription("Tabbed view of team and player statistics. Use Ctrl+Tab to switch between tabs.")
        tab_widget.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        
        # Store first table for focus management
        first_table = None
        
        # Team Statistics Tab
        if "teams" in data and data["teams"]:
            # Debug: Show team data info
            team_debug_label = QLabel(f"Teams found: {len(data['teams'])}")
            team_debug_label.setStyleSheet("color: green; font-style: italic;")
            layout.addWidget(team_debug_label)
            
            team_widget = QWidget()
            team_layout = QVBoxLayout()
            
            for team_data in data["teams"]:
                team_name = team_data.get("name", "Unknown Team")
                team_stats = team_data.get("stats", {})
                
                if team_stats:
                    # Create team header
                    team_label = QLabel(f"=== {team_name} ===")
                    team_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
                    team_layout.addWidget(team_label)
                    
                    # Create team statistics table
                    team_table = BoxscoreTable(title=f"{team_name} Team Stats")
                    team_table.setup_columns(["Statistic", "Value"])
                    
                    # Debug: Confirm table creation
                    table_debug_label = QLabel(f"Created team table for {team_name}")
                    table_debug_label.setStyleSheet("color: orange; font-style: italic;")
                    team_layout.addWidget(table_debug_label)
                    
                    # Convert stats dict to table data
                    stats_data = []
                    for stat_name, stat_value in team_stats.items():
                        # Make stat names more readable
                        display_name = stat_name.replace('atBats', 'At Bats').replace('homeRuns', 'Home Runs')
                        display_name = display_name.replace('rbi', 'RBI').replace('avg', 'Batting Avg')
                        display_name = display_name.replace('strikeouts', 'Strikeouts').replace('era', 'ERA')
                        stats_data.append([display_name.title(), str(stat_value)])
                    
                    # Set focus to first table if not already set
                    set_focus_for_table = first_table is None
                    if set_focus_for_table:
                        first_table = team_table
                    
                    team_table.populate_data(stats_data, set_focus=True)  # Always set focus for the first table
                    team_layout.addWidget(team_table)
            
            team_widget.setLayout(team_layout)
            tab_widget.addTab(team_widget, "Team Stats")
        
        # Player Statistics Tab
        if "players" in data and data["players"]:
            # Debug: Show player data info
            player_debug_label = QLabel(f"Player teams found: {len(data['players'])}")
            player_debug_label.setStyleSheet("color: green; font-style: italic;")
            layout.addWidget(player_debug_label)
            
            player_widget = QWidget()
            player_layout = QVBoxLayout()
            
            for team_players in data["players"]:
                team_name = team_players.get("team", "Unknown Team")
                players = team_players.get("players", [])
                
                if players:
                    # Create team header
                    team_label = QLabel(f"=== {team_name} ===")
                    team_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
                    player_layout.addWidget(team_label)
                    
                    # Separate batters and pitchers
                    batters = [p for p in players if p.get("position", "") not in ["P", "RP", "SP", "CP"]]
                    pitchers = [p for p in players if p.get("position", "") in ["P", "RP", "SP", "CP"]]
                    
                    # Batting statistics
                    if batters:
                        batting_label = QLabel(f"--- {team_name} Batting ---")
                        batting_label.setStyleSheet("font-weight: bold; margin: 5px 0;")
                        player_layout.addWidget(batting_label)
                        
                        batting_table = BoxscoreTable(title=f"{team_name} Batting")
                        batting_headers = ["Player", "Pos", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
                        batting_table.setup_columns(batting_headers, stretch_column=0)
                        
                        # Debug: Confirm batting table creation
                        batting_debug_label = QLabel(f"Created batting table for {team_name} with {len(batters)} batters")
                        batting_debug_label.setStyleSheet("color: orange; font-style: italic;")
                        player_layout.addWidget(batting_debug_label)
                        
                        batting_data = []
                        for player in batters:
                            row = [
                                player.get("name", ""),
                                player.get("position", ""),
                                player.get("ab", "0"),
                                player.get("r", "0"),
                                player.get("h", "0"),
                                player.get("rbi", "0"),
                                player.get("bb", "0"),
                                player.get("so", "0"),
                                player.get("avg", ".000")
                            ]
                            batting_data.append(row)
                        
                        # Set focus if this is the first table and no team stats tab
                        set_focus_for_table = first_table is None
                        if set_focus_for_table:
                            first_table = batting_table
                        
                        batting_table.populate_data(batting_data, set_focus=True)  # Always set focus for first batting table
                        player_layout.addWidget(batting_table)
                    
                    # Pitching statistics
                    if pitchers:
                        pitching_label = QLabel(f"--- {team_name} Pitching ---")
                        pitching_label.setStyleSheet("font-weight: bold; margin: 5px 0;")
                        player_layout.addWidget(pitching_label)
                        
                        pitching_table = BoxscoreTable(title=f"{team_name} Pitching")
                        pitching_headers = ["Player", "IP", "H", "R", "ER", "BB", "SO", "ERA"]
                        pitching_table.setup_columns(pitching_headers, stretch_column=0)
                        
                        pitching_data = []
                        for player in pitchers:
                            row = [
                                player.get("name", ""),
                                player.get("ip", "0.0"),
                                player.get("h", "0"),
                                player.get("r", "0"),
                                player.get("er", "0"),
                                player.get("bb", "0"),
                                player.get("so", "0"),
                                player.get("era", "0.00")
                            ]
                            pitching_data.append(row)
                        
                        pitching_table.populate_data(pitching_data, set_focus=False)
                        player_layout.addWidget(pitching_table)
            
            player_widget.setLayout(player_layout)
            tab_widget.addTab(player_widget, "Player Stats")
        
        # Add the tab widget to the main layout
        layout.addWidget(tab_widget)
        
        # Configure tab widget focus and navigation
        if tab_widget.count() > 0:
            tab_widget.setCurrentIndex(0)
            
            # Connect tab change signal for proper focus management
            def on_tab_changed(index):
                current_widget = tab_widget.currentWidget()
                if current_widget:
                    tables = current_widget.findChildren(BoxscoreTable)
                    if tables:
                        # Focus on the first table in the new tab
                        QTimer.singleShot(50, lambda: tables[0].setFocus())
                        if tables[0].rowCount() > 0:
                            QTimer.singleShot(50, lambda: tables[0].setCurrentCell(0, 0))
            
            tab_widget.currentChanged.connect(on_tab_changed)

    def _add_injuries_list_to_layout(self, layout, data):
        """Add injuries list to layout"""
        if not data:
            layout.addWidget(QLabel("No injury data available."))
            return
        
        # Create injuries table
        table = QTableWidget()
        table.setColumnCount(len(INJURY_HEADERS))
        table.setHorizontalHeaderLabels(INJURY_HEADERS)
        table.setRowCount(len(data))
        
        for row, injury in enumerate(data):
            injury_data = [
                injury.get("player", ""),
                injury.get("position", ""),
                injury.get("team", ""),
                injury.get("status", ""),
                injury.get("details", "")
            ]
            
            for col, value in enumerate(injury_data):
                item = QTableWidgetItem(str(value))
                table.setItem(row, col, item)
        
        # Configure table
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Player name stretches
        
        layout.addWidget(table)
    
    def _add_news_list_to_layout(self, layout, data):
        """Add news list to layout"""
        if not data:
            layout.addWidget(QLabel("No news data available."))
            return
        
        # Handle different news data formats
        news_articles = data
        if isinstance(data, dict) and "articles" in data:
            news_articles = data["articles"]
        
        if not news_articles:
            layout.addWidget(QLabel("No news articles available."))
            return
        
        # Create list widget for news
        news_list = QListWidget()
        
        for news_item in news_articles:
            news_data = NewsData(news_item)
            display_text = news_data.get_display_text()
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, news_data)
            news_list.addItem(item)
        
        # Connect double-click to open in browser
        def open_news_item(item):
            news_data = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(news_data, NewsData) and news_data.has_web_url():
                webbrowser.open(news_data.web_url)
            else:
                QMessageBox.information(self, "No Link", "No web link available for this story.")
        
        news_list.itemDoubleClicked.connect(open_news_item)
        layout.addWidget(QLabel("Double-click a headline to open in browser:"))
        layout.addWidget(news_list)

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
            if has_divisions and self.league == "MLB":
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
        division_order = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West", "League"]
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
        
        for item in self.news_headlines:
            news = NewsData(item)
            display = news.get_display_text()
            list_item = QListWidgetItem(display)
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
            if has_divisions and self.league == "MLB":
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
        division_order = ["AL East", "AL Central", "AL West", "NL East", "NL Central", "NL West", "League"]
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

class SportsScoresApp(QWidget):
    """Main application class using QStackedWidget for better view management"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sports Scores (ESPN)")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Application state
        self.config = {}
        self.view_stack = []  # Stack for navigation history
        
        # Initialize configuration
        self._init_config()
        
        # Setup UI with stacked widget
        self.setup_ui()
        
        # Show home view initially
        self.show_home()
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
    
    def open_league(self, league: str):
        """Open a league view"""
        try:
            self._push_to_stack("home", None)
            league_view = LeagueView(self, league)
            self._switch_to_view(league_view, "league", league)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open league: {e}")

    def open_game_details(self, game_id: str):
        """Open game details view"""
        try:
            self._push_to_stack("league", self.current_league if hasattr(self, 'current_league') else None)
            gdv = GameDetailsView(self, getattr(self, 'current_league', None), game_id)
            self._switch_to_view(gdv, "game", game_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open game details: {e}")

    def go_back(self):
        if not self.view_stack:
            return
        try:
            prev = self.view_stack.pop()
            vtype, data = prev.get('type'), prev.get('data')
            if vtype == "home":
                self.show_home(); return
            if vtype == "league" and data:
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
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SportsScoresApp()
    sys.exit(app.exec())
