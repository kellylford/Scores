"""
Team Configuration Dialog - Multi-tab interface for selecting favorite teams
"""

import sys
import os
from typing import List, Dict, Optional

# Add project root to sys.path if running as script
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QListWidget, 
    QListWidgetItem, QPushButton, QLabel, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from services.favorite_teams_manager import favorite_teams_manager
from services.api_service import ApiService
from exceptions import ApiError


class TeamListWidget(QListWidget):
    """Custom list widget for team selection with space key toggle"""
    
    def __init__(self, league: str, parent=None):
        super().__init__(parent)
        self.league = league
        self.parent_dialog = parent
        self.teams_data = []
        
        # Setup accessibility
        self.setAccessibleName(f"{league} Teams List")
        self.setAccessibleDescription(f"List of {league} teams. Press Space to toggle favorite status.")
        
        # Load teams
        self._load_teams()
    
    def keyPressEvent(self, event):
        """Handle space key for toggling favorites"""
        if event.key() == Qt.Key.Key_Space:
            self._toggle_current_item()
        else:
            super().keyPressEvent(event)
    
    def _load_teams(self):
        """Load teams for this league"""
        try:
            # Get team data from API (we'll need to get this from standings or games)
            standings = ApiService.get_standings(self.league)
            
            # Extract team information
            teams = []
            for standing in standings:
                if isinstance(standing, dict):
                    team = standing.get("team", {})
                    if team:
                        teams.append({
                            "id": team.get("id", ""),
                            "name": team.get("displayName", team.get("name", "Unknown")),
                            "abbreviation": team.get("abbreviation", "")
                        })
            
            # Sort teams alphabetically
            teams.sort(key=lambda t: t["name"])
            self.teams_data = teams
            
            # Populate list
            self._populate_list()
            
        except Exception as e:
            print(f"[WARNING] Failed to load {self.league} teams: {e}")
            # Add error item
            error_item = QListWidgetItem(f"Failed to load {self.league} teams")
            error_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.addItem(error_item)
    
    def _populate_list(self):
        """Populate the list with teams"""
        self.clear()
        
        for team in self.teams_data:
            team_id = team["id"]
            team_name = team["name"]
            
            # Check if team is a favorite
            is_favorite = favorite_teams_manager.is_favorite(team_id)
            
            # Format display text
            if is_favorite:
                display_text = f"Favorite - {team_name}"
            else:
                display_text = team_name
            
            # Create list item
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, team)
            
            # Visual indication for favorites (could use icons in future)
            if is_favorite:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            
            self.addItem(item)
    
    def _toggle_current_item(self):
        """Toggle favorite status of currently selected item"""
        current_item = self.currentItem()
        if not current_item:
            return
        
        team_data = current_item.data(Qt.ItemDataRole.UserRole)
        if not team_data:
            return
        
        team_id = team_data["id"]
        team_name = team_data["name"]
        
        # Check if we can add more favorites
        if not favorite_teams_manager.is_favorite(team_id) and not favorite_teams_manager.can_add_more():
            QMessageBox.warning(
                self, 
                "Favorite Limit Reached",
                f"You can only have {favorite_teams_manager.MAX_TEAMS} favorite teams.\n"
                "Please remove some favorites before adding more."
            )
            return
        
        # Toggle favorite status
        is_now_favorite = favorite_teams_manager.toggle_favorite(team_id, team_name, self.league)
        
        # Update display
        if is_now_favorite:
            display_text = f"Favorite - {team_name}"
            font = current_item.font()
            font.setBold(True)
            current_item.setFont(font)
        else:
            display_text = team_name
            font = current_item.font()
            font.setBold(False)
            current_item.setFont(font)
        
        current_item.setText(display_text)
        
        # Notify parent dialog to update favorite count
        if self.parent_dialog:
            self.parent_dialog._update_favorite_count()
    
    def refresh(self):
        """Refresh the team list"""
        self._populate_list()


