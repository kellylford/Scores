from typing import Dict, List
from datetime import datetime
import re

# Import timezone conversion function
try:
    from timezone_utils import convert_espn_time_to_local
    TIMEZONE_CONVERSION_AVAILABLE = True
except ImportError:
    TIMEZONE_CONVERSION_AVAILABLE = False

class GameData:
    """Data model for game information"""
    def __init__(self, raw_data: Dict, league: str = None):
        self.raw = raw_data or {}
        self.league = league
        self.game_id = self.raw.get("id", "")
        self.name = self.raw.get("name", "Unknown Game")
        self.start_time = self.raw.get("start_time", self.raw.get("date", ""))
        
        # Apply timezone conversion to start_time if available
        if TIMEZONE_CONVERSION_AVAILABLE and self.start_time:
            self.start_time = convert_espn_time_to_local(self.start_time)
            
        self.status = self.raw.get("status", "")
        self.teams = self.raw.get("teams", [])

    def _format_football_time(self, time_str: str) -> str:
        """Format football game times to 'Thu 8/28 8:00PM' style"""
        if not time_str:
            return time_str
            
        # Handle formats like "8/28 - 5:30 PM EDT"
        if " - " in time_str and ("PM" in time_str or "AM" in time_str):
            try:
                date_part, time_part = time_str.split(" - ", 1)
                
                # Parse the date (e.g., "8/28")
                if "/" in date_part:
                    month_day = date_part.strip()
                    month, day = map(int, month_day.split("/"))
                    
                    # Smart year detection - use the most appropriate year
                    current_year = datetime.now().year
                    current_month = datetime.now().month
                    
                    # If the game month is significantly before current month, it's likely next year
                    # If the game month is after current month or close to it, use current year
                    if month < current_month - 6:  # More than 6 months ago, probably next year
                        year = current_year + 1
                    elif month < current_month - 2:  # A few months ago, might be previous year
                        year = current_year - 1  
                    else:
                        year = current_year
                    
                    # Create date and get day of week
                    game_date = datetime(year, month, day)
                    day_abbrev = game_date.strftime("%a")
                    
                    # Clean up time (remove timezone, simplify format)
                    clean_time = time_part.strip()
                    # Remove timezone abbreviations
                    clean_time = re.sub(r'\s+(EDT|EST|CDT|CST|MDT|MST|PDT|PST|ET|CT|MT|PT)$', '', clean_time)
                    
                    # Convert to simpler format (remove spaces, make PM/AM consistent)
                    clean_time = clean_time.replace(" ", "")
                    
                    return f"{day_abbrev} {month_day} {clean_time}"
                    
            except (ValueError, IndexError):
                # If parsing fails, return original
                pass
                
        return time_str

    def get_display_text(self) -> str:
        parts: List[str] = []
        
        # Build team and score display
        if self.teams:
            display_parts = []
            for t in self.teams:
                abbrev = t.get("name") or t.get("abbreviation", "?")
                score = t.get("score")
                display_parts.append(f"{abbrev}{' ' + score if score else ''}")
            parts.append(" vs ".join(display_parts))
        else:
            parts.append(self.name)
        
        # Determine if this is a football game for special formatting
        is_football = self.league in ['NFL', 'NCAAF'] if self.league else \
                     any(keyword in self.name.lower() for keyword in ['ncaaf', 'nfl']) or \
                     any(keyword in str(self.raw).lower() for keyword in ['football'])
        
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
                # Clean up the time display - use enhanced football formatting
                time_display = self.start_time
                if is_football:
                    time_display = self._format_football_time(time_display)
                
                if " - " in time_display and not is_football:
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
            time_display = self.start_time
            if is_football:
                time_display = self._format_football_time(time_display)
            parts.append(f"({time_display})")
        
        return " ".join(parts)

    def has_scores(self) -> bool:
        return any(t.get("score") for t in self.teams)
