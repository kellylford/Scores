"""
Accessible Table Solution using QTextBrowser

This provides better screen reader support than QWebEngineView
by using QTextBrowser which screen readers recognize as text content.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, 
    QTextBrowser, QLabel, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class AccessibleTableWidget(QWidget):
    """Widget that displays table data in an accessible format for screen readers"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accessible Table Demo - Screen Reader Friendly")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Screen Reader Accessible Table Demo")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Info label
        info_label = QLabel("These tables are optimized for screen readers like JAWS, NVDA, and Narrator")
        info_label.setStyleSheet("color: #666; margin: 5px; font-style: italic;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Button controls
        button_layout = QHBoxLayout()
        
        standings_btn = QPushButton("Show Standings Table")
        standings_btn.clicked.connect(self.show_standings_table)
        standings_btn.setAccessibleDescription("Display MLB team standings in accessible table format")
        button_layout.addWidget(standings_btn)
        
        player_stats_btn = QPushButton("Show Player Stats Table")
        player_stats_btn.clicked.connect(self.show_player_stats_table)
        player_stats_btn.setAccessibleDescription("Display player statistics in accessible table format")
        button_layout.addWidget(player_stats_btn)
        
        team_summary_btn = QPushButton("Show Team Summary Table")
        team_summary_btn.clicked.connect(self.show_team_summary_table)
        team_summary_btn.setAccessibleDescription("Display team performance summary in accessible table format")
        button_layout.addWidget(team_summary_btn)
        
        layout.addLayout(button_layout)
        
        # Create splitter for side-by-side view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Text browser for HTML table (better screen reader support)
        self.text_browser = QTextBrowser()
        self.text_browser.setAccessibleName("Accessible Data Table")
        self.text_browser.setAccessibleDescription("Table data formatted for screen reader navigation")
        
        # Set font for better readability
        font = QFont("Consolas", 10)  # Monospace font for better alignment
        self.text_browser.setFont(font)
        
        splitter.addWidget(self.text_browser)
        
        # Add structured text version for comparison
        self.structured_text = QTextBrowser()
        self.structured_text.setAccessibleName("Structured Text Alternative")
        self.structured_text.setAccessibleDescription("Same data in structured text format for comparison")
        splitter.addWidget(self.structured_text)
        
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
        # Show initial content
        self.show_standings_table()
    
    def create_accessible_html_table(self, data, headers, title, description=""):
        """Create HTML table optimized for screen readers"""
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.4;
                    color: #333;
                }}
                
                h1 {{
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }}
                
                .description {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #007bff;
                    margin: 15px 0;
                    font-style: italic;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    border: 2px solid #2c3e50;
                }}
                
                caption {{
                    font-weight: bold;
                    font-size: 1.1em;
                    margin-bottom: 10px;
                    text-align: left;
                    color: #2c3e50;
                }}
                
                th {{
                    background-color: #3498db;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #2980b9;
                    font-weight: bold;
                }}
                
                td {{
                    padding: 10px 12px;
                    border: 1px solid #ddd;
                    background-color: white;
                }}
                
                tr:nth-child(even) td {{
                    background-color: #f8f9fa;
                }}
                
                tbody tr:hover td {{
                    background-color: #e3f2fd;
                }}
                
                .sr-instructions {{
                    background: #d1ecf1;
                    color: #0c5460;
                    padding: 10px;
                    border: 1px solid #bee5eb;
                    border-radius: 4px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            
            {f'<div class="description">{description}</div>' if description else ''}
            
            <div class="sr-instructions">
                <strong>Screen Reader Instructions:</strong> 
                Use table navigation commands to move through this data. 
                In JAWS, use Ctrl+Alt+Arrow keys. In NVDA, use Ctrl+Alt+Arrow keys.
            </div>
            
            <table role="table" aria-label="{title}">
                <caption>
                    {title} - {len(data)} rows, {len(headers)} columns
                    {f'. {description}' if description else ''}
                </caption>
                
                <thead>
                    <tr>
        """
        
        # Add headers
        for i, header in enumerate(headers):
            html += f"""
                        <th scope="col" id="col{i}">{header}</th>
            """
        
        html += """
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add data rows
        for row_idx, row_data in enumerate(data):
            html += f'                    <tr>\n'
            
            for col_idx, header in enumerate(headers):
                value = str(row_data.get(header, "")).strip()
                
                # First column gets row header treatment
                if col_idx == 0:
                    html += f'                        <th scope="row" headers="col{col_idx}">{value}</th>\n'
                else:
                    html += f'                        <td headers="col{col_idx}">{value}</td>\n'
            
            html += '                    </tr>\n'
        
        html += """
                </tbody>
            </table>
            
            <div class="sr-instructions">
                <strong>Table Summary:</strong> This table contains {row_count} rows of data with {col_count} columns: {headers_list}.
            </div>
        </body>
        </html>
        """.format(
            row_count=len(data),
            col_count=len(headers),
            headers_list=", ".join(headers)
        )
        
        return html
    
    def create_structured_text(self, data, headers, title, description=""):
        """Create structured text version for screen readers"""
        
        text = f"""
{title}
{'=' * len(title)}

{description}

Table Summary: {len(data)} rows, {len(headers)} columns
Columns: {', '.join(headers)}

Screen Reader Navigation:
- Use standard text navigation commands
- Each row is on a separate line
- Data is separated by pipes (|) for clarity

Data:
-----

"""
        
        # Add header row
        text += "| " + " | ".join(f"{header:12s}" for header in headers) + " |\n"
        text += "|" + "|".join("-" * 14 for _ in headers) + "|\n"
        
        # Add data rows
        for row_data in data:
            row_values = []
            for header in headers:
                value = str(row_data.get(header, "")).strip()
                row_values.append(f"{value:12s}")
            
            text += "| " + " | ".join(row_values) + " |\n"
        
        text += f"\nEnd of table. Total rows: {len(data)}\n"
        
        return text
    
    def show_standings_table(self):
        """Display MLB standings in accessible format"""
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
        
        # Set HTML content
        html_content = self.create_accessible_html_table(standings_data, headers, title, description)
        self.text_browser.setHtml(html_content)
        
        # Set structured text content
        text_content = self.create_structured_text(standings_data, headers, title, description)
        self.structured_text.setPlainText(text_content)
    
    def show_player_stats_table(self):
        """Display player statistics in accessible format"""
        player_data = [
            {"Player": "Aaron Judge", "Position": "RF", "AB": "4", "R": "2", "H": "3", "RBI": "2", "BB": "1", "SO": "0", "AVG": ".311"},
            {"Player": "Gleyber Torres", "Position": "2B", "AB": "4", "R": "1", "H": "2", "RBI": "1", "BB": "0", "SO": "1", "AVG": ".279"},
            {"Player": "Anthony Rizzo", "Position": "1B", "AB": "3", "R": "0", "H": "1", "RBI": "0", "BB": "1", "SO": "1", "AVG": ".224"},
            {"Player": "Giancarlo Stanton", "Position": "DH", "AB": "4", "R": "1", "H": "1", "RBI": "2", "BB": "0", "SO": "2", "AVG": ".211"},
            {"Player": "Josh Donaldson", "Position": "3B", "AB": "4", "R": "0", "H": "0", "RBI": "0", "BB": "0", "SO": "3", "AVG": ".222"},
        ]
        
        headers = ["Player", "Position", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
        title = "Player Statistics - New York Yankees"
        description = "Individual player batting statistics. AB=At Bats, R=Runs, H=Hits, RBI=Runs Batted In, BB=Walks, SO=Strikeouts, AVG=Batting Average."
        
        # Set HTML content
        html_content = self.create_accessible_html_table(player_data, headers, title, description)
        self.text_browser.setHtml(html_content)
        
        # Set structured text content
        text_content = self.create_structured_text(player_data, headers, title, description)
        self.structured_text.setPlainText(text_content)
    
    def show_team_summary_table(self):
        """Display team summary statistics in accessible format"""
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
        title = "Team Summary Statistics"
        description = "Team-level performance statistics comparing both teams in the current game."
        
        # Set HTML content
        html_content = self.create_accessible_html_table(team_data, headers, title, description)
        self.text_browser.setHtml(html_content)
        
        # Set structured text content
        text_content = self.create_structured_text(team_data, headers, title, description)
        self.structured_text.setPlainText(text_content)

def main():
    app = QApplication(sys.argv)
    
    # Create and show the widget
    widget = AccessibleTableWidget()
    widget.show()
    
    print("🎯 Accessible Table Demo Started")
    print("✅ This version uses QTextBrowser which screen readers recognize")
    print("✅ JAWS virtual cursor should work properly")
    print("✅ Table navigation commands should be available")
    print("📋 Try both the HTML table and structured text versions")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
