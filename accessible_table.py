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
                    self.setItem(row_idx, col_idx, item)
        
        # Update accessibility for all cells after populating
        for row_idx in range(self.rowCount()):
            for col_idx in range(self.columnCount()):
                self._update_cell_accessibility(row_idx, col_idx)
        
        # Set focus to first cell if requested and data exists
        if set_focus and data and self.rowCount() > 0 and self.columnCount() > 0:
            self.setCurrentCell(0, 0)
            self._update_cell_accessibility(0, 0)
    
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
                new_row = current_row - 1
                self.setCurrentCell(new_row, current_col)
                self._update_cell_accessibility(new_row, current_col)
                self.setFocus()  # Ensure focus stays on table
                event.accept()
                return
            else:
                # At top row, don't move
                event.accept()
                return
                
        elif key == Qt.Key.Key_Down:
            if current_row < self.rowCount() - 1:
                new_row = current_row + 1
                self.setCurrentCell(new_row, current_col)
                self._update_cell_accessibility(new_row, current_col)
                self.setFocus()  # Ensure focus stays on table
                event.accept()
                return
            else:
                # At bottom row, don't move
                event.accept()
                return
                
        elif key == Qt.Key.Key_Left:
            if current_col > 0:
                new_col = current_col - 1
                self.setCurrentCell(current_row, new_col)
                self._update_cell_accessibility(current_row, new_col)
                self.setFocus()  # Ensure focus stays on table
                event.accept()
                return
            else:
                # At leftmost column, don't move
                event.accept()
                return
                
        elif key == Qt.Key.Key_Right:
            if current_col < self.columnCount() - 1:
                new_col = current_col + 1
                self.setCurrentCell(current_row, new_col)
                self._update_cell_accessibility(current_row, new_col)
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
    
    def _update_cell_accessibility(self, row: int, col: int):
        """
        Update accessibility description for the current cell to include row context.
        For player tables, includes player name. For other tables, includes row identifier.
        """
        if row < 0 or row >= self.rowCount() or col < 0 or col >= self.columnCount():
            return
            
        current_item = self.item(row, col)
        if not current_item:
            return
            
        # Get the current cell value
        cell_value = current_item.text()
        
        # Get column header
        header_item = self.horizontalHeaderItem(col)
        column_name = header_item.text() if header_item else f"Column {col + 1}"
        
        # Get row context (typically from first column - player name or stat name)
        row_context = ""
        if self.columnCount() > 0:
            first_col_item = self.item(row, 0)
            if first_col_item:
                row_context = first_col_item.text()
        
        # Build enhanced accessibility description
        if row_context and col > 0:  # Don't include row context for the first column itself
            accessibility_text = f"{row_context}, {column_name}, {cell_value}"
        else:
            accessibility_text = f"{column_name}, {cell_value}"
            
        # Update the accessibility using the most compatible method
        # Many screen readers read tooltips, so this is our primary method
        current_item.setToolTip(accessibility_text)
        
        # Also try other accessibility methods for broader compatibility
        current_item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, accessibility_text)
        current_item.setData(Qt.ItemDataRole.AccessibleTextRole, accessibility_text)
        current_item.setWhatsThis(accessibility_text)  # Additional accessibility method
    
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
        """Enhanced key handling for boxscore tables with tab widget support"""
        key = event.key()
        modifiers = event.modifiers()
        
        # Handle Shift+Tab to go back to tab bar
        if key == Qt.Key.Key_Backtab or (key == Qt.Key.Key_Tab and modifiers == Qt.KeyboardModifier.ShiftModifier):
            # Find parent tab widget and focus on its tab bar
            parent = self.parent()
            while parent:
                if hasattr(parent, 'tabBar'):  # It's a QTabWidget
                    parent.tabBar().setFocus()
                    event.accept()
                    return
                parent = parent.parent()
            # If no tab widget found, let default handling occur
        
        # Handle regular Tab to move to next table in same tab or next tab
        elif key == Qt.Key.Key_Tab and modifiers == Qt.KeyboardModifier.NoModifier:
            # Find all tables in current tab
            tab_widget = None
            parent = self.parent()
            while parent:
                if hasattr(parent, 'tabBar'):  # It's a QTabWidget
                    tab_widget = parent
                    break
                parent = parent.parent()
            
            if tab_widget:
                current_widget = tab_widget.currentWidget()
                if current_widget:
                    tables = current_widget.findChildren(BoxscoreTable)
                    if len(tables) > 1:
                        # Find current table index and move to next
                        try:
                            current_index = tables.index(self)
                            next_index = (current_index + 1) % len(tables)
                            next_table = tables[next_index]
                            next_table.setFocus()
                            if next_table.rowCount() > 0:
                                next_table.setCurrentCell(0, 0)
                            event.accept()
                            return
                        except (ValueError, IndexError):
                            pass
                    
                    # If only one table or couldn't find next, go to next tab
                    current_tab = tab_widget.currentIndex()
                    next_tab = (current_tab + 1) % tab_widget.count()
                    tab_widget.setCurrentIndex(next_tab)
                    
                    # Focus first table in next tab
                    next_widget = tab_widget.currentWidget()
                    if next_widget:
                        next_tables = next_widget.findChildren(BoxscoreTable)
                        if next_tables:
                            next_tables[0].setFocus()
                            if next_tables[0].rowCount() > 0:
                                next_tables[0].setCurrentCell(0, 0)
                    event.accept()
                    return
        
        # Use parent's arrow key navigation for all other keys
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


