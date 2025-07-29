"""
Native PyQt6 Table with Enhanced Accessibility

This uses QTableWidget with proper accessibility configuration
for optimal screen reader support.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QTabWidget
)
from PyQt6.QtCore import Qt

class NativeAccessibleTableWidget(QWidget):
    """Widget using native PyQt6 tables with enhanced accessibility"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Native PyQt6 Accessible Tables")
        self.setGeometry(100, 100, 1200, 800)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Native PyQt6 Accessible Tables - Optimized for Screen Readers")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Button controls
        button_layout = QHBoxLayout()
        
        standings_btn = QPushButton("Show Standings Table")
        standings_btn.clicked.connect(self.show_standings_table)
        button_layout.addWidget(standings_btn)
        
        player_stats_btn = QPushButton("Show Player Stats Table")
        player_stats_btn.clicked.connect(self.show_player_stats_table)
        button_layout.addWidget(player_stats_btn)
        
        team_summary_btn = QPushButton("Show Team Summary Table")
        team_summary_btn.clicked.connect(self.show_team_summary_table)
        button_layout.addWidget(team_summary_btn)
        
        layout.addLayout(button_layout)
        
        # Tab widget to hold different tables
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Data Tables")
        self.tab_widget.setAccessibleDescription("Tabbed interface containing sports data tables")
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
        
        # Show initial content
        self.show_standings_table()
    
    def create_accessible_table(self, data, headers, title, description=""):
        """Create an accessible QTableWidget"""
        
        table = QTableWidget()
        table.setRowCount(len(data))
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Set accessibility properties
        table.setAccessibleName(title)
        table.setAccessibleDescription(f"{description} Table with {len(data)} rows and {len(headers)} columns.")
        
        # Configure table behavior for accessibility
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        
        # Hide row numbers for cleaner appearance
        table.verticalHeader().setVisible(False)
        
        # Configure column headers
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        
        # Populate table with data
        for row_idx, row_data in enumerate(data):
            for col_idx, header_name in enumerate(headers):
                value = str(row_data.get(header_name, "")).strip()
                item = QTableWidgetItem(value)
                
                # Set accessibility text for each cell
                accessible_text = f"{headers[col_idx]}: {value}"
                if row_idx == 0 or col_idx == 0:  # First row or column
                    accessible_text = f"Row {row_idx + 1}, {accessible_text}"
                
                item.setData(Qt.ItemDataRole.AccessibleTextRole, accessible_text)
                item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, 
                           f"Cell at row {row_idx + 1}, column {col_idx + 1}: {value}")
                
                # Make cells read-only
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                table.setItem(row_idx, col_idx, item)
        
        # Set focus to first cell
        table.setCurrentCell(0, 0)
        table.setFocus()
        
        return table
    
    def show_standings_table(self):
        """Display MLB standings table"""
        standings_data = [
            {"Team": "New York Yankees", "W": "95", "L": "67", "Win %": ".586", "GB": "-", "Division": "AL East"},
            {"Team": "Houston Astros", "W": "93", "L": "69", "Win %": ".574", "GB": "2.0", "Division": "AL West"},
            {"Team": "Los Angeles Dodgers", "W": "100", "L": "62", "Win %": ".617", "GB": "-", "Division": "NL West"},
            {"Team": "Atlanta Braves", "W": "98", "L": "64", "Win %": ".605", "GB": "2.0", "Division": "NL East"},
            {"Team": "Philadelphia Phillies", "W": "87", "L": "75", "Win %": ".537", "GB": "11.0", "Division": "NL East"},
            {"Team": "San Diego Padres", "W": "82", "L": "80", "Win %": ".506", "GB": "18.0", "Division": "NL West"},
        ]
        
        headers = ["Team", "W", "L", "Win %", "GB", "Division"]
        title = "MLB Standings"
        description = "Current Major League Baseball team standings showing wins, losses, win percentage, games behind leader, and division information."
        
        table = self.create_accessible_table(standings_data, headers, title, description)
        
        # Clear existing tabs and add new one
        self.tab_widget.clear()
        self.tab_widget.addTab(table, "MLB Standings")
    
    def show_player_stats_table(self):
        """Display player statistics table"""
        player_data = [
            {"Player": "Aaron Judge", "Position": "RF", "AB": "4", "R": "2", "H": "3", "RBI": "2", "BB": "1", "SO": "0", "AVG": ".311"},
            {"Player": "Gleyber Torres", "Position": "2B", "AB": "4", "R": "1", "H": "2", "RBI": "1", "BB": "0", "SO": "1", "AVG": ".279"},
            {"Player": "Anthony Rizzo", "Position": "1B", "AB": "3", "R": "0", "H": "1", "RBI": "0", "BB": "1", "SO": "1", "AVG": ".224"},
            {"Player": "Giancarlo Stanton", "Position": "DH", "AB": "4", "R": "1", "H": "1", "RBI": "2", "BB": "0", "SO": "2", "AVG": ".211"},
            {"Player": "Josh Donaldson", "Position": "3B", "AB": "4", "R": "0", "H": "0", "RBI": "0", "BB": "0", "SO": "3", "AVG": ".222"},
        ]
        
        headers = ["Player", "Position", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
        title = "Player Statistics"
        description = "Individual player batting statistics. AB=At Bats, R=Runs, H=Hits, RBI=Runs Batted In, BB=Walks, SO=Strikeouts, AVG=Batting Average."
        
        table = self.create_accessible_table(player_data, headers, title, description)
        
        # Clear existing tabs and add new one
        self.tab_widget.clear()
        self.tab_widget.addTab(table, "Player Statistics")
    
    def show_team_summary_table(self):
        """Display team summary statistics table"""
        team_data = [
            {"Team": "New York Yankees", "Statistic": "Total Runs", "Value": "8"},
            {"Team": "New York Yankees", "Statistic": "Total Hits", "Value": "12"},
            {"Team": "New York Yankees", "Statistic": "Total RBIs", "Value": "7"},
            {"Team": "New York Yankees", "Statistic": "Total At Bats", "Value": "35"},
            {"Team": "Houston Astros", "Statistic": "Total Runs", "Value": "4"},
            {"Team": "Houston Astros", "Statistic": "Total Hits", "Value": "8"},
            {"Team": "Houston Astros", "Statistic": "Total RBIs", "Value": "4"},
            {"Team": "Houston Astros", "Statistic": "Total At Bats", "Value": "32"},
        ]
        
        headers = ["Team", "Statistic", "Value"]
        title = "Team Summary"
        description = "Team-level performance statistics comparing both teams in the current game."
        
        table = self.create_accessible_table(team_data, headers, title, description)
        
        # Clear existing tabs and add new one
        self.tab_widget.clear()
        self.tab_widget.addTab(table, "Team Summary")

def main():
    app = QApplication(sys.argv)
    
    # Create and show the widget
    widget = NativeAccessibleTableWidget()
    widget.show()
    
    print("🎯 Native PyQt6 Accessible Table Demo Started")
    print("✅ Using QTableWidget with enhanced accessibility")
    print("✅ Proper ARIA-like attributes set for screen readers")
    print("✅ Keyboard navigation enabled")
    print("📋 Use arrow keys, Tab, and Enter to navigate")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
