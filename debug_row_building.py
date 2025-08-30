#!/usr/bin/env python3
"""
Debug script to test the row building logic directly
"""

from services.api_service import ApiService
from models.standings import StandingsData

def test_row_building():
    """Test row building logic directly"""
    
    print("Testing row building logic...")
    
    # Get MLB standings
    standings_list = ApiService.get_standings('MLB')
    standings_data = StandingsData(standings_list)
    
    if "AL East" in standings_data.divisions:
        teams = standings_data.divisions["AL East"]
        team = teams[0]
        
        print(f"Testing with team: {team.get('team_name', team.get('name'))}")
        print(f"Team data keys: {list(team.keys())}")
        
        # Import the row building methods
        from accessible_table import StandingsTable
        
        # Create a dummy table instance to access the methods
        # We can't actually create the table without QApplication, but we can test the logic
        
        # Test basic row building
        print(f"\n--- Testing Basic Row Building ---")
        
        # Simulate _build_basic_row method logic
        team_name = team.get("team_name") or team.get("name", "")
        wins = str(team.get("wins", ""))
        losses = str(team.get("losses", ""))
        
        # Format win percentage properly
        win_pct = team.get("win_percentage") or team.get("win_pct", "")
        if isinstance(win_pct, (int, float)) and win_pct > 0:
            win_pct = f"{win_pct:.3f}"
        
        games_back = team.get("games_back") or team.get("games_behind", "")
        streak = team.get("streak", "N/A")
        
        basic_row = [
            "1",  # position
            team_name,
            wins,
            losses,
            win_pct,
            games_back,
            streak
        ]
        
        print(f"Basic row: {basic_row}")
        
        print(f"\n--- Testing Expanded Row Building ---")
        
        # Simulate _build_expanded_row method logic for MLB
        def format_differential(value):
            if value > 0:
                return f"+{value}"
            elif value < 0:
                return str(value)
            else:
                return "0"
        
        def format_record(wins, losses):
            return f"{wins}-{losses}"
        
        def format_percentage(value):
            if value > 0:
                return f"{value:.1f}%"
            return "—"
        
        def format_magic_number(value):
            if value and value > 0:
                return str(value)
            return "—"
        
        expanded_additions = [
            str(team.get("runs_for", "")),
            str(team.get("runs_against", "")),
            format_differential(team.get("run_differential", 0)),
            format_record(team.get("home_wins", 0), team.get("home_losses", 0)),
            format_record(team.get("road_wins", 0), team.get("road_losses", 0)),
            format_percentage(team.get("playoff_percent", 0)),
            format_magic_number(team.get("magic_number"))
        ]
        
        expanded_row = basic_row + expanded_additions
        
        print(f"Expanded additions: {expanded_additions}")
        print(f"Full expanded row: {expanded_row}")
        
        # Show column mapping
        basic_headers = ["Pos", "Team", "W", "L", "PCT", "GB", "Streak"]
        expanded_headers = ["Pos", "Team", "W", "L", "PCT", "GB", "Streak", "R", "RA", "Diff", "Home", "Road", "Playoff%", "Magic#"]
        
        print(f"\n--- Column Mapping ---")
        print(f"Basic view ({len(basic_headers)} columns):")
        for i, (header, value) in enumerate(zip(basic_headers, basic_row)):
            print(f"  {i}: {header} = {value}")
        
        print(f"\nExpanded view ({len(expanded_headers)} columns):")
        for i, (header, value) in enumerate(zip(expanded_headers, expanded_row)):
            print(f"  {i}: {header} = {value}")
        
        # Check if expanded data is actually different
        print(f"\n--- Verification ---")
        print(f"Basic row length: {len(basic_row)}")
        print(f"Expanded row length: {len(expanded_row)}")
        print(f"Expanded data contains:")
        for i, addition in enumerate(expanded_additions):
            print(f"  {expanded_headers[7+i]}: {addition}")

if __name__ == "__main__":
    test_row_building()
