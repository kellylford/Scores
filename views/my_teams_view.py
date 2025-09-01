"""
My Teams View - Displays games for favorite teams
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add project root to sys.path if running as script
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QLabel, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from services.favorite_teams_manager import favorite_teams_manager
from services.api_service import ApiService
from exceptions import ApiError
from timezone_utils import convert_espn_time_to_local


class MyTeamsView(QWidget):
    """View for displaying games from favorite teams"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # UI components
        self.game_list = None
        self.mode_combo = None
        self.status_label = None
        self.configure_button = None
        
        # Data
        self.current_games = []
        self.current_mode = "live"  # "live", "past", "future"
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_F5:
            self.refresh()
        elif event.key() == Qt.Key.Key_Escape:
            # Go back to home
            if self.parent_app and hasattr(self.parent_app, 'go_back'):
                self.parent_app.go_back()
        else:
            super().keyPressEvent(event)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("My Teams")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Configure button
        self.configure_button = QPushButton("Configure Teams")
        self.configure_button.setAccessibleName("Configure favorite teams")
        self.configure_button.setAccessibleDescription("Open dialog to add or remove favorite teams")
        self.configure_button.clicked.connect(self._open_configuration)
        header_layout.addWidget(self.configure_button)
        
        self.layout.addLayout(header_layout)
        
        # Mode selection (for non-live games)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("View Mode:"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Live Games", "Past Games", "Future Games"])
        self.mode_combo.setAccessibleName("Game display mode")
        self.mode_combo.setAccessibleDescription("Select whether to show live, past, or future games")
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        
        mode_layout.addStretch()
        self.layout.addLayout(mode_layout)
        
        # Status label
        self.status_label = QLabel()
        self.layout.addWidget(self.status_label)
        
        # Games list
        self.game_list = QListWidget()
        self.game_list.setAccessibleName("My Teams Games List")
        self.game_list.setAccessibleDescription("List of games for your favorite teams")
        self.game_list.itemActivated.connect(self._on_game_selected)
        self.layout.addWidget(self.game_list)
        
        # Initial load
        self._check_favorites_and_load()
    
    def on_show(self):
        """Called when the view is shown"""
        if self.parent_app:
            self.parent_app.update_window_title(["My Teams"])
        self.refresh()
    
    def refresh(self):
        """Refresh the games list"""
        self._load_games()
    
    def _check_favorites_and_load(self):
        """Check if favorites exist and load games or show configuration"""
        favorites = favorite_teams_manager.get_favorites()
        if not favorites:
            # No favorites - show configuration dialog
            self._show_initial_setup()
        else:
            self._load_games()
    
    def _show_initial_setup(self):
        """Show initial setup guidance and open configuration"""
        msg = QMessageBox()
        msg.setWindowTitle("My Teams Setup")
        msg.setText("Welcome to My Teams!")
        msg.setInformativeText("You haven't selected any favorite teams yet. "
                             "Would you like to configure your favorite teams now?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self._open_configuration()
        else:
            self._update_status("No favorite teams configured. Click 'Configure Teams' to get started.")
    
    def _open_configuration(self):
        """Open the team configuration dialog"""
        try:
            # Import here to avoid circular imports
            from dialogs.team_configuration_dialog import TeamConfigurationDialog
            
            dialog = TeamConfigurationDialog(self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                # Refresh after configuration changes
                self.refresh()
        except ImportError:
            QMessageBox.critical(self, "Error", "Team configuration dialog not available yet.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open configuration: {e}")
    
    def _on_mode_changed(self, mode_text: str):
        """Handle mode combo box changes"""
        mode_map = {
            "Live Games": "live",
            "Past Games": "past", 
            "Future Games": "future"
        }
        self.current_mode = mode_map.get(mode_text, "live")
        self._load_games()
    
    def _load_games(self):
        """Load games for favorite teams based on current mode"""
        try:
            self._update_status("Loading games...")
            
            favorites = favorite_teams_manager.get_favorites()
            if not favorites:
                self._update_status("No favorite teams configured.")
                self.game_list.clear()
                return
            
            # Group favorites by league for efficient API calls
            leagues = {}
            for fav in favorites:
                if fav.league not in leagues:
                    leagues[fav.league] = []
                leagues[fav.league].append(fav)
            
            # Load games for each league
            all_games = []
            teams_without_games = []
            
            for league, league_favs in leagues.items():
                try:
                    league_games = self._load_league_games(league, league_favs)
                    if league_games:
                        all_games.extend(league_games)
                    else:
                        # Add teams without games to separate list
                        teams_without_games.extend(league_favs)
                except Exception as e:
                    print(f"[WARNING] Failed to load {league} games: {e}")
                    teams_without_games.extend(league_favs)
            
            # Sort games by date/time
            all_games.sort(key=self._get_game_sort_key)
            
            # Display games
            self._display_games(all_games, teams_without_games)
            
        except Exception as e:
            self._update_status(f"Error loading games: {e}")
    
    def _load_league_games(self, league: str, favorites: List) -> List[Dict]:
        """Load games for a specific league and filter for favorite teams"""
        try:
            # Get all games for the league
            games = ApiService.get_scores(league)
            
            # Create set of favorite team IDs for efficient lookup
            fav_team_ids = {fav.team_id for fav in favorites}
            
            # Filter games based on mode and favorite teams
            filtered_games = []
            
            for game in games:
                # Check if any team in the game is a favorite
                home_team = game.get("home_team", {})
                away_team = game.get("away_team", {})
                
                home_id = home_team.get("id", "")
                away_id = away_team.get("id", "")
                
                if home_id in fav_team_ids or away_id in fav_team_ids:
                    # Add league info to game for display purposes
                    game["league"] = league
                    
                    # Filter by mode
                    if self._game_matches_mode(game):
                        filtered_games.append(game)
            
            return filtered_games
            
        except Exception as e:
            print(f"[WARNING] Failed to load {league} games: {e}")
            return []
    
    def _game_matches_mode(self, game: Dict) -> bool:
        """Check if game matches the current display mode"""
        status = game.get("status", {}).get("type", {}).get("name", "").lower()
        
        if self.current_mode == "live":
            # Live games are those currently in progress
            return status in ["in progress", "halftime", "delayed", "suspended"]
        elif self.current_mode == "past":
            # Past games are completed
            return status in ["final", "final/ot", "final/so"]
        elif self.current_mode == "future":
            # Future games are scheduled
            return status in ["scheduled", "postponed"]
        
        return True  # Default to show all
    
    def _get_game_sort_key(self, game: Dict):
        """Get sort key for game based on current mode"""
        try:
            date_str = game.get("date", "")
            if date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return datetime.min
        except:
            return datetime.min
    
    def _display_games(self, games: List[Dict], teams_without_games: List):
        """Display games in the list widget"""
        self.game_list.clear()
        self.current_games = games
        
        if not games and not teams_without_games:
            # No games and no favorites
            item = QListWidgetItem("No games found for your favorite teams.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.game_list.addItem(item)
            self._update_status(f"No {self.current_mode} games found.")
            return
        
        # Add games
        for game in games:
            self._add_game_item(game)
        
        # Add separator and teams without games if any
        if teams_without_games:
            if games:
                # Add separator
                sep_item = QListWidgetItem("─" * 40)
                sep_item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.game_list.addItem(sep_item)
                
                # Add header for teams without games
                header_item = QListWidgetItem("Teams with no games available:")
                header_item.setFlags(Qt.ItemFlag.NoItemFlags)
                font = header_item.font()
                font.setBold(True)
                header_item.setFont(font)
                self.game_list.addItem(header_item)
            
            # Add teams without games
            for team in teams_without_games:
                no_game_item = QListWidgetItem(f"{team.team_name} - No games available")
                no_game_item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.game_list.addItem(no_game_item)
        
        # Update status
        game_count = len(games)
        no_game_count = len(teams_without_games)
        status_parts = []
        
        if game_count > 0:
            status_parts.append(f"{game_count} {self.current_mode} game{'s' if game_count != 1 else ''}")
        
        if no_game_count > 0:
            status_parts.append(f"{no_game_count} team{'s' if no_game_count != 1 else ''} with no games")
        
        if status_parts:
            self._update_status(" | ".join(status_parts))
        else:
            self._update_status("No games found.")
    
    def _add_game_item(self, game: Dict):
        """Add a game item to the list"""
        try:
            # Format game display text (similar to Live Scores format)
            home_team = game.get("home_team", {})
            away_team = game.get("away_team", {})
            status = game.get("status", {})
            league = game.get("league", "")
            
            home_name = home_team.get("display_name", "TBD")
            away_name = away_team.get("display_name", "TBD")
            
            # Format score if available
            home_score = game.get("home_score", "")
            away_score = game.get("away_score", "")
            
            if home_score and away_score:
                score_text = f"{away_name} {away_score}, {home_name} {home_score}"
            else:
                score_text = f"{away_name} @ {home_name}"
            
            # Add status and time
            status_text = status.get("type", {}).get("shortDetail", "")
            if status_text:
                display_text = f"{score_text} - {status_text}"
            else:
                display_text = score_text
            
            # Add league prefix
            if league:
                display_text = f"[{league}] {display_text}"
            
            # Create list item
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, game)
            
            self.game_list.addItem(item)
            
        except Exception as e:
            print(f"[WARNING] Failed to format game item: {e}")
            item = QListWidgetItem("Game information unavailable")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.game_list.addItem(item)
    
    def _on_game_selected(self, item: QListWidgetItem):
        """Handle game selection"""
        game_data = item.data(Qt.ItemDataRole.UserRole)
        if game_data and self.parent_app:
            game_id = game_data.get("id")
            if game_id:
                # Navigate to game details (similar to Live Scores)
                self.parent_app.open_game_details(game_id, from_live_scores=True)
    
    def _update_status(self, message: str):
        """Update the status label"""
        if self.status_label:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.status_label.setText(f"My Teams - {message} (Updated: {timestamp})")