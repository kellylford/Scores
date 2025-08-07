from typing import Dict, List

class GameData:
    """Data model for game information"""
    def __init__(self, raw_data: Dict):
        self.raw = raw_data or {}
        self.game_id = self.raw.get("id", "")
        self.name = self.raw.get("name", "Unknown Game")
        self.start_time = self.raw.get("start_time", self.raw.get("date", ""))
        self.status = self.raw.get("status", "")
        self.teams = self.raw.get("teams", [])

    def get_display_text(self) -> str:
        parts: List[str] = []
        if self.teams:
            display_parts = []
            for t in self.teams:
                abbrev = t.get("abbreviation") or t.get("name", "?")
                score = t.get("score")
                display_parts.append(f"{abbrev}{' ' + score if score else ''}")
            parts.append(" vs ".join(display_parts))
        else:
            parts.append(self.name)
        if self.status:
            parts.append(f"[{self.status}]")
        elif self.start_time:
            parts.append(f"({self.start_time})")
        return " ".join(parts)

    def has_scores(self) -> bool:
        return any(t.get("score") for t in self.teams)