class FavoriteTeamsTab(QWidget):
    """Tab showing all current favorite teams"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_dialog = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Header
        self.layout.addWidget(QLabel("Current Favorite Teams:"))
        
        # Favorites list
        self.favorites_list = QListWidget()
        self.favorites_list.setAccessibleName("Current Favorite Teams")
        self.favorites_list.setAccessibleDescription("List of your current favorite teams. Press Delete to remove a team.")
        self.layout.addWidget(self.favorites_list)
        
        # Remove button
        button_layout = QHBoxLayout()
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setAccessibleDescription("Remove the selected team from favorites")
        self.remove_button.clicked.connect(self._remove_selected)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.setAccessibleDescription("Remove all teams from favorites")
        self.clear_all_button.clicked.connect(self._clear_all)
        button_layout.addWidget(self.clear_all_button)
        
        self.layout.addLayout(button_layout)
        
        # Enable delete key
        self.favorites_list.keyPressEvent = self._list_key_press
        
        # Load favorites
        self.refresh()
    
    def _list_key_press(self, event):
        """Handle key press events for the favorites list"""
        if event.key() == Qt.Key.Key_Delete:
            self._remove_selected()
        else:
            QListWidget.keyPressEvent(self.favorites_list, event)
    
    def refresh(self):
        """Refresh the favorites list"""
        self.favorites_list.clear()
        
        favorites = favorite_teams_manager.get_favorites()
        if not favorites:
            item = QListWidgetItem("No favorite teams selected")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.favorites_list.addItem(item)
            self.remove_button.setEnabled(False)
            self.clear_all_button.setEnabled(False)
        else:
            # Group by league
            by_league = {}
            for fav in favorites:
                if fav.league not in by_league:
                    by_league[fav.league] = []
                by_league[fav.league].append(fav)
            
            # Add teams grouped by league
            for league in sorted(by_league.keys()):
                league_teams = by_league[league]
                
                # League header
                header_item = QListWidgetItem(f"--- {league} ---")
                header_item.setFlags(Qt.ItemFlag.NoItemFlags)
                font = header_item.font()
                font.setBold(True)
                header_item.setFont(font)
                self.favorites_list.addItem(header_item)
                
                # Teams in this league
                for fav in sorted(league_teams, key=lambda f: f.team_name):
                    item = QListWidgetItem(fav.team_name)
                    item.setData(Qt.ItemDataRole.UserRole, fav)
                    self.favorites_list.addItem(item)
            
            self.remove_button.setEnabled(True)
            self.clear_all_button.setEnabled(True)
    
    def _remove_selected(self):
        """Remove the selected favorite team"""
        current_item = self.favorites_list.currentItem()
        if not current_item:
            return
        
        fav_data = current_item.data(Qt.ItemDataRole.UserRole)
        if not fav_data:
            return
        
        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Remove Favorite",
            f"Remove {fav_data.team_name} from your favorites?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            favorite_teams_manager.remove_favorite(fav_data.team_id)
            self.refresh()
            
            # Update parent dialog
            if self.parent_dialog:
                self.parent_dialog._update_favorite_count()
                self.parent_dialog._refresh_all_tabs()
    
    def _clear_all(self):
        """Clear all favorite teams"""
        favorites = favorite_teams_manager.get_favorites()
        if not favorites:
            return
        
        reply = QMessageBox.question(
            self,
            "Clear All Favorites",
            f"Remove all {len(favorites)} favorite teams?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            favorite_teams_manager.clear_all_favorites()
            self.refresh()
            
            # Update parent dialog
            if self.parent_dialog:
                self.parent_dialog._update_favorite_count()
                self.parent_dialog._refresh_all_tabs()


class TeamConfigurationDialog(QDialog):
    """Multi-tab dialog for configuring favorite teams"""
    
    SUPPORTED_LEAGUES = ["NFL", "MLB", "NCAAF"]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Favorite Teams")
        self.setModal(True)
        self.resize(600, 500)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Header with favorite count
        self.count_label = QLabel()
        self.count_label.setAccessibleName("Favorite team count")
        layout.addWidget(self.count_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.team_tabs = {}
        
        # League tabs
        for league in self.SUPPORTED_LEAGUES:
            team_list = TeamListWidget(league, self)
            self.team_tabs[league] = team_list
            self.tab_widget.addTab(team_list, f"{league} Teams")
        
        # Favorites tab
        self.favorites_tab = FavoriteTeamsTab(self)
        self.tab_widget.addTab(self.favorites_tab, "Favorite Teams")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.setAccessibleDescription("Save current favorite team configuration")
        self.save_button.clicked.connect(self._save_configuration)
        button_layout.addWidget(self.save_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initial update
        self._update_favorite_count()
    
    def _update_favorite_count(self):
        """Update the favorite count display"""
        count = favorite_teams_manager.get_favorite_count()
        remaining = favorite_teams_manager.get_remaining_slots()
        
        self.count_label.setText(
            f"Favorite Teams: {count}/{favorite_teams_manager.MAX_TEAMS} "
            f"({remaining} remaining)"
        )
    
    def _refresh_all_tabs(self):
        """Refresh all team tabs"""
        for tab in self.team_tabs.values():
            tab.refresh()
        self.favorites_tab.refresh()
    
    def _save_configuration(self):
        """Save the current configuration"""
        try:
            # Configuration is already saved automatically when teams are toggled
            # This is just for confirmation
            count = favorite_teams_manager.get_favorite_count()
            
            if count == 0:
                reply = QMessageBox.question(
                    self,
                    "No Favorites Selected",
                    "You haven't selected any favorite teams. Continue anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return
            
            QMessageBox.information(
                self,
                "Configuration Saved",
                f"Saved {count} favorite team{'s' if count != 1 else ''}."
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_F1:
            self._show_help()
        else:
            super().keyPressEvent(event)
    
    def _show_help(self):
        """Show help information"""
        help_text = """
Team Configuration Help:

• Use the league tabs (NFL, MLB, NCAAF) to browse teams
• Press SPACE on a team to add/remove it from favorites
• Use the "Favorite Teams" tab to see all your selections
• Maximum 20 favorite teams allowed
• Press F1 to show this help
• Press ESC to cancel
        """.strip()
        
        QMessageBox.information(self, "Help", help_text)