class InjuryTable(AccessibleTable):
    """Specialized table for displaying injury report data"""
    
    def __init__(self, parent=None, title: str = "Injury Report"):
        super().__init__(
            parent=parent,
            accessible_name=title,
            accessible_description=f"{title} table showing player injuries with status and details"
        )
        # Configure for injury-specific needs
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def populate_injury_data(self, injury_data: List[Dict], set_focus: bool = True):
        """
        Populate table with injury data from ESPN API format
        
        Args:
            injury_data: List of team injury objects from ESPN API
            set_focus: Whether to set focus to first cell after population
        """
        if not injury_data:
            return
            
        # Flatten the team-based injury structure into a list of individual injuries
        all_injuries = []
        
        for team_injury in injury_data:
            team_info = team_injury.get("team", {})
            team_name = team_info.get("displayName", "Unknown Team")
            team_abbr = team_info.get("abbreviation", "")
            
            injuries = team_injury.get("injuries", [])
            for injury in injuries:
                athlete = injury.get("athlete", {})
                details = injury.get("details", {})
                
                injury_row = [
                    athlete.get("displayName", "Unknown Player"),
                    athlete.get("position", {}).get("abbreviation", ""),
                    f"{team_name} ({team_abbr})" if team_abbr else team_name,
                    injury.get("status", "Unknown"),
                    details.get("type", "Not specified"),
                    details.get("detail", "No details available"),
                    details.get("returnDate", "Unknown") if details.get("returnDate") else "TBD"
                ]
                all_injuries.append(injury_row)
        
        # Use parent's populate_data method
        self.populate_data(all_injuries, set_focus)
        
        # Set accessible description with count
        injury_count = len(all_injuries)
        team_count = len(injury_data)
        self.setAccessibleDescription(
            f"Injury report table with {injury_count} injuries across {team_count} teams. "
            "Use arrow keys to navigate between cells, Tab to exit table."
        )
        
    def enhance_cell_accessibility(self, row: int, col: int, value: Any):
        """Add injury-specific accessibility enhancements"""
        item = self.item(row, col)
        if not item:
            return
            
        # Add contextual descriptions for injury data
        player_name = self.item(row, 0).text() if self.item(row, 0) else "Unknown"
        
        if col == 3:  # Status column
            item.setAccessibleDescription(f"{player_name} injury status: {value}")
        elif col == 4:  # Type column
            item.setAccessibleDescription(f"{player_name} injury type: {value}")
        elif col == 5:  # Details column
            item.setAccessibleDescription(f"{player_name} injury details: {value}")
        elif col == 6:  # Return date column
            item.setAccessibleDescription(f"{player_name} expected return: {value}")
        else:
            item.setAccessibleDescription(f"{value}")
