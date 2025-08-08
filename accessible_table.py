"""
Reusable accessible table widget for sports score application.
Provides consistent keyboard navigation and screen reader support.
"""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, QEvent
from typing import List, Dict, Any, Optional


class AccessibleTable(QTableWidget):
    """
    Accessible table widget with consistent keyboard navigation and screen reader support.
    
    Features:
    - Proper tab key navigation (tab to enter/exit table)
    - Arrow key navigation within table cells
    - Screen reader accessibility with proper roles and descriptions
    - Consistent styling and behavior
    - Configurable headers and data
    """
    
    def __init__(self, parent=None, accessible_name: str = "Data Table", 
                 accessible_description: str = "Data table with arrow key navigation"):
        super().__init__(parent)
        self.accessible_name = accessible_name
        self.accessible_description = accessible_description
        self._setup_accessibility()
        self._setup_behavior()
        self._setup_styling()
    
    def _setup_accessibility(self):
        """Configure accessibility features"""
        self.setAccessibleName(self.accessible_name)
        self.setAccessibleDescription(
            f"{self.accessible_description}. Use up/down/left/right arrow keys to navigate cells, "
            "Tab to enter or exit table."
        )
        
    def _setup_behavior(self):
        """Configure table behavior and keyboard navigation"""
        # Enable keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setTabKeyNavigation(False)  # We'll handle tab manually
        
        # Set selection behavior
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Disable editing
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Enable proper keyboard navigation
        self.setTextElideMode(Qt.TextElideMode.ElideRight)
        
        # Make sure focus is properly visible
        self.setStyleSheet("""
            QTableWidget::item:focus {
                background-color: #316AC5;
                color: white;
                border: 2px solid #FF6600;
            }
            QTableWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
        """)
        
    def _setup_styling(self):
        """Configure table visual styling"""
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        
    def setup_columns(self, headers: List[str], stretch_column: Optional[int] = None):
        """
        Setup table columns with headers and optional stretch column.
        
        Args:
            headers: List of column header labels
            stretch_column: Index of column that should stretch (0-based), None for auto-resize
        """
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Configure header resize modes
        header = self.horizontalHeader()
        if stretch_column is not None and 0 <= stretch_column < len(headers):
            # Set all columns to resize to contents except the stretch column
            for i in range(len(headers)):
                if i == stretch_column:
                    header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
                else:
                    header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        else:
            # Auto-resize all columns to contents
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def populate_data(self, data: List[List[Any]], set_focus: bool = True):
        """
        Populate table with data.
        
        Args:
            data: List of rows, where each row is a list of cell values
            set_focus: Whether to set focus to first cell after populating
        """
        if not data:
            self.setRowCount(0)
            return
            
        self.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_value in enumerate(row_data):
                if col_idx < self.columnCount():
                    item = QTableWidgetItem(str(cell_value))
                    
                    # Set accessible description for screen readers
                    # Include column header and cell value
                    header_text = self.horizontalHeaderItem(col_idx).text() if self.horizontalHeaderItem(col_idx) else f"Column {col_idx + 1}"
                    item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, 
                               f"{header_text}: {str(cell_value)}")
                    
                    self.setItem(row_idx, col_idx, item)
        
        # Set focus to first cell if requested and data exists
        if set_focus and data and self.rowCount() > 0 and self.columnCount() > 0:
            self.setCurrentCell(0, 0)
    
    def populate_from_dicts(self, data: List[Dict[str, Any]], headers: List[str], 
                          key_mapping: Dict[str, str] = None, set_focus: bool = True):
        """
        Populate table from list of dictionaries.
        
        Args:
            data: List of dictionaries containing row data
            headers: List of column headers (used for display and ordering)
            key_mapping: Optional mapping from header names to dictionary keys
            set_focus: Whether to set focus to first cell after populating
        """
        if not data or not headers:
            self.setRowCount(0)
            return
        
        # Setup columns first
        self.setup_columns(headers)
        
        # Convert dictionaries to list of lists based on headers
        rows = []
        for item in data:
            row = []
            for header in headers:
                # Use key mapping if provided, otherwise use header as key
                key = key_mapping.get(header, header.lower().replace(' ', '_')) if key_mapping else header.lower().replace(' ', '_')
                value = item.get(key, item.get(header, ""))
                row.append(value)
            rows.append(row)
        
        self.populate_data(rows, set_focus)
    
    def keyPressEvent(self, event):
        """
        Handle key press events for improved keyboard navigation.
        Ensures all arrow keys work properly within the table.
        """
        key = event.key()
        current_row = self.currentRow()
        current_col = self.currentColumn()
        
        # Handle arrow key navigation explicitly - process BEFORE calling parent
        if key == Qt.Key.Key_Up:
            if current_row > 0:
                self.setCurrentCell(current_row - 1, current_col)
                self.setFocus()  # Ensure focus stays on table
                event.accept()
                return
            else:
                # At top row, don't move
                event.accept()
                return
                
        elif key == Qt.Key.Key_Down:
            if current_row < self.rowCount() - 1:
                self.setCurrentCell(current_row + 1, current_col)
                self.setFocus()  # Ensure focus stays on table
                event.accept()
                return
            else:
                # At bottom row, don't move
                event.accept()
                return
                
        elif key == Qt.Key.Key_Left:
            if current_col > 0:
                self.setCurrentCell(current_row, current_col - 1)
                self.setFocus()  # Ensure focus stays on table
                event.accept()
                return
            else:
                # At leftmost column, don't move
                event.accept()
                return
                
        elif key == Qt.Key.Key_Right:
            if current_col < self.columnCount() - 1:
                self.setCurrentCell(current_row, current_col + 1)
                self.setFocus()  # Ensure focus stays on table
                event.accept()
                return
            else:
                # At rightmost column, don't move
                event.accept()
                return
        
        # Handle Tab key to exit table (let parent handle tab navigation)
        elif key == Qt.Key.Key_Tab:
            # Let the parent widget handle tab navigation to exit the table
            event.ignore()  # Let parent handle this
            return
        
        # For all other keys, let the parent handle them
        super().keyPressEvent(event)
    
    def set_stretch_column(self, column_index: int):
        """
        Set a specific column to stretch to fill available space.
        
        Args:
            column_index: 0-based index of column to stretch
        """
        if 0 <= column_index < self.columnCount():
            header = self.horizontalHeader()
            header.setSectionResizeMode(column_index, QHeaderView.ResizeMode.Stretch)
    
    def update_accessible_name(self, name: str):
        """Update the accessible name of the table"""
        self.accessible_name = name
        self.setAccessibleName(name)
    
    def update_accessible_description(self, description: str):
        """Update the accessible description of the table"""
        self.accessible_description = description
        self.setAccessibleDescription(
            f"{description}. Use up/down/left/right arrow keys to navigate cells, "
            "Tab to enter or exit table."
        )


