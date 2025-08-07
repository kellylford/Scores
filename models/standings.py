from typing import Any, Dict, List

class StandingsData:
    """Data model for team standings"""
    def __init__(self, raw_data: List[Dict]):
        self.raw_data = raw_data
        self.teams = self._parse_teams(raw_data)
        self.divisions = self._organize_by_divisions()

    def _parse_teams(self, data: List[Dict]) -> List[Dict]:
        teams: List[Dict] = []
        if not data:
            return teams
        for entry in data:
            if not isinstance(entry, dict):
                continue
            name = entry.get("team_name") or entry.get("name") or entry.get("displayName") or entry.get("abbreviation", "Unknown")
            wins = entry.get("wins") if isinstance(entry.get("wins"), (int, str)) else entry.get("record", "0-0").split("-")[0]
            losses = entry.get("losses") if isinstance(entry.get("losses"), (int, str)) else entry.get("record", "0-0").split("-")[-1]
            win_pct = entry.get("win_percentage") or entry.get("win_pct") or entry.get("winPercent") or entry.get("pct") or "0.000"
            gb = entry.get("games_back") or entry.get("games_behind") or entry.get("gb") or "—"
            division = entry.get("division", "League")
            streak = entry.get("streak", "")
            record = entry.get("record") or f"{wins}-{losses}"
            teams.append({
                "name": name,
                "wins": wins,
                "losses": losses,
                "win_pct": win_pct,
                "games_behind": gb,
                "streak": streak or "N/A",
                "record": record,
                "division": division
            })
        return teams

    def _organize_by_divisions(self) -> Dict[str, List[Dict]]:
        def _to_int(val: Any) -> int:
            try:
                return int(val)
            except Exception:
                return -10_000
        def _to_float(val: Any) -> float:
            try:
                return float(val)
            except Exception:
                return -1.0
        divisions: Dict[str, List[Dict]] = {}
        for team in self.teams:
            division = team.get("division", "League")
            divisions.setdefault(division, []).append(team)
        for division_teams in divisions.values():
            division_teams.sort(key=lambda x: (_to_float(x.get("win_pct")), _to_int(x.get("wins"))), reverse=True)
        return divisions
