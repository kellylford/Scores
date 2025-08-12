"""
HTML Table Accessibility Helper

This module provides HTML-based table functionality for better accessibility
support in the Sports Scores application. HTML tables have excellent screen
reader support and follow web accessibility standards.

Usage:
    from html_table_helper import HTMLTableDialog
    
    # Show standings in an accessible HTML table
    dialog = HTMLTableDialog(standings_data, headers, "MLB Standings", parent_widget)
    dialog.exec()
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    print("PyQt6-WebEngine not available. Install it with: pip install PyQt6-WebEngine")
    WEB_ENGINE_AVAILABLE = False
    # Fallback to regular QTextBrowser 
    from PyQt6.QtWidgets import QTextBrowser

class HTMLTableDialog(QDialog):
    """Dialog that displays table data using HTML for better accessibility"""
    
    def __init__(self, data, headers, title, parent=None, description=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 1000, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Add title label
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        if WEB_ENGINE_AVAILABLE:
            # Use QWebEngineView for full HTML support
            self.web_view = QWebEngineView()
            self.web_view.setAccessibleName(f"{title} Table Viewer")
            self.web_view.setAccessibleDescription(f"Interactive HTML table displaying {title.lower()} with full accessibility support")
            
            html_content = self.create_accessible_html_table(data, headers, title, description)
            self.web_view.setHtml(html_content)
            layout.addWidget(self.web_view)
        else:
            # Fallback to QTextBrowser with HTML
            self.text_browser = QTextBrowser()
            self.text_browser.setAccessibleName(f"{title} Table Viewer")
            self.text_browser.setAccessibleDescription(f"HTML table displaying {title.lower()}")
            
            html_content = self.create_simple_html_table(data, headers, title, description)
            self.text_browser.setHtml(html_content)
            layout.addWidget(self.text_browser)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        if WEB_ENGINE_AVAILABLE:
            # Add button to export table to system browser
            export_btn = QPushButton("Open in Browser")
            export_btn.clicked.connect(self.open_in_browser)
            button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Store data for potential export
        self.table_data = data
        self.table_headers = headers
        self.table_title = title
        self.table_description = description
    
    def create_accessible_html_table(self, data, headers, title, description=""):
        """Create a fully accessible HTML table with advanced features"""
        
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
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    color: #212529;
                    line-height: 1.5;
                }}
                
                .table-container {{
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                    margin: 20px 0;
                }}
                
                .table-header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                }}
                
                .table-header h1 {{
                    margin: 0;
                    font-size: 1.75rem;
                    font-weight: 600;
                }}
                
                .table-description {{
                    padding: 15px 20px;
                    background: #e9ecef;
                    color: #6c757d;
                    font-style: italic;
                    border-bottom: 1px solid #dee2e6;
                }}
                
                .table-wrapper {{
                    overflow-x: auto;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 14px;
                    min-width: 600px;
                }}
                
                th {{
                    background: linear-gradient(to bottom, #495057, #343a40);
                    color: white;
                    padding: 12px 16px;
                    text-align: left;
                    font-weight: 600;
                    position: sticky;
                    top: 0;
                    border-bottom: 2px solid #28a745;
                    white-space: nowrap;
                }}
                
                th:first-child {{
                    border-top-left-radius: 4px;
                }}
                
                th:last-child {{
                    border-top-right-radius: 4px;
                }}
                
                td {{
                    padding: 12px 16px;
                    border-bottom: 1px solid #dee2e6;
                    vertical-align: middle;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                
                tr:hover {{
                    background-color: #e3f2fd !important;
                }}
                
                /* Enhanced focus styles for accessibility */
                table:focus {{
                    outline: 3px solid #007bff;
                    outline-offset: 2px;
                }}
                
                th:focus, td:focus {{
                    outline: 2px solid #007bff;
                    outline-offset: -2px;
                    background-color: #cce5ff !important;
                    box-shadow: inset 0 0 0 2px #007bff;
                }}
                
                /* Current cell highlight */
                .current-cell {{
                    background-color: #fff3cd !important;
                    border: 2px solid #856404 !important;
                }}
                
                /* Screen reader only content */
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
                
                /* Sort indicators */
                .sortable {{
                    cursor: pointer;
                    user-select: none;
                }}
                
                .sortable:hover {{
                    background: linear-gradient(to bottom, #5a6268, #495057);
                }}
                
                .sort-indicator {{
                    display: inline-block;
                    margin-left: 8px;
                    opacity: 0.7;
                }}
                
                /* Navigation help */
                .nav-help {{
                    padding: 10px 20px;
                    background: #d1ecf1;
                    color: #0c5460;
                    font-size: 12px;
                    border-top: 1px solid #bee5eb;
                }}
                
                /* Responsive design */
                @media (max-width: 768px) {{
                    body {{
                        padding: 10px;
                    }}
                    
                    table {{
                        font-size: 12px;
                    }}
                    
                    th, td {{
                        padding: 8px 12px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="table-container">
                <div class="table-header">
                    <h1 id="table-title">{title}</h1>
                </div>
                
                {f'<div class="table-description" id="table-desc">{description}</div>' if description else ''}
                
                <div class="table-wrapper">
                    <table 
                        role="table" 
                        aria-labelledby="table-title"
                        {f'aria-describedby="table-desc"' if description else ''}
                        tabindex="0"
                        id="main-table"
                    >
                        <caption class="sr-only">
                            {title}. {description if description else ''} 
                            Use arrow keys to navigate between cells, or Tab to move through the table. 
                            Press Space to hear cell content, Enter to select a row.
                        </caption>
                        
                        <thead>
                            <tr role="row">
        """
        
        # Add headers with sort functionality
        for i, header in enumerate(headers):
            html += f"""
                                <th role="columnheader" 
                                    scope="col" 
                                    tabindex="0"
                                    class="sortable"
                                    aria-sort="none"
                                    id="col-{i}"
                                    onclick="sortTable({i})"
                                    onkeydown="if(event.key==='Enter'||event.key===' '){{sortTable({i}); event.preventDefault();}}">
                                    {header}
                                    <span class="sort-indicator" id="sort-{i}">⇅</span>
                                </th>
            """
        
        html += """
                            </tr>
                        </thead>
                        <tbody id="table-body">
        """
        
        # Add data rows
        for row_idx, row_data in enumerate(data):
            html += f'<tr role="row" data-row="{row_idx}">\n'
            
            for col_idx, header in enumerate(headers):
                value = str(row_data.get(header, "")).strip()
                cell_id = f"cell-{row_idx}-{col_idx}"
                
                # First column gets row header treatment
                if col_idx == 0:
                    html += f"""
                                    <th role="rowheader" 
                                        scope="row" 
                                        id="{cell_id}"
                                        headers="col-{col_idx}"
                                        tabindex="0"
                                        data-value="{value}">
                                        {value}
                                    </th>
                    """
                else:
                    html += f"""
                                    <td role="gridcell" 
                                        id="{cell_id}"
                                        headers="col-{col_idx}"
                                        tabindex="0"
                                        data-value="{value}">
                                        {value}
                                    </td>
                    """
            
            html += '</tr>\n'
        
        html += f"""
                        </tbody>
                    </table>
                </div>
                
                <div class="nav-help">
                    <strong>Navigation:</strong> Use arrow keys to move between cells • Tab/Shift+Tab to navigate • 
                    Space to hear cell content • Enter to select row • Click column headers to sort • 
                    Ctrl+Home/End for first/last cell
                </div>
            </div>
            
            <script>
                let currentRow = 0;
                let currentCol = 0;
                let sortDirection = {{}};
                
                // Initialize sort direction for all columns
                {f"".join([f"sortDirection[{i}] = 'asc'; " for i in range(len(headers))])}
                
                document.addEventListener('DOMContentLoaded', function() {{
                    const table = document.getElementById('main-table');
                    const cells = table.querySelectorAll('th[role="columnheader"], th[role="rowheader"], td[role="gridcell"]');
                    const headerCells = table.querySelectorAll('th[role="columnheader"]');
                    const bodyCells = table.querySelectorAll('th[role="rowheader"], td[role="gridcell"]');
                    
                    // Focus first data cell initially (skip headers)
                    if (bodyCells.length > 0) {{
                        bodyCells[0].focus();
                        updateCurrentPosition(0, 0);
                    }}
                    
                    function updateCurrentPosition(row, col) {{
                        currentRow = row;
                        currentCol = col;
                        
                        // Remove previous current cell styling
                        document.querySelectorAll('.current-cell').forEach(cell => {{
                            cell.classList.remove('current-cell');
                        }});
                        
                        // Add current cell styling
                        const currentCell = getCellAt(row, col);
                        if (currentCell) {{
                            currentCell.classList.add('current-cell');
                        }}
                    }}
                    
                    function getCellAt(row, col) {{
                        // Account for header row (row 0 is headers, data starts at row 1)
                        const actualRow = row + 1; // +1 because row 0 is header
                        const selector = `tr:nth-child(${{actualRow + 1}}) > *:nth-child(${{col + 1}})`;
                        return table.querySelector(selector);
                    }}
                    
                    function getTotalRows() {{
                        return table.querySelectorAll('tbody tr').length;
                    }}
                    
                    function getTotalCols() {{
                        return headerCells.length;
                    }}
                    
                    // Enhanced keyboard navigation
                    table.addEventListener('keydown', function(e) {{
                        const totalRows = getTotalRows();
                        const totalCols = getTotalCols();
                        
                        switch(e.key) {{
                            case 'ArrowRight':
                                e.preventDefault();
                                if (currentCol < totalCols - 1) {{
                                    currentCol++;
                                    const nextCell = getCellAt(currentRow, currentCol);
                                    if (nextCell) {{
                                        nextCell.focus();
                                        updateCurrentPosition(currentRow, currentCol);
                                    }}
                                }}
                                break;
                                
                            case 'ArrowLeft':
                                e.preventDefault();
                                if (currentCol > 0) {{
                                    currentCol--;
                                    const prevCell = getCellAt(currentRow, currentCol);
                                    if (prevCell) {{
                                        prevCell.focus();
                                        updateCurrentPosition(currentRow, currentCol);
                                    }}
                                }}
                                break;
                                
                            case 'ArrowDown':
                                e.preventDefault();
                                if (currentRow < totalRows - 1) {{
                                    currentRow++;
                                    const downCell = getCellAt(currentRow, currentCol);
                                    if (downCell) {{
                                        downCell.focus();
                                        updateCurrentPosition(currentRow, currentCol);
                                    }}
                                }}
                                break;
                                
                            case 'ArrowUp':
                                e.preventDefault();
                                if (currentRow > 0) {{
                                    currentRow--;
                                    const upCell = getCellAt(currentRow, currentCol);
                                    if (upCell) {{
                                        upCell.focus();
                                        updateCurrentPosition(currentRow, currentCol);
                                    }}
                                }}
                                break;
                                
                            case 'Home':
                                e.preventDefault();
                                if (e.ctrlKey) {{
                                    // Ctrl+Home: Go to first cell
                                    currentRow = 0;
                                    currentCol = 0;
                                }} else {{
                                    // Home: Go to first cell in current row
                                    currentCol = 0;
                                }}
                                const homeCell = getCellAt(currentRow, currentCol);
                                if (homeCell) {{
                                    homeCell.focus();
                                    updateCurrentPosition(currentRow, currentCol);
                                }}
                                break;
                                
                            case 'End':
                                e.preventDefault();
                                if (e.ctrlKey) {{
                                    // Ctrl+End: Go to last cell
                                    currentRow = totalRows - 1;
                                    currentCol = totalCols - 1;
                                }} else {{
                                    // End: Go to last cell in current row
                                    currentCol = totalCols - 1;
                                }}
                                const endCell = getCellAt(currentRow, currentCol);
                                if (endCell) {{
                                    endCell.focus();
                                    updateCurrentPosition(currentRow, currentCol);
                                }}
                                break;
                                
                            case ' ':
                                e.preventDefault();
                                // Announce current cell content
                                const currentCell = getCellAt(currentRow, currentCol);
                                if (currentCell) {{
                                    const content = currentCell.textContent.trim();
                                    const colHeader = headerCells[currentCol].textContent.trim();
                                    // This would ideally use speech synthesis
                                    console.log(`${{colHeader}}: ${{content}}`);
                                    // Visual feedback
                                    currentCell.style.backgroundColor = '#fff3cd';
                                    setTimeout(() => {{
                                        if (!currentCell.classList.contains('current-cell')) {{
                                            currentCell.style.backgroundColor = '';
                                        }}
                                    }}, 500);
                                }}
                                break;
                                
                            case 'Enter':
                                e.preventDefault();
                                // Select/highlight entire row
                                const rowCells = table.querySelectorAll(`tbody tr:nth-child(${{currentRow + 1}}) td, tbody tr:nth-child(${{currentRow + 1}}) th`);
                                rowCells.forEach(cell => {{
                                    cell.style.backgroundColor = '#d4edda';
                                }});
                                setTimeout(() => {{
                                    rowCells.forEach(cell => {{
                                        cell.style.backgroundColor = '';
                                    }});
                                }}, 1000);
                                break;
                        }}
                    }});
                    
                    // Update current position when clicking cells
                    bodyCells.forEach((cell, index) => {{
                        cell.addEventListener('focus', function() {{
                            const row = Math.floor(index / totalCols);
                            const col = index % totalCols;
                            updateCurrentPosition(row, col);
                        }});
                    }});
                }});
                
                // Sorting functionality
                function sortTable(columnIndex) {{
                    const table = document.getElementById('main-table');
                    const tbody = table.querySelector('tbody');
                    const rows = Array.from(tbody.querySelectorAll('tr'));
                    const sortIndicator = document.getElementById(`sort-${{columnIndex}}`);
                    const isAscending = sortDirection[columnIndex] === 'asc';
                    
                    // Clear other sort indicators
                    for (let i = 0; i < {len(headers)}; i++) {{
                        if (i !== columnIndex) {{
                            document.getElementById(`sort-${{i}}`).textContent = '⇅';
                            sortDirection[i] = 'asc';
                        }}
                    }}
                    
                    // Sort rows
                    rows.sort((a, b) => {{
                        const aText = a.children[columnIndex].textContent.trim();
                        const bText = b.children[columnIndex].textContent.trim();
                        
                        // Try to parse as numbers first
                        const aNum = parseFloat(aText);
                        const bNum = parseFloat(bText);
                        
                        if (!isNaN(aNum) && !isNaN(bNum)) {{
                            return isAscending ? aNum - bNum : bNum - aNum;
                        }} else {{
                            return isAscending ? aText.localeCompare(bText) : bText.localeCompare(aText);
                        }}
                    }});
                    
                    // Update sort direction and indicator
                    sortDirection[columnIndex] = isAscending ? 'desc' : 'asc';
                    sortIndicator.textContent = isAscending ? '↓' : '↑';
                    
                    // Re-append sorted rows
                    rows.forEach(row => tbody.appendChild(row));
                    
                    // Update column aria-sort attribute
                    const header = document.getElementById(`col-${{columnIndex}}`);
                    header.setAttribute('aria-sort', isAscending ? 'descending' : 'ascending');
                    
                    // Reset other column aria-sort attributes
                    for (let i = 0; i < {len(headers)}; i++) {{
                        if (i !== columnIndex) {{
                            document.getElementById(`col-${{i}}`).setAttribute('aria-sort', 'none');
                        }}
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        return html
    
    def create_simple_html_table(self, data, headers, title, description=""):
        """Create a simpler HTML table for QTextBrowser fallback"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                
                .container {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                
                h1 {{
                    color: #2c3e50;
                    margin-top: 0;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                
                th {{
                    background-color: #34495e;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #2c3e50;
                }}
                
                td {{
                    padding: 10px 12px;
                    border: 1px solid #ddd;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                
                .description {{
                    color: #666;
                    font-style: italic;
                    margin-bottom: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                {f'<div class="description">{description}</div>' if description else ''}
                
                <table>
                    <thead>
                        <tr>
        """
        
        for header in headers:
            html += f"<th>{header}</th>"
        
        html += """
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for row_data in data:
            html += "<tr>"
            for header in headers:
                value = str(row_data.get(header, "")).strip()
                html += f"<td>{value}</td>"
            html += "</tr>"
        
        html += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def open_in_browser(self):
        """Export table to a temporary HTML file and open in system browser"""
        import tempfile
        import webbrowser
        import os
        
        # Create HTML content
        html_content = self.create_accessible_html_table(
            self.table_data, 
            self.table_headers, 
            self.table_title, 
            self.table_description
        )
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_file_path = f.name
        
        # Open in browser
        webbrowser.open(f'file://{temp_file_path}')

def show_html_table(data, headers, title, parent=None, description=""):
    """
    Convenience function to show table data in an accessible HTML dialog
    
    Args:
        data: List of dictionaries containing row data
        headers: List of column headers  
        title: Table title
        parent: Parent widget (optional)
        description: Optional table description
    """
    dialog = HTMLTableDialog(data, headers, title, parent, description)
    return dialog.exec()

# Example usage function for testing
def test_html_table():
    """Test function to demonstrate HTML table functionality"""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Sample data
    sample_data = [
        {"Team": "Yankees", "W": "95", "L": "67", "Win %": ".586", "GB": "-"},
        {"Team": "Astros", "W": "93", "L": "69", "Win %": ".574", "GB": "2.0"},
        {"Team": "Dodgers", "W": "100", "L": "62", "Win %": ".617", "GB": "-"},
    ]
    
    headers = ["Team", "W", "L", "Win %", "GB"]
    title = "MLB Standings Test"
    description = "Test HTML table with enhanced accessibility features"
    
    show_html_table(sample_data, headers, title, None, description)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_html_table()
