#!/usr/bin/env python3
"""
Comprehensive Accessible Table Explorer

This application allows interactive testing and comparison of different PyQt6 table approaches
for accessibility, specifically testing screen reader behavior and navigation patterns.

The goal is to find the best approach for accessible table navigation that properly announces
row and column headers as users navigate through cells.
"""

import sys
import os
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QGroupBox, QLabel, QPushButton, QCheckBox,
    QComboBox, QSpinBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QTextBrowser, QHeaderView, QFrame, QScrollArea, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCursor

# Try to import WebEngine for HTML table testing
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    print("PyQt6-WebEngine not available. HTML table testing will be limited.")

# Import our existing accessible table implementation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from accessible_table import AccessibleTable, BoxscoreTable
    ACCESSIBLE_TABLE_AVAILABLE = True
except ImportError:
    ACCESSIBLE_TABLE_AVAILABLE = False
    print("Local accessible_table module not available.")


class AccessibilityTestResults(QWidget):
    """Widget to display and log accessibility test results"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Accessibility Test Results & Findings")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px;")
        layout.addWidget(title)
        
        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setReadOnly(True)
        self.results_text.setPlainText(
            "Test Results Log:\n"
            "================\n"
            "Use the controls above to test different accessibility configurations.\n"
            "Results and observations will be logged here.\n\n"
        )
        layout.addWidget(self.results_text)
        
        # Clear button
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self.clear_results)
        layout.addWidget(clear_btn)
        
        self.setLayout(layout)
        
    def log_result(self, message: str):
        """Add a test result to the log"""
        cursor = self.results_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(f"{message}\n")
        self.results_text.setTextCursor(cursor)
        self.results_text.ensureCursorVisible()
        
    def clear_results(self):
        """Clear the results log"""
        self.results_text.clear()
        self.log_result("Results cleared. Ready for new tests.")


class AccessibilityControlPanel(QWidget):
    """Control panel for adjusting accessibility settings"""
    
    def __init__(self, results_widget: AccessibilityTestResults):
        super().__init__()
        self.results = results_widget
        self.test_tables = []  # Will be populated with table widgets to test
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Accessibility Control Panel")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px;")
        layout.addWidget(title)
        
        # Controls in a form layout
        form_layout = QFormLayout()
        
        # Navigation announcement mode
        self.nav_mode = QComboBox()
        self.nav_mode.addItems([
            "Row + Column + Value",
            "Column + Value only", 
            "Row + Value only",
            "Value only",
            "Full context (Row header + Column header + Value)"
        ])
        self.nav_mode.setCurrentText("Full context (Row header + Column header + Value)")
        self.nav_mode.currentTextChanged.connect(self.on_nav_mode_changed)
        form_layout.addRow("Navigation Mode:", self.nav_mode)
        
        # Include row numbers
        self.include_row_numbers = QCheckBox("Include row numbers in announcements")
        self.include_row_numbers.setChecked(False)
        self.include_row_numbers.toggled.connect(self.on_row_numbers_changed)
        form_layout.addRow("Row Numbers:", self.include_row_numbers)
        
        # Use tooltips for accessibility
        self.use_tooltips = QCheckBox("Use tooltips for screen reader text")
        self.use_tooltips.setChecked(True)
        self.use_tooltips.toggled.connect(self.on_tooltips_changed)
        form_layout.addRow("Tooltips:", self.use_tooltips)
        
        # Use accessible roles
        self.use_accessible_roles = QCheckBox("Set explicit accessible roles")
        self.use_accessible_roles.setChecked(True)
        self.use_accessible_roles.toggled.connect(self.on_accessible_roles_changed)
        form_layout.addRow("Accessible Roles:", self.use_accessible_roles)
        
        # Tab navigation behavior
        self.tab_behavior = QComboBox()
        self.tab_behavior.addItems([
            "Tab enters/exits table",
            "Tab navigates within table", 
            "Tab disabled in table"
        ])
        self.tab_behavior.setCurrentText("Tab enters/exits table")
        self.tab_behavior.currentTextChanged.connect(self.on_tab_behavior_changed)
        form_layout.addRow("Tab Behavior:", self.tab_behavior)
        
        layout.addLayout(form_layout)
        
        # Test buttons
        button_layout = QHBoxLayout()
        
        test_nav_btn = QPushButton("Test Navigation")
        test_nav_btn.clicked.connect(self.test_navigation)
        button_layout.addWidget(test_nav_btn)
        
        test_announce_btn = QPushButton("Test Announcements")
        test_announce_btn.clicked.connect(self.test_announcements)
        button_layout.addWidget(test_announce_btn)
        
        focus_first_btn = QPushButton("Focus First Cell")
        focus_first_btn.clicked.connect(self.focus_first_cell)
        button_layout.addWidget(focus_first_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def register_table(self, table_widget):
        """Register a table widget for testing"""
        self.test_tables.append(table_widget)
        
    def on_nav_mode_changed(self, mode: str):
        """Handle navigation mode change"""
        self.results.log_result(f"Navigation mode changed to: {mode}")
        self.update_table_accessibility()
        
    def on_row_numbers_changed(self, checked: bool):
        """Handle row numbers setting change"""
        self.results.log_result(f"Row numbers in announcements: {'Enabled' if checked else 'Disabled'}")
        self.update_table_accessibility()
        
    def on_tooltips_changed(self, checked: bool):
        """Handle tooltips setting change"""
        self.results.log_result(f"Tooltips for accessibility: {'Enabled' if checked else 'Disabled'}")
        self.update_table_accessibility()
        
    def on_accessible_roles_changed(self, checked: bool):
        """Handle accessible roles setting change"""
        self.results.log_result(f"Explicit accessible roles: {'Enabled' if checked else 'Disabled'}")
        self.update_table_accessibility()
        
    def on_tab_behavior_changed(self, behavior: str):
        """Handle tab behavior change"""
        self.results.log_result(f"Tab behavior changed to: {behavior}")
        for table in self.test_tables:
            if hasattr(table, 'setTabKeyNavigation'):
                if behavior == "Tab navigates within table":
                    table.setTabKeyNavigation(True)
                else:
                    table.setTabKeyNavigation(False)
                    
    def update_table_accessibility(self):
        """Update accessibility settings for all registered tables"""
        for table in self.test_tables:
            if isinstance(table, QTableWidget):
                self.update_qtable_accessibility(table)
                
    def update_qtable_accessibility(self, table: QTableWidget):
        """Update accessibility for QTableWidget"""
        nav_mode = self.nav_mode.currentText()
        include_row_nums = self.include_row_numbers.isChecked()
        use_tooltips = self.use_tooltips.isChecked()
        use_roles = self.use_accessible_roles.isChecked()
        
        # Update each cell's accessibility
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    # Get context information
                    cell_value = item.text()
                    column_header = table.horizontalHeaderItem(col).text() if table.horizontalHeaderItem(col) else f"Column {col + 1}"
                    
                    # Try to get row header (first column value as row context)
                    row_header = ""
                    if col > 0 and table.item(row, 0):
                        row_header = table.item(row, 0).text()
                    
                    # Build accessibility text based on mode
                    if nav_mode == "Row + Column + Value":
                        if include_row_nums:
                            acc_text = f"Row {row + 1}, {column_header}, {cell_value}"
                        else:
                            acc_text = f"{column_header}, {cell_value}"
                    elif nav_mode == "Column + Value only":
                        acc_text = f"{column_header}, {cell_value}"
                    elif nav_mode == "Row + Value only":
                        if row_header:
                            acc_text = f"{row_header}, {cell_value}"
                        else:
                            acc_text = f"Row {row + 1}, {cell_value}"
                    elif nav_mode == "Value only":
                        acc_text = cell_value
                    else:  # Full context
                        if row_header and col > 0:
                            acc_text = f"{row_header}, {column_header}, {cell_value}"
                        else:
                            acc_text = f"{column_header}, {cell_value}"
                    
                    # Apply accessibility settings
                    if use_tooltips:
                        item.setToolTip(acc_text)
                    
                    if use_roles:
                        item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, acc_text)
                        item.setData(Qt.ItemDataRole.AccessibleTextRole, acc_text)
                        item.setWhatsThis(acc_text)
                        
    def test_navigation(self):
        """Test navigation behavior"""
        self.results.log_result("Testing navigation behavior...")
        if self.test_tables:
            table = self.test_tables[0]  # Test first table
            if isinstance(table, QTableWidget) and table.rowCount() > 0:
                # Move through a few cells to test navigation
                table.setCurrentCell(0, 0)
                self.results.log_result(f"Focused cell (0,0): {table.item(0, 0).text() if table.item(0, 0) else 'Empty'}")
                
                if table.columnCount() > 1:
                    table.setCurrentCell(0, 1)
                    self.results.log_result(f"Moved to cell (0,1): {table.item(0, 1).text() if table.item(0, 1) else 'Empty'}")
                    
                if table.rowCount() > 1:
                    table.setCurrentCell(1, 1)
                    self.results.log_result(f"Moved to cell (1,1): {table.item(1, 1).text() if table.item(1, 1) else 'Empty'}")
                    
    def test_announcements(self):
        """Test announcement behavior"""
        self.results.log_result("Testing announcement behavior...")
        nav_mode = self.nav_mode.currentText()
        self.results.log_result(f"Current navigation mode: {nav_mode}")
        self.results.log_result(f"Row numbers included: {self.include_row_numbers.isChecked()}")
        self.results.log_result(f"Using tooltips: {self.use_tooltips.isChecked()}")
        
    def focus_first_cell(self):
        """Focus the first cell of the first table"""
        if self.test_tables:
            table = self.test_tables[0]
            if isinstance(table, QTableWidget) and table.rowCount() > 0:
                table.setFocus()
                table.setCurrentCell(0, 0)
                self.results.log_result("Focused first cell of first table")


class StandardQTableDemo(QWidget):
    """Demo of standard QTableWidget with accessibility enhancements"""
    
    def __init__(self, control_panel: AccessibilityControlPanel):
        super().__init__()
        self.control_panel = control_panel
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Standard QTableWidget with Enhanced Accessibility")
        title.setStyleSheet("font-size: 12px; font-weight: bold; margin: 5px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("This uses the standard Qt QTableWidget with enhanced accessibility settings.")
        desc.setStyleSheet("color: #666; margin: 5px; font-style: italic;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Create table
        self.table = QTableWidget()
        self.setup_sample_data()
        self.setup_accessibility()
        
        layout.addWidget(self.table)
        
        # Register with control panel
        self.control_panel.register_table(self.table)
        
        self.setLayout(layout)
        
    def setup_sample_data(self):
        """Setup sample sports data"""
        headers = ["Player", "Pos", "AB", "H", "RBI", "BA"]
        data = [
            ["TJ Friedl", "CF", "4", "1", "0", ".251"],
            ["Jonathan India", "2B", "3", "2", "1", ".267"],
            ["Tyler Stephenson", "C", "4", "0", "0", ".189"],
            ["Spencer Steer", "3B", "4", "1", "2", ".233"],
            ["Jake Meyers", "RF", "3", "0", "0", ".245"]
        ]
        
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)
                
        # Adjust column widths
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()
        
    def setup_accessibility(self):
        """Setup accessibility features"""
        self.table.setAccessibleName("Player Statistics Table")
        self.table.setAccessibleDescription(
            "Baseball player statistics with columns for Player, Position, At Bats, Hits, RBI, and Batting Average. "
            "Use arrow keys to navigate between cells."
        )
        
        # Enable focus and keyboard navigation
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.setTabKeyNavigation(False)  # We'll handle tab manually
        
        # Selection behavior
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)


class AccessibleTableDemo(QWidget):
    """Demo of our custom AccessibleTable implementation"""
    
    def __init__(self, control_panel: AccessibilityControlPanel):
        super().__init__()
        self.control_panel = control_panel
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Custom AccessibleTable Implementation")
        title.setStyleSheet("font-size: 12px; font-weight: bold; margin: 5px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("This uses our custom AccessibleTable class with built-in accessibility features.")
        desc.setStyleSheet("color: #666; margin: 5px; font-style: italic;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Create table
        if ACCESSIBLE_TABLE_AVAILABLE:
            self.table = BoxscoreTable(title="Player Statistics")
            self.setup_sample_data()
            layout.addWidget(self.table)
            
            # Register with control panel
            self.control_panel.register_table(self.table)
        else:
            error_label = QLabel("AccessibleTable not available. Please check the import.")
            error_label.setStyleSheet("color: red; margin: 20px;")
            layout.addWidget(error_label)
        
        self.setLayout(layout)
        
    def setup_sample_data(self):
        """Setup sample sports data"""
        if hasattr(self, 'table'):
            headers = ["Player", "Pos", "AB", "H", "RBI", "BA"]
            data = [
                ["TJ Friedl", "CF", "4", "1", "0", ".251"],
                ["Jonathan India", "2B", "3", "2", "1", ".267"],
                ["Tyler Stephenson", "C", "4", "0", "0", ".189"],
                ["Spencer Steer", "3B", "4", "1", "2", ".233"],
                ["Jake Meyers", "RF", "3", "0", "0", ".245"]
            ]
            
            self.table.setup_columns(headers)
            self.table.populate_data(data, set_focus=False)


class HTMLTableDemo(QWidget):
    """Demo of HTML table in QWebEngineView"""
    
    def __init__(self, control_panel: AccessibilityControlPanel):
        super().__init__()
        self.control_panel = control_panel
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("HTML Table in QWebEngineView")
        title.setStyleSheet("font-size: 12px; font-weight: bold; margin: 5px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("This renders an HTML table with full semantic markup in a web view.")
        desc.setStyleSheet("color: #666; margin: 5px; font-style: italic;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        if WEBENGINE_AVAILABLE:
            # Create web view
            self.web_view = QWebEngineView()
            self.web_view.setAccessibleName("HTML Table Viewer")
            self.web_view.setAccessibleDescription("Web view displaying HTML table with accessibility features")
            
            # Load HTML content
            self.load_html_table()
            layout.addWidget(self.web_view)
        else:
            error_label = QLabel("QWebEngineView not available. HTML table testing requires PyQt6-WebEngine.")
            error_label.setStyleSheet("color: red; margin: 20px;")
            layout.addWidget(error_label)
        
        self.setLayout(layout)
        
    def load_html_table(self):
        """Load HTML table content"""
        html_content = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Accessible Sports Table</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }
                table { border-collapse: collapse; width: 100%; background: white; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; font-weight: bold; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                tr:hover { background-color: #e6f3ff; }
                .focus-cell { background-color: #007acc !important; color: white; }
            </style>
        </head>
        <body>
            <h2>Player Statistics</h2>
            <table role="table" aria-label="Baseball player statistics">
                <thead>
                    <tr role="row">
                        <th role="columnheader" scope="col" tabindex="0">Player</th>
                        <th role="columnheader" scope="col" tabindex="0">Pos</th>
                        <th role="columnheader" scope="col" tabindex="0">AB</th>
                        <th role="columnheader" scope="col" tabindex="0">H</th>
                        <th role="columnheader" scope="col" tabindex="0">RBI</th>
                        <th role="columnheader" scope="col" tabindex="0">BA</th>
                    </tr>
                </thead>
                <tbody>
                    <tr role="row">
                        <th role="rowheader" scope="row" tabindex="0">TJ Friedl</th>
                        <td role="gridcell" tabindex="0">CF</td>
                        <td role="gridcell" tabindex="0">4</td>
                        <td role="gridcell" tabindex="0">1</td>
                        <td role="gridcell" tabindex="0">0</td>
                        <td role="gridcell" tabindex="0">.251</td>
                    </tr>
                    <tr role="row">
                        <th role="rowheader" scope="row" tabindex="0">Jonathan India</th>
                        <td role="gridcell" tabindex="0">2B</td>
                        <td role="gridcell" tabindex="0">3</td>
                        <td role="gridcell" tabindex="0">2</td>
                        <td role="gridcell" tabindex="0">1</td>
                        <td role="gridcell" tabindex="0">.267</td>
                    </tr>
                    <tr role="row">
                        <th role="rowheader" scope="row" tabindex="0">Tyler Stephenson</th>
                        <td role="gridcell" tabindex="0">C</td>
                        <td role="gridcell" tabindex="0">4</td>
                        <td role="gridcell" tabindex="0">0</td>
                        <td role="gridcell" tabindex="0">0</td>
                        <td role="gridcell" tabindex="0">.189</td>
                    </tr>
                    <tr role="row">
                        <th role="rowheader" scope="row" tabindex="0">Spencer Steer</th>
                        <td role="gridcell" tabindex="0">3B</td>
                        <td role="gridcell" tabindex="0">4</td>
                        <td role="gridcell" tabindex="0">1</td>
                        <td role="gridcell" tabindex="0">2</td>
                        <td role="gridcell" tabindex="0">.233</td>
                    </tr>
                    <tr role="row">
                        <th role="rowheader" scope="row" tabindex="0">Jake Meyers</th>
                        <td role="gridcell" tabindex="0">RF</td>
                        <td role="gridcell" tabindex="0">3</td>
                        <td role="gridcell" tabindex="0">0</td>
                        <td role="gridcell" tabindex="0">0</td>
                        <td role="gridcell" tabindex="0">.245</td>
                    </tr>
                </tbody>
            </table>
            
            <script>
                // Basic keyboard navigation for testing
                document.addEventListener('keydown', function(e) {
                    const focused = document.activeElement;
                    if (!focused || (!focused.matches('th') && !focused.matches('td'))) return;
                    
                    const table = focused.closest('table');
                    const row = focused.closest('tr');
                    const cells = Array.from(row.querySelectorAll('th, td'));
                    const rows = Array.from(table.querySelectorAll('tr'));
                    
                    const cellIndex = cells.indexOf(focused);
                    const rowIndex = rows.indexOf(row);
                    
                    let newFocus = null;
                    
                    switch(e.key) {
                        case 'ArrowRight':
                            if (cellIndex < cells.length - 1) {
                                newFocus = cells[cellIndex + 1];
                            }
                            break;
                        case 'ArrowLeft':
                            if (cellIndex > 0) {
                                newFocus = cells[cellIndex - 1];
                            }
                            break;
                        case 'ArrowDown':
                            if (rowIndex < rows.length - 1) {
                                const nextRow = rows[rowIndex + 1];
                                const nextCells = Array.from(nextRow.querySelectorAll('th, td'));
                                newFocus = nextCells[Math.min(cellIndex, nextCells.length - 1)];
                            }
                            break;
                        case 'ArrowUp':
                            if (rowIndex > 0) {
                                const prevRow = rows[rowIndex - 1];
                                const prevCells = Array.from(prevRow.querySelectorAll('th, td'));
                                newFocus = prevCells[Math.min(cellIndex, prevCells.length - 1)];
                            }
                            break;
                    }
                    
                    if (newFocus) {
                        e.preventDefault();
                        newFocus.focus();
                    }
                });
            </script>
        </body>
        </html>
        '''
        
        self.web_view.setHtml(html_content)


class TextBrowserTableDemo(QWidget):
    """Demo of HTML table in QTextBrowser"""
    
    def __init__(self, control_panel: AccessibilityControlPanel):
        super().__init__()
        self.control_panel = control_panel
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("HTML Table in QTextBrowser")
        title.setStyleSheet("font-size: 12px; font-weight: bold; margin: 5px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("This renders HTML table content in QTextBrowser for screen reader compatibility.")
        desc.setStyleSheet("color: #666; margin: 5px; font-style: italic;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Create text browser
        self.text_browser = QTextBrowser()
        self.text_browser.setAccessibleName("Text Browser Table")
        self.text_browser.setAccessibleDescription("HTML table content in text browser format")
        
        # Load HTML content
        self.load_html_content()
        layout.addWidget(self.text_browser)
        
        self.setLayout(layout)
        
    def load_html_content(self):
        """Load simplified HTML table content"""
        html_content = '''
        <h3>Player Statistics</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr style="background-color: #f2f2f2;">
                <th>Player</th>
                <th>Pos</th>
                <th>AB</th>
                <th>H</th>
                <th>RBI</th>
                <th>BA</th>
            </tr>
            <tr>
                <td><strong>TJ Friedl</strong></td>
                <td>CF</td>
                <td>4</td>
                <td>1</td>
                <td>0</td>
                <td>.251</td>
            </tr>
            <tr>
                <td><strong>Jonathan India</strong></td>
                <td>2B</td>
                <td>3</td>
                <td>2</td>
                <td>1</td>
                <td>.267</td>
            </tr>
            <tr>
                <td><strong>Tyler Stephenson</strong></td>
                <td>C</td>
                <td>4</td>
                <td>0</td>
                <td>0</td>
                <td>.189</td>
            </tr>
            <tr>
                <td><strong>Spencer Steer</strong></td>
                <td>3B</td>
                <td>4</td>
                <td>1</td>
                <td>2</td>
                <td>.233</td>
            </tr>
            <tr>
                <td><strong>Jake Meyers</strong></td>
                <td>RF</td>
                <td>3</td>
                <td>0</td>
                <td>0</td>
                <td>.245</td>
            </tr>
        </table>
        '''
        
        self.text_browser.setHtml(html_content)


class AccessibleTableExplorer(QMainWindow):
    """Main application window for testing accessible tables"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accessible Table Explorer - Qt6 Table Accessibility Testing")
        self.setGeometry(100, 100, 1400, 900)
        self.setup_ui()
        
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Qt6 Accessible Table Explorer")
        header_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2c3e50; "
            "background: #ecf0f1; padding: 10px; margin: 5px; border-radius: 5px;"
        )
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(
            "This application allows testing and comparison of different PyQt6 table approaches "
            "for accessibility. Use the control panel to adjust settings and test navigation "
            "behavior with screen readers."
        )
        desc_label.setStyleSheet("color: #666; margin: 5px; padding: 5px;")
        desc_label.setWordWrap(True)
        main_layout.addWidget(desc_label)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section: Table demos
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        
        # Tab widget for different table approaches
        self.tab_widget = QTabWidget()
        
        # Results widget (shared between all demos)
        self.results_widget = AccessibilityTestResults()
        
        # Control panel (shared between all demos)
        self.control_panel = AccessibilityControlPanel(self.results_widget)
        
        # Create demo tabs
        self.tab_widget.addTab(StandardQTableDemo(self.control_panel), "Standard QTableWidget")
        
        if ACCESSIBLE_TABLE_AVAILABLE:
            self.tab_widget.addTab(AccessibleTableDemo(self.control_panel), "Custom AccessibleTable")
        
        if WEBENGINE_AVAILABLE:
            self.tab_widget.addTab(HTMLTableDemo(self.control_panel), "HTML in WebEngine")
            
        self.tab_widget.addTab(TextBrowserTableDemo(self.control_panel), "HTML in TextBrowser")
        
        table_layout.addWidget(self.tab_widget)
        table_widget.setLayout(table_layout)
        
        # Bottom section: Controls and results
        controls_widget = QWidget()
        controls_layout = QHBoxLayout()
        
        # Control panel on left
        controls_layout.addWidget(self.control_panel, 1)
        
        # Results on right
        controls_layout.addWidget(self.results_widget, 2)
        
        controls_widget.setLayout(controls_layout)
        
        # Add to splitter
        splitter.addWidget(table_widget)
        splitter.addWidget(controls_widget)
        splitter.setSizes([600, 300])  # Give more space to tables
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Log initial state
        self.results_widget.log_result("Accessible Table Explorer started")
        self.results_widget.log_result(f"Available table types: {self.tab_widget.count()}")
        if WEBENGINE_AVAILABLE:
            self.results_widget.log_result("✓ PyQt6-WebEngine available for HTML table testing")
        else:
            self.results_widget.log_result("✗ PyQt6-WebEngine not available")
        if ACCESSIBLE_TABLE_AVAILABLE:
            self.results_widget.log_result("✓ Custom AccessibleTable available")
        else:
            self.results_widget.log_result("✗ Custom AccessibleTable not available")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties for accessibility
    app.setApplicationName("Accessible Table Explorer")
    app.setApplicationDisplayName("Qt6 Accessible Table Testing")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = AccessibleTableExplorer()
    window.show()
    
    print("Accessible Table Explorer started")
    print("Use this application to test different PyQt6 table accessibility approaches.")
    print("Focus on a table and use arrow keys for navigation.")
    print("Use Tab to move between interface elements.")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())