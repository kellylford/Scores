"""
HTML Table Example for Better Accessibility

This demonstrates how to display table data in an HTML control (QWebEngineView)
which provides much better accessibility support than PyQt6 native tables.
HTML tables have excellent screen reader support and follow web accessibility standards.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt

class HTMLTableWidget(QWidget):
    """Widget that displays table data using HTML for better accessibility"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTML Table Accessibility Demo")
        self.setGeometry(100, 100, 1000, 700)
        
        # Layout
        layout = QVBoxLayout()
        
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
        
        # Web view for HTML content
        self.web_view = QWebEngineView()
        self.web_view.setAccessibleName("Data Table Viewer")
        self.web_view.setAccessibleDescription("Interactive HTML table displaying sports data with full accessibility support")
        layout.addWidget(self.web_view)
        
        self.setLayout(layout)
        
        # Show initial content
        self.show_standings_table()
    
    def create_accessible_html_table(self, data, headers, title, description=""):
        """
        Create an accessible HTML table with proper ARIA labels and semantic markup
        
        Args:
            data: List of dictionaries containing row data
            headers: List of column headers
            title: Table title
            description: Optional table description
        """
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                
                .table-container {{
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                    margin: 20px 0;
                }}
                
                h1 {{
                    background: #2c3e50;
                    color: white;
                    margin: 0;
                    padding: 20px;
                    font-size: 1.5em;
                }}
                
                .description {{
                    padding: 15px 20px;
                    background: #ecf0f1;
                    font-style: italic;
                    color: #666;
                    border-bottom: 1px solid #ddd;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 14px;
                }}
                
                th {{
                    background-color: #34495e;
                    color: white;
                    padding: 12px 8px;
                    text-align: left;
                    font-weight: bold;
                    border-bottom: 2px solid #2c3e50;
                }}
                
                td {{
                    padding: 10px 8px;
                    border-bottom: 1px solid #eee;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                
                tr:hover {{
                    background-color: #e3f2fd;
                }}
                
                /* Focus styles for keyboard navigation */
                table:focus {{
                    outline: 3px solid #007acc;
                    outline-offset: 2px;
                }}
                
                th:focus, td:focus {{
                    outline: 2px solid #007acc;
                    outline-offset: -2px;
                    background-color: #e3f2fd;
                }}
                
                /* Responsive design */
                @media (max-width: 768px) {{
                    table {{
                        font-size: 12px;
                    }}
                    
                    th, td {{
                        padding: 8px 4px;
                    }}
                }}
                
                .sr-only {{
                    position: absolute;
                    width: 1px;
                    height: 1px;
                    padding: 0;
                    margin: -1px;
                    overflow: hidden;
                    clip: rect(0, 0, 0, 0);
                    white-space: nowrap;
                    border: 0;
                }}
            </style>
        </head>
        <body>
            <div class="table-container">
                <h1 id="table-title">{title}</h1>
                {f'<div class="description">{description}</div>' if description else ''}
                
                <table 
                    role="table" 
                    aria-labelledby="table-title"
                    {f'aria-describedby="table-desc"' if description else ''}
                    tabindex="0"
                >
                    <caption class="sr-only">
                        {title}. {description if description else ''} 
                        Use arrow keys to navigate, or Tab to move through cells.
                    </caption>
                    
                    <thead>
                        <tr role="row">
        """
        
        # Add headers
        for i, header in enumerate(headers):
            html += f"""
                            <th role="columnheader" 
                                scope="col" 
                                tabindex="0"
                                aria-sort="none"
                                id="col-{i}">
                                {header}
                            </th>
            """
        
        html += """
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add data rows
        for row_idx, row_data in enumerate(data):
            html += f'<tr role="row">\n'
            
            for col_idx, header in enumerate(headers):
                value = row_data.get(header, "")
                cell_id = f"cell-{row_idx}-{col_idx}"
                
                # First column gets row header treatment
                if col_idx == 0:
                    html += f"""
                                <th role="rowheader" 
                                    scope="row" 
                                    id="{cell_id}"
                                    headers="col-{col_idx}"
                                    tabindex="0">
                                    {value}
                                </th>
                    """
                else:
                    html += f"""
                                <td role="gridcell" 
                                    id="{cell_id}"
                                    headers="col-{col_idx}"
                                    tabindex="0">
                                    {value}
                                </td>
                    """
            
            html += '</tr>\n'
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <script>
                // Enhanced keyboard navigation
                document.addEventListener('DOMContentLoaded', function() {
                    const table = document.querySelector('table');
                    const cells = table.querySelectorAll('th, td');
                    let currentCell = 0;
                    
                    // Focus first cell initially
                    if (cells.length > 0) {
                        cells[0].focus();
                    }
                    
                    table.addEventListener('keydown', function(e) {
                        const totalCells = cells.length;
                        const cols = table.querySelectorAll('thead th').length;
                        const currentRow = Math.floor(currentCell / cols);
                        const currentCol = currentCell % cols;
                        
                        switch(e.key) {
                            case 'ArrowRight':
                                e.preventDefault();
                                if (currentCell < totalCells - 1) {
                                    currentCell++;
                                    cells[currentCell].focus();
                                }
                                break;
                                
                            case 'ArrowLeft':
                                e.preventDefault();
                                if (currentCell > 0) {
                                    currentCell--;
                                    cells[currentCell].focus();
                                }
                                break;
                                
                            case 'ArrowDown':
                                e.preventDefault();
                                if (currentCell + cols < totalCells) {
                                    currentCell += cols;
                                    cells[currentCell].focus();
                                }
                                break;
                                
                            case 'ArrowUp':
                                e.preventDefault();
                                if (currentCell - cols >= 0) {
                                    currentCell -= cols;
                                    cells[currentCell].focus();
                                }
                                break;
                                
                            case 'Home':
                                e.preventDefault();
                                if (e.ctrlKey) {
                                    // Ctrl+Home: Go to first cell
                                    currentCell = 0;
                                } else {
                                    // Home: Go to first cell in current row
                                    currentCell = currentRow * cols;
                                }
                                cells[currentCell].focus();
                                break;
                                
                            case 'End':
                                e.preventDefault();
                                if (e.ctrlKey) {
                                    // Ctrl+End: Go to last cell
                                    currentCell = totalCells - 1;
                                } else {
                                    // End: Go to last cell in current row
                                    currentCell = currentRow * cols + (cols - 1);
                                }
                                cells[currentCell].focus();
                                break;
                        }
                    });
                    
                    // Update current cell when clicking
                    cells.forEach((cell, index) => {
                        cell.addEventListener('focus', function() {
                            currentCell = index;
                        });
                    });
                });
            </script>
        </body>
        </html>
        """
        
        return html
    
    def show_standings_table(self):
        """Display MLB standings in HTML table format"""
        # Sample standings data
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
        description = "Current Major League Baseball team standings showing wins, losses, win percentage, games behind, and division information. Navigate using arrow keys or Tab."
        
        html_content = self.create_accessible_html_table(standings_data, headers, title, description)
        self.web_view.setHtml(html_content)
    
    def show_player_stats_table(self):
        """Display player statistics in HTML table format"""
        # Sample player stats data
        player_data = [
            {"Player": "Aaron Judge", "Position": "RF", "AB": "4", "R": "2", "H": "3", "RBI": "2", "BB": "1", "SO": "0", "AVG": ".311"},
            {"Player": "Gleyber Torres", "Position": "2B", "AB": "4", "R": "1", "H": "2", "RBI": "1", "BB": "0", "SO": "1", "AVG": ".279"},
            {"Player": "Anthony Rizzo", "Position": "1B", "AB": "3", "R": "0", "H": "1", "RBI": "0", "BB": "1", "SO": "1", "AVG": ".224"},
            {"Player": "Giancarlo Stanton", "Position": "DH", "AB": "4", "R": "1", "H": "1", "RBI": "2", "BB": "0", "SO": "2", "AVG": ".211"},
            {"Player": "Josh Donaldson", "Position": "3B", "AB": "4", "R": "0", "H": "0", "RBI": "0", "BB": "0", "SO": "3", "AVG": ".222"},
        ]
        
        headers = ["Player", "Position", "AB", "R", "H", "RBI", "BB", "SO", "AVG"]
        title = "Player Statistics - New York Yankees"
        description = "Individual player batting statistics for the current game. AB=At Bats, R=Runs, H=Hits, RBI=Runs Batted In, BB=Walks, SO=Strikeouts, AVG=Batting Average."
        
        html_content = self.create_accessible_html_table(player_data, headers, title, description)
        self.web_view.setHtml(html_content)
    
    def show_team_summary_table(self):
        """Display team summary statistics in HTML table format"""
        # Sample team summary data
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
        
        html_content = self.create_accessible_html_table(team_data, headers, title, description)
        self.web_view.setHtml(html_content)

def main():
    app = QApplication(sys.argv)
    
    # Create and show the widget
    widget = HTMLTableWidget()
    widget.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
