"""
Reusable accessible table widget for sports score application.
Provides consistent keyboard navigation and screen reader support.
"""

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QStackedWidget,
    QListWidget, QListWidgetItem, QWidget, QVBoxLayout
)
from PyQt6.QtCore import Qt, QEvent
from typing import List, Dict, Any, Optional
import settings


class AccessibleTable(QWidget):
    """
    Accessible table widget with multiple view modes and consistent keyboard navigation.
    
    Features:
    - Three view modes: Table, Quick List, Full List
    - Keyboard shortcuts: Alt+V (cycle), Alt+T (table), Alt+Q (quick), Alt+F (full)
    - Proper tab key navigation and arrow key navigation
    - Screen reader accessibility with proper roles and descriptions
    - Seamless focus management across view switches
    - Real-time data synchronization across all views
    """
    
    # View mode constants
    VIEW_TABLE = 0
    VIEW_QUICK_LIST = 1
    VIEW_FULL_LIST = 2
    
    def __init__(self, parent=None, accessible_name: str = "Data Table", 
                 accessible_description: str = "Data table with arrow key navigation"):
        super().__init__(parent)
        self.accessible_name = accessible_name
        self.accessible_description = accessible_description
        
        # Data storage
        self._headers = []
        self._data = []
        self._current_view = settings.get('default_view_mode', self.VIEW_TABLE)
        self._needs_data_sync = False
        
        # Setup the view container and individual views
        self._setup_view_container()
        self._setup_table_view()
        self._setup_list_views()
        self._setup_accessibility()
        self._setup_behavior()
    
    def _setup_view_container(self):
        """Setup the stacked widget container for multiple view modes"""
        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create stacked widget to hold different views
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        
    def _setup_table_view(self):
        """Setup the traditional table view"""
        self.table_widget = QTableWidget()
        self.table_widget.setAccessibleName(self.accessible_name)
        self.table_widget.setAccessibleDescription(
            f"{self.accessible_description}. Use up/down/left/right arrow keys to navigate cells, "
            "Tab to enter or exit table. Alt+V to cycle views, Alt+Q for quick list, Alt+F for full list."
        )
        
        # Configure table behavior
        self.table_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table_widget.setTabKeyNavigation(False)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setTextElideMode(Qt.TextElideMode.ElideRight)
        
        # Apply styling
        self.table_widget.setStyleSheet("""
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
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.verticalHeader().setVisible(False)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(self.table_widget)
        
    def _setup_list_views(self):
        """Setup the quick list and full list views"""
        # Quick List View (values only)
        self.quick_list = QListWidget()
        self.quick_list.setAccessibleName(f"{self.accessible_name} - Quick List")
        self.quick_list.setAccessibleDescription(
            f"{self.accessible_description} in quick list format. "
            "Use up/down arrow keys to navigate, Alt+V to cycle views, Alt+T for table view."
        )
        self.quick_list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.stacked_widget.addWidget(self.quick_list)
        
        # Full List View (header-value pairs)
        self.full_list = QListWidget()
        self.full_list.setAccessibleName(f"{self.accessible_name} - Full List")
        self.full_list.setAccessibleDescription(
            f"{self.accessible_description} in detailed list format with headers. "
            "Use up/down arrow keys to navigate, Alt+V to cycle views, Alt+T for table view."
        )
        self.full_list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.stacked_widget.addWidget(self.full_list)
        
    def _setup_accessibility(self):
        """Configure accessibility features"""
        self.setAccessibleName(self.accessible_name)
        self.setAccessibleDescription(
            f"{self.accessible_description}. Multiple view modes available: "
            "Alt+V to cycle views, Alt+T for table, Alt+Q for quick list, Alt+F for full list."
        )
        
    def _setup_behavior(self):
        """Configure table behavior and keyboard navigation"""
        # Set the initial view to the user's saved preference
        self.stacked_widget.setCurrentIndex(self._current_view)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Install event filter to handle keyboard shortcuts
        self.installEventFilter(self)
        self.table_widget.installEventFilter(self)
        self.quick_list.installEventFilter(self)
        self.full_list.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """Handle keyboard shortcuts for view switching"""
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            
            # Handle Alt+V (cycle views)
            if modifiers == Qt.KeyboardModifier.AltModifier and key == Qt.Key.Key_V:
                self._cycle_view()
                return True
                
            # Handle Alt+T (table view)
            elif modifiers == Qt.KeyboardModifier.AltModifier and key == Qt.Key.Key_T:
                self._switch_to_view(self.VIEW_TABLE)
                return True
                
            # Handle Alt+Q (quick list view)
            elif modifiers == Qt.KeyboardModifier.AltModifier and key == Qt.Key.Key_Q:
                self._switch_to_view(self.VIEW_QUICK_LIST)
                return True
                
            # Handle Alt+F (full list view)
            elif modifiers == Qt.KeyboardModifier.AltModifier and key == Qt.Key.Key_F:
                self._switch_to_view(self.VIEW_FULL_LIST)
                return True
                
            # Handle table-specific navigation for the table widget
            elif obj == self.table_widget:
                return self._handle_table_navigation(event)
        
        return super().eventFilter(obj, event)
        
    def _cycle_view(self):
        """Cycle through the three view modes"""
        next_view = (self._current_view + 1) % 3
        self._switch_to_view(next_view)
        
    def _switch_to_view(self, view_mode: int):
        """Switch to the specified view mode with focus management"""
        if view_mode == self._current_view:
            return
        
        # Sync data from table if needed before switching to list views
        if self._needs_data_sync and (view_mode == self.VIEW_QUICK_LIST or view_mode == self.VIEW_FULL_LIST):
            self._sync_data_from_table()
            
        # Get current position before switching
        current_row = self._get_current_row()
        
        # Switch the view
        old_view = self._current_view
        self._current_view = view_mode
        self.stacked_widget.setCurrentIndex(view_mode)
        settings.set('default_view_mode', view_mode)
        
        # Set focus to the new view and restore position
        self._set_focus_to_current_view()
        self._restore_position(current_row)
        
        # Announce the view change
        self._announce_view_change(old_view, view_mode)
        
    def _get_current_row(self) -> int:
        """Get the current row/item index from the active view"""
        if self._current_view == self.VIEW_TABLE:
            return self.table_widget.currentRow()
        elif self._current_view == self.VIEW_QUICK_LIST:
            return self.quick_list.currentRow()
        elif self._current_view == self.VIEW_FULL_LIST:
            return self.full_list.currentRow()
        return 0
        
    def _restore_position(self, row: int):
        """Restore the position in the new view"""
        if row < 0:
            row = 0
            
        if self._current_view == self.VIEW_TABLE:
            if row < self.table_widget.rowCount():
                self.table_widget.setCurrentCell(row, 0)
        elif self._current_view == self.VIEW_QUICK_LIST:
            if row < self.quick_list.count():
                self.quick_list.setCurrentRow(row)
        elif self._current_view == self.VIEW_FULL_LIST:
            if row < self.full_list.count():
                self.full_list.setCurrentRow(row)
                
    def _set_focus_to_current_view(self):
        """Set focus to the currently active view"""
        if self._current_view == self.VIEW_TABLE:
            self.table_widget.setFocus()
        elif self._current_view == self.VIEW_QUICK_LIST:
            self.quick_list.setFocus()
        elif self._current_view == self.VIEW_FULL_LIST:
            self.full_list.setFocus()
            
    def _announce_view_change(self, old_view: int, new_view: int):
        """Announce view change for screen readers"""
        view_names = {
            self.VIEW_TABLE: "Table View",
            self.VIEW_QUICK_LIST: "Quick List View", 
            self.VIEW_FULL_LIST: "Full List View"
        }
        
        new_view_name = view_names.get(new_view, "Unknown View")
        
        # Update accessible description to announce the change
        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
            current_widget.setAccessibleDescription(
                f"Switched to {new_view_name}. {current_widget.accessibleDescription()}"
            )
        
    def _handle_table_navigation(self, event):
        """Handle keyboard navigation within the table view"""
        key = event.key()
        current_row = self.table_widget.currentRow()
        current_col = self.table_widget.currentColumn()
        
        # Handle arrow key navigation explicitly
        if key == Qt.Key.Key_Up:
            if current_row > 0:
                new_row = current_row - 1
                self.table_widget.setCurrentCell(new_row, current_col)
                self.table_widget.setFocus()
                return True
            return True  # Prevent default behavior at boundary
                
        elif key == Qt.Key.Key_Down:
            if current_row < self.table_widget.rowCount() - 1:
                new_row = current_row + 1
                self.table_widget.setCurrentCell(new_row, current_col)
                self.table_widget.setFocus()
                return True
            return True  # Prevent default behavior at boundary
                
        elif key == Qt.Key.Key_Left:
            if current_col > 0:
                new_col = current_col - 1
                self.table_widget.setCurrentCell(current_row, new_col)
                self.table_widget.setFocus()
                return True
            return True  # Prevent default behavior at boundary
                
        elif key == Qt.Key.Key_Right:
            if current_col < self.table_widget.columnCount() - 1:
                new_col = current_col + 1
                self.table_widget.setCurrentCell(current_row, new_col)
                self.table_widget.setFocus()
                return True
            return True  # Prevent default behavior at boundary
        
        # Handle Tab key to exit table
        elif key == Qt.Key.Key_Tab:
            # Let the parent widget handle tab navigation to exit the table
            return False  # Allow default tab handling
        
        return False  # Let table handle other keys normally
        
    def setup_columns(self, headers: List[str], stretch_column: Optional[int] = None):
        """
        Setup table columns with headers and optional stretch column.
        
        Args:
            headers: List of column header labels
            stretch_column: Index of column that should stretch (0-based), None for auto-resize
        """
        self._headers = headers.copy()
        
        # Setup the table widget columns
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # Configure header resize modes
        header = self.table_widget.horizontalHeader()
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
        Populate all views with data.
        
        Args:
            data: List of rows, where each row is a list of cell values
            set_focus: Whether to set focus to first cell after populating
        """
        self._data = data.copy() if data else []
        
        # Populate table view
        self._populate_table_view(data, set_focus)
        
        # Populate list views
        self._populate_list_views(data)
        
    def _populate_table_view(self, data: List[List[Any]], set_focus: bool):
        """Populate the table view with data"""
        if not data:
            self.table_widget.setRowCount(0)
            return
            
        self.table_widget.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_value in enumerate(row_data):
                if col_idx < self.table_widget.columnCount():
                    item = QTableWidgetItem(str(cell_value))
                    self.table_widget.setItem(row_idx, col_idx, item)
        
        # Update accessibility for all cells after populating
        for row_idx in range(self.table_widget.rowCount()):
            for col_idx in range(self.table_widget.columnCount()):
                self._update_cell_accessibility(row_idx, col_idx)
        
        # Set focus to first cell if requested and data exists
        if set_focus and data and self.table_widget.rowCount() > 0 and self.table_widget.columnCount() > 0:
            self.table_widget.setCurrentCell(0, 0)
            if self._current_view == self.VIEW_TABLE:
                self.table_widget.setFocus()
            
    def _populate_list_views(self, data: List[List[Any]]):
        """Populate both list views with data"""
        if not data or not self._headers:
            self.quick_list.clear()
            self.full_list.clear()
            return
            
        # Clear existing items
        self.quick_list.clear()
        self.full_list.clear()
        
        # Populate both list views
        for row_data in data:
            # Quick List View: "Value1, Value2, Value3..."
            quick_text = ", ".join(str(value) for value in row_data)
            quick_item = QListWidgetItem(quick_text)
            quick_item.setData(Qt.ItemDataRole.AccessibleTextRole, quick_text)
            self.quick_list.addItem(quick_item)
            
            # Full List View: "Header1: Value1; Header2: Value2; Header3: Value3"
            full_parts = []
            for header, value in zip(self._headers, row_data):
                full_parts.append(f"{header}: {value}")
            full_text = "; ".join(full_parts)
            full_item = QListWidgetItem(full_text)
            full_item.setData(Qt.ItemDataRole.AccessibleTextRole, full_text)
            self.full_list.addItem(full_item)
    
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
            self.table_widget.setRowCount(0)
            self.quick_list.clear()
            self.full_list.clear()
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
    
    def _update_cell_accessibility(self, row: int, col: int):
        """
        Update accessibility description for the current cell to include row context.
        For player tables, includes player name. For other tables, includes row identifier.
        """
        if row < 0 or row >= self.table_widget.rowCount() or col < 0 or col >= self.table_widget.columnCount():
            return
            
        current_item = self.table_widget.item(row, col)
        if not current_item:
            return
            
        # Get the current cell value
        cell_value = current_item.text()
        
        # Get column header
        header_item = self.table_widget.horizontalHeaderItem(col)
        column_name = header_item.text() if header_item else f"Column {col + 1}"
        
        # Get row context (typically from first column - player name or stat name)
        row_context = ""
        if self.table_widget.columnCount() > 0:
            first_col_item = self.table_widget.item(row, 0)
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
        if 0 <= column_index < self.table_widget.columnCount():
            header = self.table_widget.horizontalHeader()
            header.setSectionResizeMode(column_index, QHeaderView.ResizeMode.Stretch)
    
    def update_accessible_name(self, name: str):
        """Update the accessible name of the table and all views"""
        self.accessible_name = name
        self.setAccessibleName(name)
        self.table_widget.setAccessibleName(name)
        self.quick_list.setAccessibleName(f"{name} - Quick List")
        self.full_list.setAccessibleName(f"{name} - Full List")
    
    def update_accessible_description(self, description: str):
        """Update the accessible description of the table and all views"""
        self.accessible_description = description
        base_desc = f"{description}. Multiple view modes available: Alt+V to cycle views, Alt+T for table, Alt+Q for quick list, Alt+F for full list."
        self.setAccessibleDescription(base_desc)
        
        self.table_widget.setAccessibleDescription(
            f"{description}. Use up/down/left/right arrow keys to navigate cells, "
            "Tab to enter or exit table. Alt+V to cycle views, Alt+Q for quick list, Alt+F for full list."
        )
        self.quick_list.setAccessibleDescription(
            f"{description} in quick list format. Use up/down arrow keys to navigate, Alt+V to cycle views, Alt+T for table view."
        )
        self.full_list.setAccessibleDescription(
            f"{description} in detailed list format with headers. Use up/down arrow keys to navigate, Alt+V to cycle views, Alt+T for table view."
        )
        
    # Compatibility methods for existing code that expects QTableWidget interface
    def rowCount(self):
        """Return the number of rows in the table"""
        return self.table_widget.rowCount()
        
    def columnCount(self):
        """Return the number of columns in the table"""
        return self.table_widget.columnCount()
        
    def setRowCount(self, rows: int):
        """Set the number of rows in the table"""
        self.table_widget.setRowCount(rows)
        
    def setColumnCount(self, columns: int):
        """Set the number of columns in the table"""
        self.table_widget.setColumnCount(columns)
        
    def item(self, row: int, column: int):
        """Get the item at the specified row and column"""
        return self.table_widget.item(row, column)
        
    def setItem(self, row: int, column: int, item):
        """Set the item at the specified row and column and sync internal data"""
        self.table_widget.setItem(row, column, item)
        # Mark that data needs to be synced
        self._needs_data_sync = True
        
    def _sync_data_from_table(self):
        """Sync internal _data list from table widget contents"""
        self._data = []
        for row in range(self.table_widget.rowCount()):
            row_data = []
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                row_data.append(item.text() if item else "")
            self._data.append(row_data)
        
        # Refresh list views if we have headers
        if self._headers:
            self._populate_list_views(self._data)
        
        self._needs_data_sync = False
        
    def currentRow(self):
        """Get the current row in the active view"""
        return self._get_current_row()
        
    def currentColumn(self):
        """Get the current column (only applicable to table view)"""
        if self._current_view == self.VIEW_TABLE:
            return self.table_widget.currentColumn()
        return 0
        
    def setCurrentCell(self, row: int, column: int):
        """Set the current cell (only applicable to table view)"""
        if self._current_view == self.VIEW_TABLE:
            self.table_widget.setCurrentCell(row, column)
            
    def hasFocus(self):
        """Check if any of the views has focus"""
        return (self.table_widget.hasFocus() or 
                self.quick_list.hasFocus() or 
                self.full_list.hasFocus() or
                super().hasFocus())
                
    def setFocus(self):
        """Set focus to the current active view"""
        self._set_focus_to_current_view()
        
    def horizontalHeaderItem(self, column: int):
        """Get the horizontal header item for the specified column"""
        return self.table_widget.horizontalHeaderItem(column)
        
    def horizontalHeader(self):
        """Get the horizontal header"""
        return self.table_widget.horizontalHeader()
    
    def setHorizontalHeaderLabels(self, labels: List[str]):
        """Set the horizontal header labels and update internal headers list"""
        self._headers = labels.copy()
        self.table_widget.setHorizontalHeaderLabels(labels)
        # If data already exists, refresh the list views
        if self._data:
            self._populate_list_views(self._data)
    
    # Expose table widget signals for compatibility
    @property
    def itemActivated(self):
        """Signal emitted when an item is activated (double-clicked or Enter pressed)"""
        return self.table_widget.itemActivated
    
    @property
    def itemClicked(self):
        """Signal emitted when an item is clicked"""
        return self.table_widget.itemClicked
    
    @property
    def itemSelectionChanged(self):
        """Signal emitted when the item selection changes"""
        return self.table_widget.itemSelectionChanged
    
    @property
    def currentCellChanged(self):
        """Signal emitted when the current cell changes"""
        return self.table_widget.currentCellChanged


class StandingsTable(AccessibleTable):
    """Specialized table for displaying team standings with basic/expanded views"""
    
    BASIC_HEADERS = ["Pos", "Team", "W", "L", "PCT", "GB", "Streak"]
    
    # Sport-specific basic headers (for sports with ties)
    BASIC_HEADERS_WITH_TIES = ["Pos", "Team", "W", "L", "T", "PCT", "GB", "Streak"]
    
    # Sport-specific expanded headers
    EXPANDED_HEADERS = {
        "MLB": ["Pos", "Team", "W", "L", "PCT", "GB", "Streak", "R", "RA", "Diff", "Home", "Road", "Playoff%", "Magic#"],
        "NFL": ["Pos", "Team", "W", "L", "T", "PCT", "GB", "Streak", "PF", "PA", "Diff", "Div Rec", "Seed"],
        "NBA": ["Pos", "Team", "W", "L", "PCT", "GB", "Streak", "PPG", "OppPPG", "Diff", "DivW%", "Seed"],
        "NHL": ["Pos", "Team", "W", "L", "OTL", "PCT", "GB", "Streak", "Pts", "GF", "GA", "Diff", "Seed"],
        "default": BASIC_HEADERS
    }
    
    def __init__(self, parent=None, division_name: str = "", league: str = "", expanded: bool = False):
        table_name = f"{division_name} Standings" if division_name else "Standings"
        super().__init__(
            parent=parent,
            accessible_name=table_name,
            accessible_description=f"{table_name} table showing team records and statistics"
        )
        self.league = league
        self.expanded = expanded
        self.division_name = division_name
        
        # Setup columns based on view mode
        if expanded:
            headers = self.EXPANDED_HEADERS.get(league, self.BASIC_HEADERS)
        else:
            # Use ties column for NFL in basic view
            headers = self.BASIC_HEADERS_WITH_TIES if league == "NFL" else self.BASIC_HEADERS
        self.setup_columns(headers, stretch_column=1)  # Team name stretches
    
    def set_expanded_view(self, expanded: bool):
        """Toggle between basic and expanded view"""
        if self.expanded == expanded:
            return
            
        # Remember if we had focus before the change
        had_focus = self.hasFocus()
        current_row = self.currentRow()
        current_col = self.currentColumn()
            
        self.expanded = expanded
        
        # Get appropriate headers
        if expanded:
            headers = self.EXPANDED_HEADERS.get(self.league, self.BASIC_HEADERS)
        else:
            headers = self.BASIC_HEADERS_WITH_TIES if self.league == "NFL" else self.BASIC_HEADERS
        
        # Clear and reconfigure table
        self.setRowCount(0)
        self.setColumnCount(0)
        self.setup_columns(headers, stretch_column=1)
        
        # Restore focus if we had it before
        if had_focus:
            self.setFocus()
        
        # Force a visual update
        self.update()
        self.repaint()
    
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
            if self.expanded:
                row = self._build_expanded_row(idx + 1, team)
            else:
                row = self._build_basic_row(idx + 1, team)
            rows.append(row)
        
        self.populate_data(rows, set_focus)
    
    def _build_basic_row(self, position: int, team: Dict[str, Any]) -> List[str]:
        """Build basic standings row"""
        # Handle different field name formats from API vs StandingsData model
        team_name = team.get("team_name") or team.get("name", "")
        wins = str(team.get("wins", ""))
        losses = str(team.get("losses", ""))
        ties = team.get("ties", 0)
        
        # Format win percentage properly
        win_pct = team.get("win_percentage") or team.get("win_pct", "")
        if isinstance(win_pct, (int, float)) and win_pct > 0:
            win_pct = f"{win_pct:.3f}"
        
        games_back = team.get("games_back") or team.get("games_behind", "")
        streak = team.get("streak", "N/A")
        
        # NFL includes ties column
        if self.league == "NFL":
            return [
                str(position),
                team_name,
                wins,
                losses,
                str(ties),
                win_pct,
                games_back,
                streak
            ]
        else:
            return [
                str(position),
                team_name,
                wins,
                losses,
                win_pct,
                games_back,
                streak
            ]
    
    def _build_expanded_row(self, position: int, team: Dict[str, Any]) -> List[str]:
        """Build expanded standings row based on sport"""
        basic_row = self._build_basic_row(position, team)
        
        if self.league == "MLB":
            return basic_row + [
                str(team.get("runs_for", "")),
                str(team.get("runs_against", "")),
                self._format_differential(team.get("run_differential", 0)),
                self._format_record(team.get("home_wins", 0), team.get("home_losses", 0)),
                self._format_record(team.get("road_wins", 0), team.get("road_losses", 0)),
                self._format_percentage(team.get("playoff_percent", 0)),
                self._format_magic_number(team.get("magic_number"))
            ]
        elif self.league == "NFL":
            # Basic row already includes ties for NFL, so just add expanded stats
            return basic_row + [
                str(team.get("points_for", "")),
                str(team.get("points_against", "")),
                self._format_differential(team.get("point_differential", 0)),
                self._format_record(team.get("division_wins", 0), team.get("division_losses", 0)),
                self._format_seed(team.get("playoff_seed"))
            ]
        elif self.league == "NBA":
            return basic_row + [
                self._format_average(team.get("avg_points_for", 0)),
                self._format_average(team.get("avg_points_against", 0)),
                str(team.get("point_differential", "")),
                self._format_percentage(team.get("division_win_percent", 0) * 100),  # Convert to percentage
                self._format_seed(team.get("playoff_seed"))
            ]
        elif self.league == "NHL":
            return basic_row + [
                str(team.get("points", "")),
                str(team.get("ot_losses", "")),
                str(team.get("goals_for", "")),
                str(team.get("goals_against", "")),
                self._format_differential(team.get("goal_differential", 0)),
                self._format_seed(team.get("playoff_seed"))
            ]
        else:
            return basic_row
    
    def _format_differential(self, value: int) -> str:
        """Format differential with +/- sign"""
        if value > 0:
            return f"+{value}"
        elif value < 0:
            return str(value)
        else:
            return "0"
    
    def _format_record(self, wins: int, losses: int) -> str:
        """Format win-loss record"""
        return f"{wins}-{losses}"
    
    def _format_percentage(self, value: float) -> str:
        """Format percentage"""
        if value > 0:
            return f"{value:.1f}%"
        return "—"
    
    def _format_average(self, value: float) -> str:
        """Format average with 1 decimal place"""
        if value > 0:
            return f"{value:.1f}"
        return "—"
    
    def _format_magic_number(self, value) -> str:
        """Format magic number"""
        if value and value > 0:
            return str(value)
        return "—"
    
    def _format_seed(self, value) -> str:
        """Format playoff seed"""
        if value and value > 0:
            return str(value)
        return "—"
    
    def _update_cell_accessibility(self, row: int, col: int):
        """
        Override accessibility for standings to use team name as context instead of position.
        """
        if row < 0 or row >= self.table_widget.rowCount() or col < 0 or col >= self.table_widget.columnCount():
            return
            
        current_item = self.table_widget.item(row, col)
        if not current_item:
            return
            
        # Get the current cell value
        cell_value = current_item.text()
        
        # Get column header
        header_item = self.table_widget.horizontalHeaderItem(col)
        column_name = header_item.text() if header_item else f"Column {col + 1}"
        
        # Get team name from column 1 (index 1) instead of position from column 0
        team_context = ""
        if self.table_widget.columnCount() > 1:
            team_col_item = self.table_widget.item(row, 1)  # Team name is in column 1
            if team_col_item:
                team_context = team_col_item.text()
        
        # Build enhanced accessibility description
        if team_context and col != 1:  # Don't include team context for the team column itself
            accessibility_text = f"{team_context}, {column_name}, {cell_value}"
        else:
            accessibility_text = f"{column_name}, {cell_value}"
            
        # Update the accessibility using the most compatible method
        current_item.setToolTip(accessibility_text)
        current_item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, accessibility_text)
        current_item.setData(Qt.ItemDataRole.AccessibleTextRole, accessibility_text)
        current_item.setWhatsThis(accessibility_text)