class StandingsTable(AccessibleTable):
    """Specialized table for displaying team standings"""
    
    STANDINGS_HEADERS = ["Pos", "Team", "W", "L", "PCT", "GB", "Streak", "Record"]
    
    def __init__(self, parent=None, division_name: str = ""):
        table_name = f"{division_name} Standings" if division_name else "Standings"
        super().__init__(
            parent=parent,
            accessible_name=table_name,
            accessible_description=f"{table_name} table showing team records and statistics"
        )
        self.setup_columns(self.STANDINGS_HEADERS, stretch_column=1)  # Team name stretches
    
    def populate_standings(self, teams: List[Dict[str, Any]], set_focus: bool = True):
        """
        Populate table with standings data.
        
        Args:
            teams: List of team dictionaries with standings data
            set_focus: Whether to set focus to first cell after populating
        """
        if not teams:
            self.setRowCount(0)
            return
        
        rows = []
        for idx, team in enumerate(teams):
            row = [
                str(idx + 1),  # Position
                team.get("name", ""),
                team.get("wins", ""),
                team.get("losses", ""),
                team.get("win_pct", ""),
                team.get("games_behind", ""),
                team.get("streak", "N/A"),
                team.get("record", "")
            ]
            rows.append(row)
        
        self.populate_data(rows, set_focus)


class LeadersTable(AccessibleTable):
    """Specialized table for displaying statistical leaders"""
    
    LEADERS_HEADERS = ["Category", "Team", "Player", "Value"]
    
    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            accessible_name="Statistical Leaders",
            accessible_description="Table showing statistical leaders across various categories"
        )
        self.setup_columns(self.LEADERS_HEADERS, stretch_column=2)  # Player name stretches
    
    def populate_leaders(self, data: Dict[str, Any], set_focus: bool = True):
        """
        Populate table with leaders data.
        
        Args:
            data: Dictionary of leader categories and data
            set_focus: Whether to set focus to first cell after populating
        """
        if not data:
            self.setRowCount(0)
            return
        
        rows = []
        for category, leaders in data.items():
            if isinstance(leaders, list):
                for leader in leaders:
                    if isinstance(leader, dict):
                        rows.append([
                            category,
                            leader.get("team", ""),
                            leader.get("name", ""),
                            leader.get("value", "")
                        ])
            elif isinstance(leaders, dict):
                rows.append([
                    category,
                    leaders.get("team", ""),
                    leaders.get("name", ""),
                    leaders.get("value", "")
                ])
        
        self.populate_data(rows, set_focus)


class BoxscoreTable(AccessibleTable):
    """Specialized table for displaying boxscore data"""
    
    def __init__(self, parent=None, title: str = "Boxscore"):
        super().__init__(
            parent=parent,
            accessible_name=title,
            accessible_description=f"{title} data table with player or team statistics"
        )
        # Ensure strong focus policy for boxscore tables
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def keyPressEvent(self, event):
        """Enhanced key handling for boxscore tables"""
        key = event.key()
        
        # Handle Ctrl+Tab to switch between tabs (if in a tab widget)
        if key == Qt.Key.Key_Tab and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Let the parent tab widget handle this
            event.ignore()
            return
        
        # Use parent's arrow key navigation
        super().keyPressEvent(event)
        
    def focusInEvent(self, event):
        """Ensure proper focus handling when table receives focus"""
        super().focusInEvent(event)
        
        # If no cell is selected, select the first cell
        if self.currentRow() == -1 and self.rowCount() > 0:
            self.setCurrentCell(0, 0)
            
    def populate_data(self, data: List[List[Any]], set_focus: bool = True):
        """Override to ensure proper focus for boxscore tables"""
        super().populate_data(data, set_focus)
        
        # Ensure the table is ready for keyboard navigation
        if set_focus and self.rowCount() > 0 and self.columnCount() > 0:
            self.setCurrentCell(0, 0)
            self.setFocus()
