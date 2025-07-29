"""
HTML Table Demo for Sports Scores App

This demo shows how the HTML table accessibility solution works with
real sports data similar to your application.

Run this to see the accessible HTML table in action:
python html_table_demo.py
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt

# Import the HTML table helper
from html_table_helper import show_html_table

class SportsTableDemo(QWidget):
    """Demo widget showing HTML table accessibility features"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sports Scores - Accessible HTML Tables Demo")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Sports Scores - Accessible HTML Tables Demo")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "This demo shows HTML-based tables with excellent accessibility support.\n"
            "HTML tables provide better screen reader support, keyboard navigation,\n"
            "and web accessibility standards compared to PyQt6 native tables."
        )
        desc_label.setStyleSheet("color: #666; margin: 10px; text-align: center;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Button section
        button_layout = QVBoxLayout()
        
        # Standings button
        standings_btn = QPushButton("View MLB Standings (HTML Table)")
        standings_btn.setToolTip("Shows team standings in an accessible HTML table format")
        standings_btn.clicked.connect(self.show_standings)
        standings_btn.setStyleSheet("padding: 10px; font-size: 14px; margin: 5px;")
        button_layout.addWidget(standings_btn)
        
        # Player stats button
        player_btn = QPushButton("View Player Statistics (HTML Table)")
        player_btn.setToolTip("Shows individual player statistics in HTML table format")
        player_btn.clicked.connect(self.show_player_stats)
        player_btn.setStyleSheet("padding: 10px; font-size: 14px; margin: 5px;")
        button_layout.addWidget(player_btn)
        
        # Team summary button
        team_btn = QPushButton("View Team Summary (HTML Table)")
        team_btn.setToolTip("Shows team performance summary statistics")
        team_btn.clicked.connect(self.show_team_summary)
        team_btn.setStyleSheet("padding: 10px; font-size: 14px; margin: 5px;")
        button_layout.addWidget(team_btn)
        
        # Injury report button
        injury_btn = QPushButton("View Injury Report (HTML Table)")
        injury_btn.setToolTip("Shows injury report in accessible table format")
        injury_btn.clicked.connect(self.show_injury_report)
        injury_btn.setStyleSheet("padding: 10px; font-size: 14px; margin: 5px;")
        button_layout.addWidget(injury_btn)
        
        layout.addLayout(button_layout)
        
        # Features section
        features_label = QLabel("HTML Table Accessibility Features:")
        features_label.setStyleSheet("font-weight: bold; margin-top: 20px; color: #2c3e50;")
        layout.addWidget(features_label)
        
        features_text = QLabel(
            "✅ Full keyboard navigation (arrow keys, Tab, Home/End)\n"
            "✅ Screen reader announcements and ARIA labels\n"
            "✅ Sortable columns with visual/audio feedback\n"
            "✅ High contrast focus indicators\n"
            "✅ Semantic HTML structure for assistive technologies\n"
            "✅ Export to browser option for sharing\n"
            "✅ Responsive design for different screen sizes\n"
            "✅ Web accessibility standards compliance"
        )
        features_text.setStyleSheet("color: #27ae60; margin: 10px; line-height: 1.4;")
        layout.addWidget(features_text)
        
        self.setLayout(layout)
    
    def show_standings(self):
        """Show sample MLB standings data in HTML table"""
        standings_data = [
            {"Team": "Los Angeles Dodgers", "W": "100", "L": "62", "Win %": ".617", "GB": "-", "Division": "NL West", "Streak": "W3"},
            {"Team": "Atlanta Braves", "W": "104", "L": "58", "Win %": ".642", "GB": "-", "Division": "NL East", "Streak": "W1"},
            {"Team": "Houston Astros", "W": "90", "L": "72", "Win %": ".556", "GB": "2.0", "Division": "AL West", "Streak": "L2"},
            {"Team": "New York Yankees", "W": "82", "L": "80", "Win %": ".506", "GB": "10.0", "Division": "AL East", "Streak": "W2"},
            {"Team": "Philadelphia Phillies", "W": "90", "L": "72", "Win %": ".556", "GB": "14.0", "Division": "NL East", "Streak": "L1"},
            {"Team": "San Diego Padres", "W": "82", "L": "80", "Win %": ".506", "GB": "18.0", "Division": "NL West", "Streak": "W4"},
            {"Team": "Milwaukee Brewers", "W": "92", "L": "70", "Win %": ".568", "GB": "6.0", "Division": "NL Central", "Streak": "W1"},
            {"Team": "Arizona Diamondbacks", "W": "89", "L": "73", "Win %": ".549", "GB": "11.0", "Division": "NL West", "Streak": "L3"},
        ]
        
        headers = ["Team", "W", "L", "Win %", "GB", "Division", "Streak"]
        title = "MLB Standings"
        description = (
            "Current Major League Baseball team standings showing wins, losses, win percentage, "
            "games behind division leader, division, and current winning/losing streak. "
            "Click column headers to sort. Use arrow keys to navigate between cells."
        )
        
        show_html_table(standings_data, headers, title, self, description)
    
    def show_player_stats(self):
        """Show sample player statistics in HTML table"""
        player_data = [
            {"Player": "Mookie Betts", "Team": "LAD", "Position": "RF", "AB": "4", "R": "3", "H": "3", "RBI": "2", "BB": "1", "SO": "0", "AVG": ".307"},
            {"Player": "Freddie Freeman", "Team": "LAD", "Position": "1B", "AB": "5", "R": "1", "H": "2", "RBI": "3", "BB": "0", "SO": "1", "AVG": ".331"},
            {"Player": "Will Smith", "Team": "LAD", "Position": "C", "AB": "4", "R": "2", "H": "2", "RBI": "1", "BB": "1", "SO": "1", "AVG": ".261"},
            {"Player": "Max Muncy", "Team": "LAD", "Position": "3B", "AB": "3", "R": "1", "H": "1", "RBI": "2", "BB": "2", "SO": "1", "AVG": ".212"},
            {"Player": "Alex Verdugo", "Team": "NYY", "Position": "LF", "AB": "4", "R": "0", "H": "1", "RBI": "0", "BB": "0", "SO": "2", "AVG": ".233"},
            {"Player": "Juan Soto", "Team": "NYY", "Position": "RF", "AB": "3", "R": "1", "H": "1", "RBI": "1", "BB": "1", "SO": "1", "AVG": ".288"},
            {"Player": "Aaron Judge", "Team": "NYY", "Position": "CF", "AB": "4", "R": "1", "H": "2", "RBI": "2", "BB": "0", "SO": "1", "AVG": ".322"},
            {"Player": "Gleyber Torres", "Team": "NYY", "Position": "2B", "AB": "4", "R": "0", "H": "0", "RBI": "0", "BB": "0", "SO": "3", "AVG": ".257"},
        ]
        
        headers = ["Player", "Team", "Position", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
        title = "Player Batting Statistics"
        description = (
            "Individual player batting statistics from recent games. "
            "AB=At Bats, R=Runs, H=Hits, RBI=Runs Batted In, BB=Walks, SO=Strikeouts, AVG=Batting Average. "
            "Table is sortable by any column - click headers to sort by that statistic."
        )
        
        show_html_table(player_data, headers, title, self, description)
    
    def show_team_summary(self):
        """Show sample team summary statistics"""
        team_data = [
            {"Team": "Los Angeles Dodgers", "Statistic": "Runs Scored", "Value": "9", "Game": "vs NYY"},
            {"Team": "Los Angeles Dodgers", "Statistic": "Hits", "Value": "13", "Game": "vs NYY"},
            {"Team": "Los Angeles Dodgers", "Statistic": "Errors", "Value": "0", "Game": "vs NYY"},
            {"Team": "Los Angeles Dodgers", "Statistic": "Left On Base", "Value": "8", "Game": "vs NYY"},
            {"Team": "New York Yankees", "Statistic": "Runs Scored", "Value": "4", "Game": "@ LAD"},
            {"Team": "New York Yankees", "Statistic": "Hits", "Value": "7", "Game": "@ LAD"},
            {"Team": "New York Yankees", "Statistic": "Errors", "Value": "2", "Game": "@ LAD"},
            {"Team": "New York Yankees", "Statistic": "Left On Base", "Value": "6", "Game": "@ LAD"},
            {"Team": "Los Angeles Dodgers", "Statistic": "Team ERA", "Value": "2.85", "Game": "Season"},
            {"Team": "New York Yankees", "Statistic": "Team ERA", "Value": "3.74", "Game": "Season"},
        ]
        
        headers = ["Team", "Statistic", "Value", "Game"]
        title = "Team Performance Summary"
        description = (
            "Team-level performance statistics comparing game and season metrics. "
            "Shows runs scored, hits, errors, and other key team statistics. "
            "Use keyboard navigation to explore all data points."
        )
        
        show_html_table(team_data, headers, title, self, description)
    
    def show_injury_report(self):
        """Show sample injury report data"""
        injury_data = [
            {"Player": "Mookie Betts", "Team": "LAD", "Injury": "Hand fracture", "Status": "Day-to-day", "Expected Return": "Unknown", "Last Update": "Oct 25"},
            {"Player": "Fernando Tatis Jr.", "Team": "SD", "Injury": "Quad strain", "Status": "10-day IL", "Expected Return": "Nov 1", "Last Update": "Oct 20"},
            {"Player": "Ronald Acuña Jr.", "Team": "ATL", "Injury": "ACL tear", "Status": "60-day IL", "Expected Return": "2025 Season", "Last Update": "Oct 15"},
            {"Player": "Jacob deGrom", "Team": "TEX", "Injury": "Elbow inflammation", "Status": "15-day IL", "Expected Return": "Unknown", "Last Update": "Oct 22"},
            {"Player": "Mike Trout", "Team": "LAA", "Injury": "Wrist surgery", "Status": "60-day IL", "Expected Return": "2025 Spring", "Last Update": "Oct 18"},
            {"Player": "Francisco Lindor", "Team": "NYM", "Injury": "Back soreness", "Status": "Day-to-day", "Expected Return": "Oct 28", "Last Update": "Oct 26"},
        ]
        
        headers = ["Player", "Team", "Injury", "Status", "Expected Return", "Last Update"]
        title = "MLB Injury Report"
        description = (
            "Current injury report for MLB players showing injury details, status, "
            "expected return dates, and last update information. "
            "IL = Injured List. Data is sortable by any column for easy analysis."
        )
        
        show_html_table(injury_data, headers, title, self, description)

def main():
    """Run the HTML table demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Sports Scores - HTML Table Demo")
    app.setApplicationVersion("1.0")
    
    # Create and show demo widget
    demo = SportsTableDemo()
    demo.show()
    
    print("HTML Table Demo Started")
    print("Features demonstrated:")
    print("✅ Accessible HTML tables with ARIA labels")
    print("✅ Keyboard navigation (arrow keys, Tab, Home/End)")
    print("✅ Sortable columns")
    print("✅ Screen reader support")
    print("✅ High contrast focus indicators")
    print("✅ Export to browser functionality")
    print("\nClick any button to see the accessible tables in action!")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
