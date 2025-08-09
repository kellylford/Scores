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
    QListWidgetItem, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

# New separated modules
from exceptions import ApiError, DataModelError
from services.api_service import ApiService
from models.game import GameData
from models.news import NewsData
from models.standings import StandingsData
from accessible_table import AccessibleTable, StandingsTable, LeadersTable, BoxscoreTable, InjuryTable

# Constants
DETAIL_FIELDS = ["boxscore", "plays", "leaders", "standings", "odds", "injuries", "broadcasts", "news", "gameInfo"]
BASEBALL_STAT_HEADERS = ["Player", "Position", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
STANDINGS_HEADERS = ["Rank", "Team", "Wins", "Losses", "Win %", "GB", "Streak", "Record"]
TEAM_SUMMARY_HEADERS = ["Team", "Statistic", "Value"]
INJURY_HEADERS = ["Player", "Position", "Team", "Status", "Type", "Details", "Return Date"]
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
    
    def keyPressEvent(self, event):
        """Handle key press events for all views"""
        if event.key() == Qt.Key.Key_F5:
            self.refresh()
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
        self.set_focus_and_select_first(self.league_list)
    
    def refresh(self):
        """Refresh the league list"""
        self.league_list.clear()
        leagues = ApiService.get_leagues()
        if not leagues:
            self._show_api_error("Failed to load leagues")
            return
        
        for league in leagues:
            self.league_list.addItem(league)
        
        self.set_focus_and_select_first(self.league_list)

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
                # Add Kitchen Sink demo for MLB when no games found
                if self.league.lower() == "mlb":
                    self.scores_list.addItem("--- Demo Game (Kitchen Sink) ---")
                    demo_item = self.scores_list.item(self.scores_list.count()-1)
                    if demo_item:
                        demo_item.setData(Qt.ItemDataRole.UserRole, "DEMO_KITCHEN_SINK")
            else:
                for game_raw in scores_data:
                    game = GameData(game_raw)
                    item_text = game.get_display_text()
                    self.scores_list.addItem(item_text)
                    list_item = self.scores_list.item(self.scores_list.count()-1)
                    if list_item:
                        list_item.setData(Qt.ItemDataRole.UserRole, game_raw.get("id"))
                # Also add demo option when there are games
                if self.league.lower() == "mlb":
                    self.scores_list.addItem("--- Demo Game (Kitchen Sink) ---")
                    demo_item = self.scores_list.item(self.scores_list.count()-1)
                    if demo_item:
                        demo_item.setData(Qt.ItemDataRole.UserRole, "DEMO_KITCHEN_SINK")
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
        self.set_focus_and_select_first(self.scores_list)
    
    def next_day(self):
        """Navigate to next day"""
        self.current_date += timedelta(days=1)
        self.load_scores()
        self.set_focus_and_select_first(self.scores_list)
    
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
        self.set_focus_and_select_first(self.scores_list)

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
        elif field_name == "kitchensink":
            # Use special Kitchen Sink dialog
            dlg = KitchenSinkDialog(field_data, self)
            dlg.exec()
            return
        
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{field_name.title()} Details")
        dlg.resize(DIALOG_WIDTH, DIALOG_HEIGHT)
        layout = QVBoxLayout()
        
        # Store reference to tab widget for F6 handling
        tab_widget_ref = None
        
        if field_name == "leaders" and isinstance(field_data, dict):
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
            # Check for demo mode - use saved data for Kitchen Sink demonstration
            if self.game_id == "DEMO_KITCHEN_SINK" and self.league.lower() == "mlb":
                raw_details = self._load_demo_kitchen_sink_data()
                if raw_details:
                    details = ApiService.extract_meaningful_game_info(raw_details)
                else:
                    # Fallback demo data
                    details = {
                        'teams': [
                            {'name': 'Pittsburgh Pirates', 'home_away': 'away', 'record': '62-59'},
                            {'name': 'Cincinnati Reds', 'home_away': 'home', 'record': '58-63'}
                        ],
                        'status': 'Final',
                        'scores': ['3', '2'],
                        'venue': 'Great American Ball Park',
                        'venue_city': 'Cincinnati',
                        'venue_state': 'OH'
                    }
                    raw_details = {
                        'rosters': [{'team': {'displayName': 'Demo Team'}, 'roster': []}],
                        'article': {'headline': 'Demo Kitchen Sink Game'},
                        'seasonseries': [{'summary': 'Demo series data'}],
                        'againstTheSpread': [{'displayName': 'Demo Team', 'record': 'Demo ATS'}],
                        'pickcenter': [{'provider': {'name': 'Demo Expert'}, 'details': 'Demo pick'}]
                    }
            else:
                raw_details = ApiService.get_game_details(self.league, self.game_id)
                details = ApiService.extract_meaningful_game_info(raw_details)
            
            # Display basic game information
            self._add_basic_game_info(details)
            
            # Show configurable details
            self._add_configurable_details(raw_details)
            
        except Exception as e:
            self._show_api_error(f"Failed to load game details: {str(e)}")
    
    def _load_demo_kitchen_sink_data(self):
        """Load saved Kitchen Sink data for demonstration"""
        import json
        import os
        
        try:
            json_file = os.path.join(os.path.dirname(__file__), "api_exploration", "game_details_401696639.json")
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading demo data: {e}")
        
        return None
    
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
        
        # Always add Kitchen Sink for ALL MLB games (for testing)
        if self.league.lower() == "mlb":
            all_available_fields.append("kitchensink")
        
        if all_available_fields:
            self.details_list.addItem("--- Additional Details ---")
            for field in all_available_fields:
                if field == "kitchensink":
                    self._add_kitchen_sink_item(raw_details)
                else:
                    value = raw_details.get(field, "N/A")
                    if value == "N/A" or not value:
                        self.details_list.addItem(f"{field}: No data available")
                    else:
                        self._add_configurable_field(field, value)
    
    def _add_configurable_field(self, field: str, value: Any):
        """Add a configurable field to the details list"""
        navigable_fields = ["standings", "leaders", "boxscore", "plays", "injuries", "news"]
        
        if field in navigable_fields:
            has_data = self._check_field_has_data(field, value)
            
            if has_data:
                item_text = f"{field.title()}"
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
        elif field == "plays" and isinstance(value, list):
            return len(value) > 0
        elif field == "injuries" and isinstance(value, list):
            return len(value) > 0
        elif field == "news" and isinstance(value, (list, dict)):
            return len(value) > 0 if isinstance(value, list) else bool(value.get("articles"))
        return False
    
    def _has_kitchen_sink_data(self, raw_details: Dict) -> bool:
        """Check if game has additional Kitchen Sink data available"""
        kitchen_sink_fields = ["rosters", "seasonseries", "article", "againstTheSpread", 
                              "pickcenter", "winprobability", "videos"]
        return any(raw_details.get(field) for field in kitchen_sink_fields)
    
    def _add_kitchen_sink_item(self, raw_details: Dict):
        """Add Kitchen Sink item to the details list"""
        item_text = "Kitchen Sink (Additional MLB Data)"
        self.details_list.addItem(item_text)
        list_item_widget = self.details_list.item(self.details_list.count() - 1)
        if list_item_widget:
            list_item_widget.setData(Qt.ItemDataRole.UserRole, {"field": "kitchensink", "data": raw_details})
    
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
        
        # Detect sport type from data structure or current league
        sport_type = self._detect_sport_type(data)
        
        # Add header info
        info_label = QLabel(f"Play-by-Play ({len(data)} plays)")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
        layout.addWidget(info_label)
        
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
        
        if sport_type == "MLB":
            self._build_baseball_tree(plays_tree, data)
        elif sport_type == "NFL":
            self._build_football_tree(plays_tree, data)
        else:
            # Default to generic organization
            self._build_generic_tree(plays_tree, data)
        
        layout.addWidget(plays_tree)
    
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
        """Build baseball-specific hierarchical tree"""
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
        
        # Build tree structure
        for period_display in sorted(inning_groups.keys(), key=lambda x: int(x.split()[0][:-2]) if x.split()[0][:-2].isdigit() else 0):
            inning_item = QTreeWidgetItem([period_display])
            inning_item.setExpanded(True)  # Expand by default
            plays_tree.addTopLevelItem(inning_item)
            
            period_data = inning_groups[period_display]
            
            # Add top half (if any plays)
            if period_data["top"]:
                # Extract inning number and create proper label
                inning_num = period_display.split()[0]  # "1st", "2nd", etc.
                top_item = QTreeWidgetItem([f"Top of the {inning_num}"])
                top_item.setExpanded(True)
                inning_item.addChild(top_item)
                self._add_baseball_plays_to_tree_group(top_item, period_data["top"])
            
            # Add bottom half (if any plays)
            if period_data["bottom"]:
                # Extract inning number and create proper label
                inning_num = period_display.split()[0]  # "1st", "2nd", etc.
                bottom_item = QTreeWidgetItem([f"Bottom of the {inning_num}"])
                bottom_item.setExpanded(True)
                inning_item.addChild(bottom_item)
                self._add_baseball_plays_to_tree_group(bottom_item, period_data["bottom"])
    
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
                    
                    # Add velocity and pitch type if available
                    if velocity and pitch_type_text:
                        enhanced_text = f"{play_text} ({velocity} mph {pitch_type_text})"
                    elif velocity:
                        enhanced_text = f"{play_text} ({velocity} mph)"
                    elif pitch_type_text:
                        enhanced_text = f"{play_text} ({pitch_type_text})"
                    
                    pitch_item = QTreeWidgetItem([f"  {enhanced_text}"])
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
            
        scroll_area = QScrollArea()
        content_widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📰 GAME ARTICLES & RECAPS"))
        
        if isinstance(article_data, dict):
            headline = article_data.get("headline", "No headline")
            article_type = article_data.get("type", "Unknown")
            description = article_data.get("description", "")
            story = article_data.get("story", "")
            
            layout.addWidget(QLabel(f"\nHeadline: {headline}"))
            layout.addWidget(QLabel(f"Type: {article_type}"))
            
            if description:
                layout.addWidget(QLabel(f"\nDescription:"))
                desc_text = QTextEdit()
                desc_text.setPlainText(description)
                desc_text.setReadOnly(True)
                desc_text.setMaximumHeight(100)
                layout.addWidget(desc_text)
            
            if story:
                layout.addWidget(QLabel(f"\nFull Article:"))
                story_text = QTextEdit()
                story_text.setPlainText(story)
                story_text.setReadOnly(True)
                layout.addWidget(story_text)
        else:
            layout.addWidget(QLabel("No article data available"))
        
        content_widget.setLayout(layout)
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        self.tab_widget.addTab(scroll_area, "Articles")
    
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
        """Handle F6 for tab navigation"""
        if event.key() == Qt.Key.Key_F6 and self.tab_widget:
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
