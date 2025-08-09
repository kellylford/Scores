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
        
        # Build team and score display
        if self.teams:
            display_parts = []
            for t in self.teams:
                abbrev = t.get("abbreviation") or t.get("name", "?")
                score = t.get("score")
                display_parts.append(f"{abbrev}{' ' + score if score else ''}")
            parts.append(" vs ".join(display_parts))
        else:
            parts.append(self.name)
        
        # Add status and timing information
        if self.status and self.status.lower() == "in progress":
            # For live games, show the inning/quarter/period situation
            if self.start_time:
                # Check for baseball inning info
                if any(inning in self.start_time.lower() for inning in ['top', 'bot', 'end', 'mid']):
                    parts.append(f"[{self.start_time}]")
                # Check for football quarter/time info  
                elif any(quarter in self.start_time.lower() for quarter in ['1st', '2nd', '3rd', '4th', 'ot']):
                    parts.append(f"[{self.start_time}]")
                # Check for other sports time/period formats
                elif " - " in self.start_time and any(period in self.start_time.lower() for period in ['quarter', 'period', 'half']):
                    parts.append(f"[{self.start_time}]")
                else:
                    parts.append(f"[{self.status}]")
            else:
                parts.append(f"[{self.status}]")
        elif self.status and self.status.lower() == "final":
            # For final games, show final status (may include extra innings)
            if self.start_time and "final" in self.start_time.lower():
                parts.append(f"[{self.start_time}]")
            else:
                parts.append(f"[{self.status}]")
        elif self.status and self.status.lower() == "scheduled":
            # For scheduled games, show start time
            if self.start_time:
                # Clean up the time display - remove date if it's today
                time_display = self.start_time
                if " - " in time_display:
                    time_part = time_display.split(" - ", 1)[1]
                    parts.append(f"({time_part})")
                else:
                    parts.append(f"({time_display})")
            else:
                parts.append(f"[{self.status}]")
        elif self.status:
            # For other statuses (Postponed, Delayed, etc.)
            parts.append(f"[{self.status}]")
        elif self.start_time:
            # Fallback: show start time for games without clear status
            parts.append(f"({self.start_time})")
        
        return " ".join(parts)

    def has_scores(self) -> bool:
        return any(t.get("score") for t in self.teams)
