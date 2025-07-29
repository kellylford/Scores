"""
Integration Example: Adding HTML Table Accessibility to Sports Scores App

This file shows how to integrate the HTML table helper into your existing
main.py sports scores application for better accessibility.

Key Benefits of HTML Tables:
1. Excellent screen reader support
2. Built-in keyboard navigation 
3. Proper table semantics and ARIA labels
4. Sortable columns
5. Better focus management
6. Web accessibility standards compliance
"""

# Example modifications to add to your main.py

def show_standings_dialog_html(self):
    """Enhanced version of show_standings_dialog using HTML table"""
    standings_data = espn_api.get_standings(self.current_league)
    
    if not standings_data:
        QMessageBox.information(self, "Standings", f"No standings data available for {self.current_league}.")
        return
    
    # Convert standings data to format expected by HTML table
    table_data = []
    for team_data in standings_data:
        table_data.append({
            "Team": team_data.get("team_name", ""),
            "W": str(team_data.get("wins", "")),
            "L": str(team_data.get("losses", "")),
            "Win %": team_data.get("win_percentage", ""),
            "GB": team_data.get("games_back", ""),
            "Division": team_data.get("division", "")
        })
    
    headers = ["Team", "W", "L", "Win %", "GB", "Division"]
    title = f"{self.current_league} Standings"
    description = f"Current {self.current_league} team standings with wins, losses, win percentage, games behind leader, and division information. Use arrow keys to navigate, click column headers to sort."
    
    # Use HTML table for better accessibility
    from html_table_helper import show_html_table
    show_html_table(table_data, headers, title, self, description)

def show_boxscore_data_html(self, layout, boxscore_data):
    """Enhanced version using HTML tables for boxscore data"""
    if not boxscore_data:
        layout.addWidget(QLabel("No boxscore data available"))
        return
    
    teams_data = boxscore_data.get("teams", [])
    
    # Create HTML table for team summary
    if teams_data:
        team_summary_data = []
        
        for team_data in teams_data:
            if isinstance(team_data, dict):
                team_info = team_data.get("team", {})
                team_name = team_info.get("displayName", "Unknown Team")
                
                # Extract team statistics
                statistics = team_data.get("statistics", [])
                if statistics:
                    for stat in statistics:
                        if isinstance(stat, dict):
                            stat_name = stat.get("name", "")
                            stat_value = stat.get("displayValue", "")
                            if stat_name and stat_value:
                                team_summary_data.append({
                                    "Team": team_name,
                                    "Statistic": stat_name,
                                    "Value": stat_value
                                })
        
        if team_summary_data:
            headers = ["Team", "Statistic", "Value"]
            title = "Team Statistics Summary"
            description = "Team-level performance statistics for this game. Sortable by team name, statistic type, or value."
            
            # Add button to show HTML table
            show_stats_btn = QPushButton("View Team Stats (Accessible Table)")
            show_stats_btn.clicked.connect(
                lambda: self.show_html_table_dialog(team_summary_data, headers, title, description)
            )
            layout.addWidget(show_stats_btn)
    
    # Create HTML table for player statistics  
    players_data = boxscore_data.get("players", [])
    if players_data:
        for team_players in players_data:
            if not isinstance(team_players, dict):
                continue
                
            team_info = team_players.get("team", {})
            team_name = team_info.get("displayName", "Unknown Team")
            
            statistics = team_players.get("statistics", [])
            if not statistics:
                continue
                
            stat_group = statistics[0] if statistics else {}
            athletes = stat_group.get("athletes", [])
            
            if athletes:
                player_data = []
                
                for athlete in athletes:
                    if not isinstance(athlete, dict):
                        continue
                        
                    athlete_info = athlete.get("athlete", {})
                    name = athlete_info.get("displayName", "Unknown Player")
                    position = athlete_info.get("position", {}).get("abbreviation", "")
                    
                    stats = athlete.get("stats", [])
                    if stats:
                        # Extract common baseball stats
                        stats_dict = {}
                        for stat in stats:
                            stats_dict[stat] = stats[stat] if stat in stats else "0"
                        
                        player_data.append({
                            "Player": name,
                            "Position": position,
                            "AB": stats_dict.get("atBats", "0"),
                            "R": stats_dict.get("runs", "0"),
                            "H": stats_dict.get("hits", "0"),
                            "RBI": stats_dict.get("RBIs", "0"),
                            "BB": stats_dict.get("walks", "0"),
                            "SO": stats_dict.get("strikeouts", "0"),
                            "AVG": stats_dict.get("avg", ".000")
                        })
                
                if player_data:
                    headers = ["Player", "Position", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
                    title = f"{team_name} - Player Statistics"
                    description = f"Individual player batting statistics for {team_name}. AB=At Bats, R=Runs, H=Hits, RBI=Runs Batted In, BB=Walks, SO=Strikeouts, AVG=Batting Average."
                    
                    # Add button to show HTML table
                    show_player_btn = QPushButton(f"View {team_name} Players (Accessible Table)")
                    show_player_btn.clicked.connect(
                        lambda checked, data=player_data, h=headers, t=title, d=description: 
                        self.show_html_table_dialog(data, h, t, d)
                    )
                    layout.addWidget(show_player_btn)

def show_html_table_dialog(self, data, headers, title, description=""):
    """Helper method to show HTML table dialog"""
    from html_table_helper import show_html_table
    show_html_table(data, headers, title, self, description)

# Instructions for integration:

"""
TO INTEGRATE INTO YOUR MAIN.PY:

1. Install PyQt6-WebEngine:
   pip install PyQt6-WebEngine

2. Add this import at the top of main.py:
   from html_table_helper import show_html_table

3. Add the show_html_table_dialog method to your SportsScoresApp class:
   def show_html_table_dialog(self, data, headers, title, description=""):
       from html_table_helper import show_html_table
       show_html_table(data, headers, title, self, description)

4. Replace your existing table methods with HTML versions, or add new menu options:
   
   For standings:
   - Replace show_standings_dialog with show_standings_dialog_html
   
   For boxscores:
   - Replace show_boxscore_data with show_boxscore_data_html
   
   Or keep both and add menu options like:
   - "View Standings (Standard Table)"
   - "View Standings (Accessible HTML Table)" 

5. Add keyboard shortcuts for accessibility:
   In your __init__ method, add:
   
   # Add accessibility shortcut
   html_action = QAction("Show Accessible Tables", self)
   html_action.setShortcut("Alt+A")
   html_action.triggered.connect(self.show_accessibility_menu)
   
   def show_accessibility_menu(self):
       # Show dialog with options for accessible table views
       pass

BENEFITS OF HTML TABLES:
✅ Excellent screen reader support
✅ Built-in keyboard navigation (arrow keys, Tab, Home/End)
✅ Proper table semantics and ARIA labels
✅ Sortable columns with visual/audio feedback
✅ Better focus management and visual indicators
✅ Web accessibility standards compliance
✅ Can be exported to browser for sharing
✅ Responsive design for different screen sizes
✅ High contrast mode support
✅ Works with assistive technologies

ACCESSIBILITY FEATURES INCLUDED:
- Full ARIA labeling and descriptions
- Keyboard navigation with arrow keys
- Screen reader announcements
- High contrast focus indicators
- Sortable columns with audio feedback
- Export to browser option
- Mobile responsive design
- Semantic HTML structure
"""
