from typing import Any, Dict, List
import espn_api
from exceptions import ApiError

__all__ = ["ApiService"]

class ApiService:
    """Service class to wrap espn_api functions with uniform error handling."""

    @staticmethod
    def _call(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise ApiError(str(e)) from e

    @staticmethod
    def get_leagues() -> List[str]:
        return ApiService._call(espn_api.get_leagues)

    @staticmethod
    def get_scores(league: str, date) -> List[Dict]:
        return ApiService._call(espn_api.get_scores, league, date)

    @staticmethod
    def get_news(league: str) -> List[Dict]:
        return ApiService._call(espn_api.get_news, league)

    @staticmethod
    def get_standings(league: str) -> List[Dict]:
        return ApiService._call(espn_api.get_standings, league)

    @staticmethod
    def get_team_schedule(league: str, team_id: str, days_ahead: int = 30, days_behind: int = 30, season=None) -> List[Dict]:
        return ApiService._call(espn_api.get_team_schedule, league, team_id, days_ahead, days_behind, season)

    @staticmethod  
    def get_available_seasons(league: str) -> List[tuple]:
        return ApiService._call(espn_api.get_available_seasons, league)

    @staticmethod
    def get_game_details(league: str, game_id: str) -> Dict:
        return ApiService._call(espn_api.get_game_details, league, game_id)

    @staticmethod
    def extract_meaningful_game_info(details: Dict) -> Dict:
        return ApiService._call(espn_api.extract_meaningful_game_info, details)

    @staticmethod
    def format_complex_data(key: str, value: Any) -> str:
        return ApiService._call(espn_api.format_complex_data, key, value)

    @staticmethod
    def get_live_scores_all_sports() -> List[Dict]:
        return ApiService._call(espn_api.get_live_scores_all_sports)

    @staticmethod
    def get_statistics(league: str) -> Dict:
        return ApiService._call(espn_api.get_statistics, league)
