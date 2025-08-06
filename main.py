import sys
import webbrowser
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel,
    QHBoxLayout, QCheckBox, QDialog, QMessageBox, QTextEdit, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QSplitter, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer
import espn_api

# Constants
DETAIL_FIELDS = ["boxscore", "leaders", "standings", "odds", "injuries", "broadcasts", "news", "gameInfo"]
DEFAULT_CONFIG_FIELDS = ["name", "status", "competitors"]
BASEBALL_STAT_HEADERS = ["Player", "Position", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
STANDINGS_HEADERS = ["Rank", "Team", "Wins", "Losses", "Win %", "GB", "Streak", "Record"]
TEAM_SUMMARY_HEADERS = ["Team", "Statistic", "Value"]
INJURY_HEADERS = ["Player", "Position", "Team", "Status", "Details"]
LEADERS_HEADERS = ["Category/Player", "Team", "Statistic", "Value"]

# UI timing constants
FOCUS_DELAY_MS = 50
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
DIALOG_WIDTH = 800
DIALOG_HEIGHT = 600
NEWS_DIALOG_WIDTH = 700
NEWS_DIALOG_HEIGHT = 500
STANDINGS_DIALOG_WIDTH = 900
STANDINGS_DIALOG_HEIGHT = 600

class ApiError(Exception):
    """Custom exception for API-related errors"""
    pass

class DataModelError(Exception):
    """Custom exception for data model parsing errors"""
    pass

class ApiService:
    """Service class to handle all ESPN API interactions with error handling"""
    
    @staticmethod
    def safe_api_call(func, *args, **kwargs):
        """Wrapper for API calls with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"API Error: {str(e)}"
            print(f"[ERROR] {error_msg}")  # Log to console
            raise ApiError(error_msg)
    
    @staticmethod
    def get_leagues() -> List[str]:
        """Get available leagues with error handling"""
        try:
            return ApiService.safe_api_call(espn_api.get_leagues)
        except ApiError:
            return []  # Return empty list on error
    
    @staticmethod
    def get_scores(league: str, date) -> List[Dict]:
        """Get scores for a league and date with error handling"""
        try:
            return ApiService.safe_api_call(espn_api.get_scores, league, date)
        except ApiError:
            return []
    
    @staticmethod
    def get_news(league: str) -> List[Dict]:
        """Get news for a league with error handling"""
        try:
            return ApiService.safe_api_call(espn_api.get_news, league)
        except ApiError:
            return []
    
    @staticmethod
    def get_standings(league: str) -> List[Dict]:
        """Get standings for a league with error handling"""
        try:
            return ApiService.safe_api_call(espn_api.get_standings, league)
        except ApiError:
            return []
    
    @staticmethod
    def get_game_details(league: str, game_id: str) -> Dict:
        """Get game details with error handling"""
        try:
            return ApiService.safe_api_call(espn_api.get_game_details, league, game_id)
        except ApiError:
            return {}
    
    @staticmethod
    def extract_meaningful_game_info(raw_details: Dict) -> Dict:
        """Extract meaningful game info with error handling"""
        try:
            return ApiService.safe_api_call(espn_api.extract_meaningful_game_info, raw_details) or {}
        except ApiError:
            return {}

class GameData:
    """Data model for game information"""
    
    def __init__(self, raw_data: Dict):
        self.raw_data = raw_data
        self.id = raw_data.get("id", "")
        self.name = raw_data.get("name", "Unknown Game")
        self.teams = raw_data.get("teams", [])
        self.start_time = raw_data.get("start_time", "")
    
    def get_display_text(self) -> str:
        """Get formatted display text for the game"""
        display = self.name
        
        # Add scores if available
        if self.teams:
            team_scores = []
            for team in self.teams:
                if team.get("score"):
                    team_scores.append(f"{team['abbreviation']} {team['score']}")
            if team_scores:
                display += f" ({' - '.join(team_scores)})"
        
        # Add timing/status info
        if self.start_time:
            if not any(team.get("score") for team in self.teams):
                display += f" - {self.start_time}"
            else:
                display += f" - {self.start_time}"
        
        return display
    
    def has_scores(self) -> bool:
        """Check if the game has scores available"""
        return any(team.get("score") for team in self.teams)

class NewsData:
    """Data model for news articles"""
    
    def __init__(self, raw_data: Union[Dict, str]):
        if isinstance(raw_data, dict):
            self.headline = raw_data.get("headline", "No headline")
            self.byline = raw_data.get("byline", "")
            self.description = raw_data.get("description", "")
            self.published = raw_data.get("published", "")
            self.web_url = raw_data.get("web_url", raw_data.get("links", {}).get("web", {}).get("href", ""))
        else:
            # Handle legacy string format
            self.headline = str(raw_data)
            self.byline = ""
            self.description = ""
            self.published = ""
            self.web_url = ""
    
    def get_display_text(self) -> str:
        """Get formatted display text for the news item"""
        display_text = self.headline
        
        if self.byline:
            display_text += f"\nBy: {self.byline}"
        
        if self.published:
            try:
                if "T" in self.published:
                    date_obj = datetime.fromisoformat(self.published.replace("Z", "+00:00"))
                    formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")
                    display_text += f"\nPublished: {formatted_date}"
                else:
                    display_text += f"\nPublished: {self.published}"
            except:
                display_text += f"\nPublished: {self.published}"
        
        if self.description:
            preview = self.description[:150] + "..." if len(self.description) > 150 else self.description
            display_text += f"\n{preview}"
        
        return display_text
    
    def has_web_url(self) -> bool:
        """Check if the news item has a web URL"""
        return bool(self.web_url)

class StandingsData:
    """Data model for team standings"""
    
    def __init__(self, raw_data: List[Dict]):
        self.raw_data = raw_data
        self.teams = self._parse_teams(raw_data)
    
    def _parse_teams(self, data: List[Dict]) -> List[Dict]:
        """Parse team standings data from various ESPN formats"""
        teams = []
        
        # Handle different ESPN data structures
        data_to_process = data
        if isinstance(data, dict):
            if "entries" in data:
                data_to_process = data["entries"]
            elif "children" in data:
                data_to_process = data["children"]
            else:
                for key, value in data.items():
                    if isinstance(value, list) and value:
                        data_to_process = value
                        break
        
        if not isinstance(data_to_process, list):
            return teams
        
        for team_data in data_to_process:
            if isinstance(team_data, dict):
                team = team_data.get("team", {})
                name = team.get("displayName", team.get("name", team.get("abbreviation", "Unknown")))
                
                stats = team_data.get("stats", [])
                record = team_data.get("record", "")
                
                # Initialize stat values
                parsed_team = {
                    "name": name,
                    "wins": "N/A",
                    "losses": "N/A",
                    "win_pct": "N/A",
                    "games_behind": "N/A",
                    "streak": "N/A",
                    "record": record
                }
                
                # Extract stats from various possible formats
                if isinstance(stats, list):
                    for stat in stats:
                        if isinstance(stat, dict):
                            stat_name = stat.get("name", "").lower()
                            value = stat.get("value", stat.get("displayValue", ""))
                            if "wins" in stat_name or stat_name == "w":
                                parsed_team["wins"] = str(value)
                            elif "losses" in stat_name or stat_name == "l":
                                parsed_team["losses"] = str(value)
                            elif "winpercent" in stat_name or "pct" in stat_name:
                                parsed_team["win_pct"] = str(value)
                            elif "gamesbehind" in stat_name or stat_name == "gb":
                                parsed_team["games_behind"] = str(value)
                            elif "streak" in stat_name:
                                parsed_team["streak"] = str(value)
                elif isinstance(stats, dict):
                    parsed_team["wins"] = str(stats.get("wins", stats.get("w", "N/A")))
                    parsed_team["losses"] = str(stats.get("losses", stats.get("l", "N/A")))
                    parsed_team["win_pct"] = str(stats.get("winPercent", stats.get("pct", "N/A")))
                    parsed_team["games_behind"] = str(stats.get("gamesBehind", stats.get("gb", "N/A")))
                    parsed_team["streak"] = str(stats.get("streak", "N/A"))
                
                # If we don't have individual stats, try to parse record string
                if parsed_team["wins"] == "N/A" and parsed_team["losses"] == "N/A" and record:
                    if "-" in str(record):
                        parts = str(record).split("-")
                        if len(parts) >= 2:
                            parsed_team["wins"] = parts[0].strip()
                            parsed_team["losses"] = parts[1].strip()
                
                # Set display record
                if not parsed_team["record"]:
                    if parsed_team["wins"] != "N/A" and parsed_team["losses"] != "N/A":
                        parsed_team["record"] = f"{parsed_team['wins']}-{parsed_team['losses']}"
                    else:
                        parsed_team["record"] = "N/A"
                
                teams.append(parsed_team)
        
        return teams

class ConfigDialog(QDialog):
    def __init__(self, details, selected, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Game Details")
        self.layout = QVBoxLayout()
        self.checkboxes = {}
        for detail in details:
            cb = QCheckBox(detail)
            cb.setChecked(detail in selected)
            self.layout.addWidget(cb)
            self.checkboxes[detail] = cb
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        self.layout.addWidget(btn)
        self.setLayout(self.layout)
    
    def get_selected(self):
        return [d for d, cb in self.checkboxes.items() if cb.isChecked()]

class BaseView(QWidget):
    """Base class for all views in the application"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
    
    def setup_ui(self):
        """Override this method to setup the UI"""
        pass
    
    def on_show(self):
        """Called when the view is shown"""
        pass
    
    def set_focus_with_delay(self, widget):
        """Set focus on a widget after a short delay"""
        QTimer.singleShot(FOCUS_DELAY_MS, lambda: widget.setFocus())

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
            self._show_news_dialog()
        elif data == "__standings__":
            self._show_standings_dialog()
        else:
            # Open game details
            game_id = data
            if self.parent_app:
                self.parent_app.open_game_details(game_id)
    
    def load_scores(self):
        """Load scores for the current date"""
        self.scores_list.clear()
        
        # Update date label
        date_str = self.current_date.strftime("%A, %B %d, %Y")
        self.date_label.setText(f"Date: {date_str}")
        
        try:
            # Get scores and news
            scores_data = ApiService.get_scores(self.league, self.current_date)
            self.news_headlines = ApiService.get_news(self.league)
            
            # Process scores
            if not scores_data:
                self.scores_list.addItem(f"No games scheduled for {date_str}")
            else:
                for score_data in scores_data:
                    game = GameData(score_data)
                    display_text = game.get_display_text()
                    
                    item = self.scores_list.addItem(display_text)
                    list_item = self.scores_list.item(self.scores_list.count()-1)
                    list_item.setData(Qt.ItemDataRole.UserRole, game.id)
            
            # Add news entry
            if self.news_headlines:
                news_count = len(self.news_headlines)
                self.scores_list.addItem(f"--- News ({news_count} stories) ---")
                news_item = self.scores_list.item(self.scores_list.count()-1)
                news_item.setData(Qt.ItemDataRole.UserRole, "__news__")
            
            # Add standings entry for MLB
            if self.league == "MLB":
                self.scores_list.addItem("--- Standings ---")
                standings_item = self.scores_list.item(self.scores_list.count()-1)
                standings_item.setData(Qt.ItemDataRole.UserRole, "__standings__")
        
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
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{field_name.title()} Details")
        dlg.resize(DIALOG_WIDTH, DIALOG_HEIGHT)
        layout = QVBoxLayout()
        
        if field_name == "standings" and isinstance(field_data, list):
            self._add_standings_table_to_layout(layout, field_data)
        elif field_name == "leaders" and isinstance(field_data, dict):
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
                formatted_data = ApiService.safe_api_call(espn_api.format_complex_data, field_name, field_data)
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
                    formatted_value = ApiService.safe_api_call(espn_api.format_complex_data, field, value)
                    self.details_list.addItem(f"{field}: {formatted_value}")
                except ApiError:
                    self.details_list.addItem(f"{field}: Error formatting data")
        else:
            # Use enhanced formatting for simple data
            try:
                formatted_value = ApiService.safe_api_call(espn_api.format_complex_data, field, value)
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
        
        # Create table
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
                team_data["streak"],
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
        """Add boxscore data to layout"""
        if not data:
            layout.addWidget(QLabel("No boxscore data available."))
            return
        
        # Create scrollable area for boxscore
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Add team summaries if available
        if "teams" in data:
            for team_data in data["teams"]:
                team_name = team_data.get("name", "Unknown Team")
                scroll_layout.addWidget(QLabel(f"=== {team_name} ==="))
                
                # Create team summary table
                if "stats" in team_data:
                    team_table = QTableWidget()
                    team_table.setColumnCount(len(TEAM_SUMMARY_HEADERS))
                    team_table.setHorizontalHeaderLabels(TEAM_SUMMARY_HEADERS)
                    
                    stats = team_data["stats"]
                    team_table.setRowCount(len(stats))
                    
                    for row, (stat_name, stat_value) in enumerate(stats.items()):
                        team_table.setItem(row, 0, QTableWidgetItem(team_name))
                        team_table.setItem(row, 1, QTableWidgetItem(str(stat_name)))
                        team_table.setItem(row, 2, QTableWidgetItem(str(stat_value)))
                    
                    team_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                    team_table.verticalHeader().setVisible(False)
                    team_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                    scroll_layout.addWidget(team_table)
        
        # Add player statistics if available
        if "players" in data:
            scroll_layout.addWidget(QLabel("=== Player Statistics ==="))
            for team_players in data["players"]:
                team_name = team_players.get("team", "Unknown Team")
                scroll_layout.addWidget(QLabel(f"--- {team_name} ---"))
                
                players = team_players.get("players", [])
                if players:
                    # Create player stats table
                    player_table = QTableWidget()
                    player_table.setColumnCount(len(BASEBALL_STAT_HEADERS))
                    player_table.setHorizontalHeaderLabels(BASEBALL_STAT_HEADERS)
                    player_table.setRowCount(len(players))
                    
                    for row, player in enumerate(players):
                        player_stats = [
                            player.get("name", ""),
                            player.get("position", ""),
                            player.get("ab", ""),
                            player.get("r", ""),
                            player.get("h", ""),
                            player.get("rbi", ""),
                            player.get("bb", ""),
                            player.get("so", ""),
                            player.get("avg", "")
                        ]
                        
                        for col, stat in enumerate(player_stats):
                            item = QTableWidgetItem(str(stat))
                            player_table.setItem(row, col, item)
                    
                    player_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                    player_table.verticalHeader().setVisible(False)
                    player_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                    scroll_layout.addWidget(player_table)
        
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
    
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
            
            item = QListWidget.QListWidgetItem(display_text)
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
        else:
            # Create news list
            news_list = QListWidget()
            news_list.setAccessibleName("News Headlines List")
            news_list.setAccessibleDescription("List of news headlines - double-click to open in browser")
            
            for i, news_item in enumerate(self.news_headlines):
                news_data = NewsData(news_item)
                display_text = news_data.get_display_text()
                
                item = QListWidget.QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, news_data)
                item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Article {i+1}: {news_data.headline}")
                
                # Make it visually distinct
                font = item.font()
                font.setPointSize(font.pointSize() + 1)
                item.setFont(font)
                
                news_list.addItem(item)
            
            # Connect double-click to open story
            news_list.itemDoubleClicked.connect(self._open_news_story)
            
            layout.addWidget(QLabel("Double-click a headline to open the full story in your browser:"))
            layout.addWidget(news_list)
            
            # Add buttons
            btn_layout = QHBoxLayout()
            
            open_btn = QPushButton("Open Selected Story")
            open_btn.clicked.connect(lambda: self._open_selected_news_story(news_list))
            btn_layout.addWidget(open_btn)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.accept)
            btn_layout.addWidget(close_btn)
            
            layout.addLayout(btn_layout)
            
            # Set initial focus
            news_list.setFocus()
        
        self.setLayout(layout)
    
    def _open_news_story(self, item):
        """Open a news story in the default web browser"""
        news_data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(news_data, NewsData) and news_data.has_web_url():
            webbrowser.open(news_data.web_url)
        else:
            QMessageBox.information(self, "No Link", "No web link available for this story.")
    
    def _open_selected_news_story(self, news_list):
        """Open the currently selected news story"""
        current_item = news_list.currentItem()
        if current_item:
            self._open_news_story(current_item)
        else:
            QMessageBox.information(self, "No Selection", "Please select a news story first.")

