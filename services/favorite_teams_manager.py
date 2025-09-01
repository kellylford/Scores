"""
Favorite Teams Manager - Handles favorite team configuration and persistence
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from exceptions import DataModelError


@dataclass
class FavoriteTeam:
    """Data class representing a favorite team"""
    team_id: str
    team_name: str
    league: str
    added_date: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "league": self.league,
            "added_date": self.added_date
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "FavoriteTeam":
        """Create from dictionary for JSON deserialization"""
        return cls(
            team_id=data["team_id"],
            team_name=data["team_name"],
            league=data["league"],
            added_date=data["added_date"]
        )


class FavoriteTeamsManager:
    """Manages favorite teams configuration and persistence"""
    
    MAX_TEAMS = 20
    CONFIG_VERSION = "1.0"
    
    def __init__(self):
        self.favorites: List[FavoriteTeam] = []
        self._config_file = self._get_config_file_path()
        self.load_favorites()
    
    def _get_config_file_path(self) -> str:
        """Get the path to the favorite teams configuration file"""
        # Store in the same directory as the executable/script
        app_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level from services/ to the main app directory
        app_dir = os.path.dirname(app_dir)
        return os.path.join(app_dir, "favorite_teams.json")
    
    def load_favorites(self) -> None:
        """Load favorite teams from JSON file"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Validate version
                if data.get("version") != self.CONFIG_VERSION:
                    print(f"[WARNING] Config version mismatch. Expected {self.CONFIG_VERSION}, got {data.get('version')}")
                
                # Load favorites
                self.favorites = []
                for fav_data in data.get("favorites", []):
                    try:
                        favorite = FavoriteTeam.from_dict(fav_data)
                        self.favorites.append(favorite)
                    except (KeyError, TypeError) as e:
                        print(f"[WARNING] Skipping invalid favorite team data: {e}")
            else:
                # No config file exists yet
                self.favorites = []
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"[WARNING] Failed to load favorites config: {e}")
            self.favorites = []
    
    def save_favorites(self) -> None:
        """Save favorite teams to JSON file"""
        try:
            data = {
                "version": self.CONFIG_VERSION,
                "favorites": [fav.to_dict() for fav in self.favorites]
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise DataModelError(f"Failed to save favorites: {e}")
    
    def add_favorite(self, team_id: str, team_name: str, league: str) -> bool:
        """Add a team to favorites. Returns True if added, False if at limit"""
        # Check if already a favorite
        if self.is_favorite(team_id):
            return True  # Already added
        
        # Check limit
        if len(self.favorites) >= self.MAX_TEAMS:
            return False
        
        # Add new favorite
        favorite = FavoriteTeam(
            team_id=team_id,
            team_name=team_name,
            league=league,
            added_date=datetime.now().isoformat()
        )
        self.favorites.append(favorite)
        self.save_favorites()
        return True
    
    def remove_favorite(self, team_id: str) -> bool:
        """Remove a team from favorites. Returns True if removed, False if not found"""
        for i, favorite in enumerate(self.favorites):
            if favorite.team_id == team_id:
                del self.favorites[i]
                self.save_favorites()
                return True
        return False
    
    def is_favorite(self, team_id: str) -> bool:
        """Check if a team is in favorites"""
        return any(fav.team_id == team_id for fav in self.favorites)
    
    def get_favorites(self) -> List[FavoriteTeam]:
        """Get all favorite teams"""
        return self.favorites.copy()
    
    def get_favorites_by_league(self, league: str) -> List[FavoriteTeam]:
        """Get favorite teams for a specific league"""
        return [fav for fav in self.favorites if fav.league == league]
    
    def get_favorite_count(self) -> int:
        """Get number of favorite teams"""
        return len(self.favorites)
    
    def get_remaining_slots(self) -> int:
        """Get number of remaining favorite team slots"""
        return self.MAX_TEAMS - len(self.favorites)
    
    def can_add_more(self) -> bool:
        """Check if more teams can be added to favorites"""
        return len(self.favorites) < self.MAX_TEAMS
    
    def toggle_favorite(self, team_id: str, team_name: str, league: str) -> bool:
        """Toggle favorite status of a team. Returns True if now favorite, False if removed"""
        if self.is_favorite(team_id):
            self.remove_favorite(team_id)
            return False
        else:
            return self.add_favorite(team_id, team_name, league)
    
    def clear_all_favorites(self) -> None:
        """Remove all favorite teams"""
        self.favorites = []
        self.save_favorites()


# Global instance
favorite_teams_manager = FavoriteTeamsManager()