class WildCardTable(StandingsTable):
    """MLB wild card race: division leaders first, then the ranked race.

    Two things differ from a division table. Row order is MLB's official
    `wildCardRank` rather than a re-sort by win percentage, so the published
    tiebreakers survive; and the playoff cut line lives in a Status column
    ("Wild card 1", "AL East leader") instead of a drawn separator, so a screen
    reader speaks who is in rather than relying on a line nobody can hear.
    """

    WILDCARD_HEADERS = ["Pos", "Team", "W", "L", "PCT", "WCGB", "Streak", "Status"]

    def __init__(self, parent=None, division_name: str = ""):
        super().__init__(parent=parent, division_name=division_name)
        # StandingsTable set up the division headers; swap in the wild card set.
        self.setRowCount(0)
        self.setColumnCount(0)
        self.setup_columns(self.WILDCARD_HEADERS, stretch_column=1)

    def set_expanded_view(self, expanded: bool):
        """No expanded variant — the wild card columns are the whole story."""
        return

    def _build_basic_row(self, position: int, team: Dict[str, Any]) -> List[str]:
        return [
            str(team.get("wc_position") or position),
            team.get("team_name") or team.get("name", ""),
            str(team.get("wins", "")),
            str(team.get("losses", "")),
            str(team.get("win_percentage", "")),
            str(team.get("games_back", "")),
            team.get("streak") or "-",
            team.get("wc_status") or "-",
        ]

    def _build_expanded_row(self, position: int, team: Dict[str, Any]) -> List[str]:
        return self._build_basic_row(position, team)


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
        
    def focusInEvent(self, event):
        """Ensure proper focus handling when table receives focus"""
        super().focusInEvent(event)
        
        # If no cell is selected, select the first cell
        if self.table_widget.currentRow() == -1 and self.table_widget.rowCount() > 0:
            self.table_widget.setCurrentCell(0, 0)
            
    def populate_data(self, data: List[List[Any]], set_focus: bool = True):
        """Override to ensure proper focus for boxscore tables"""
        super().populate_data(data, set_focus)
        
        # Ensure the table is ready for keyboard navigation
        if set_focus and self.table_widget.rowCount() > 0 and self.table_widget.columnCount() > 0:
            self.table_widget.setCurrentCell(0, 0)
            if self._current_view == self.VIEW_TABLE:
                self.table_widget.setFocus()


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
        self.update_accessible_description(
            f"Injury report table with {injury_count} injuries across {team_count} teams. "
            "Use arrow keys to navigate between cells, Tab to exit table."
        )
        
    def enhance_cell_accessibility(self, row: int, col: int, value: Any):
        """Add injury-specific accessibility enhancements"""
        item = self.table_widget.item(row, col)
        if not item:
            return
            
        # Add contextual descriptions for injury data
        player_name_item = self.table_widget.item(row, 0)
        player_name = player_name_item.text() if player_name_item else "Unknown"
        
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