class StandingsDialog(QDialog):
    """Dialog for displaying team standings"""
    
    def __init__(self, standings_data: List, league: str, parent=None):
        super().__init__(parent)
        self.standings_data = StandingsData(standings_data)
        self.league = league
        self.setWindowTitle(f"{league} Standings")
        self.resize(STANDINGS_DIALOG_WIDTH, STANDINGS_DIALOG_HEIGHT)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        if not self.standings_data.teams:
            layout.addWidget(QLabel(f"No standings data available for {self.league}."))
        else:
            # Create accessible table
            table = QTableWidget()
            table.setColumnCount(len(STANDINGS_HEADERS))
            table.setHorizontalHeaderLabels(STANDINGS_HEADERS)
            table.setRowCount(len(self.standings_data.teams))
            
            # Populate table
            for row, team_data in enumerate(self.standings_data.teams):
                rank = str(row + 1)
                
                # Set table items with accessibility descriptions
                items_data = [
                    (rank, f"Rank {rank}"),
                    (team_data["name"], f"Team: {team_data['name']}"),
                    (team_data["wins"], f"Wins: {team_data['wins']}"),
                    (team_data["losses"], f"Losses: {team_data['losses']}"),
                    (team_data["win_pct"], f"Win percentage: {team_data['win_pct']}"),
                    (team_data["games_behind"], f"Games behind: {team_data['games_behind']}"),
                    (team_data["streak"], f"Streak: {team_data['streak']}"),
                    (team_data["record"], f"Record: {team_data['record']}")
                ]
                
                for col, (value, accessible_text) in enumerate(items_data):
                    item = QTableWidgetItem(str(value))
                    item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, accessible_text)
                    table.setItem(row, col, item)
            
            # Make table accessible
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.verticalHeader().setVisible(False)
            
            # Auto-resize columns
            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Team name stretches
            
            layout.addWidget(QLabel(f"Current {self.league} Standings:"))
            layout.addWidget(table)
            
            # Set focus to table
            table.setFocus()
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

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
        """Initialize configuration with error handling"""
        try:
            leagues = ApiService.get_leagues()
            for league in leagues:
                self.config[league] = list(DEFAULT_CONFIG_FIELDS)
        except Exception as e:
            print(f"[WARNING] Failed to initialize config: {e}")
            # Continue with empty config - will be handled gracefully
    
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
            # Save current view to stack
            self._push_to_stack("home", None)
            
            league_view = LeagueView(self, league)
            self._switch_to_view(league_view, "league", league)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open league {league}: {str(e)}")
    
    def open_game_details(self, game_id: str):
        """Open game details view"""
        try:
            # Get current league from current view
            current_view = self.stacked_widget.currentWidget()
            if isinstance(current_view, LeagueView):
                league = current_view.league
                self._push_to_stack("league", league)
                
                details_view = GameDetailsView(self, league, game_id)
                self._switch_to_view(details_view, "game_details", game_id)
            else:
                QMessageBox.warning(self, "Error", "Cannot open game details: no league context")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open game details: {str(e)}")
    
    def go_back(self):
        """Navigate back to the previous view"""
        if not self.view_stack:
            return
        
        try:
            view_type, data = self.view_stack.pop()
            
            if view_type == "home":
                self.show_home()
            elif view_type == "league":
                self._show_league_view(data)
            else:
                print(f"[WARNING] Unknown view type in stack: {view_type}")
                self.show_home()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to navigate back: {str(e)}")
            self.show_home()
    
    def _show_league_view(self, league: str):
        """Show league view without adding to stack"""
        league_view = LeagueView(self, league)
        self._switch_to_view(league_view, "league", league)
    
    def _switch_to_view(self, view: BaseView, view_type: str, data: Any):
        """Switch to a new view"""
        # Clear the stacked widget
        while self.stacked_widget.count():
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        # Add and show the new view
        self.stacked_widget.addWidget(view)
        self.stacked_widget.setCurrentWidget(view)
        
        # Call the view's on_show method
        view.on_show()
    
    def _push_to_stack(self, view_type: str, data: Any):
        """Push current view info to navigation stack"""
        self.view_stack.append((view_type, data))
    
    def keyPressEvent(self, event):
        """Handle global keyboard shortcuts"""
        try:
            if event.key() == Qt.Key.Key_Escape:
                self.go_back()
            elif event.modifiers() == Qt.KeyboardModifier.AltModifier:
                current_view = self.stacked_widget.currentWidget()
                if isinstance(current_view, LeagueView):
                    if event.key() == Qt.Key.Key_P:
                        current_view.previous_day()
                    elif event.key() == Qt.Key.Key_N:
                        current_view.next_day()
                    elif event.key() == Qt.Key.Key_B:
                        self.go_back()
                    else:
                        super().keyPressEvent(event)
                elif event.key() == Qt.Key.Key_B:
                    self.go_back()
                else:
                    super().keyPressEvent(event)
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"[ERROR] Error in keyPressEvent: {e}")
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SportsScoresApp()
    sys.exit(app.exec())
