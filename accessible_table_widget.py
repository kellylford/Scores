"""
Standalone Accessible Table Widget

A reusable PyQt6 widget that provides accessible table functionality with multiple view modes.
Designed for use in any application requiring accessible data display.

Features:
- Three view modes: Table, Quick List, Full List
- Universal keyboard shortcuts: Alt+V (cycle), Alt+T, Alt+Q, Alt+F
- Screen reader optimization with proper ARIA attributes
- Focus management across view switches
- Real-time data synchronization
- Customizable configuration
"""

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QStackedWidget, 
    QListWidget, QListWidgetItem, QWidget, QVBoxLayout
)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal
from typing import List, Dict, Any, Optional

# Import core interfaces and models
from accessible_table_core import TableDataModel, TableConfig, SimpleTableDataModel


class AccessibleTableWidget(QWidget):
    """
    Accessible table widget with multiple view modes and consistent keyboard navigation.
    
    This is a standalone, reusable component that can be used in any PyQt6 application
    to display tabular data in an accessible format.
    
    Features:
    - Three view modes: Table, Quick List, Full List
    - Keyboard shortcuts: Alt+V (cycle), Alt+T (table), Alt+Q (quick), Alt+F (full)
    - Proper tab key navigation and arrow key navigation
    - Screen reader accessibility with proper roles and descriptions
    - Seamless focus management across view switches
    - Real-time data synchronization across all views
    - Configurable behavior and appearance
    """
    
    # Signals
    view_changed = pyqtSignal(str)  # Emitted when view mode changes
    item_selected = pyqtSignal(dict)  # Emitted when an item is selected
    data_updated = pyqtSignal()  # Emitted when data is updated
    
    def __init__(self, parent=None, 
                 accessible_name: str = "Data Table", 
                 accessible_description: str = "Data table with arrow key navigation",
                 config: Optional[TableConfig] = None):
        """
        Initialize the accessible table widget.
        
        Args:
            parent: Parent widget
            accessible_name: Name for screen readers
            accessible_description: Description for screen readers
            config: Configuration object, uses default if None
        """
        super().__init__(parent)
        
        # Configuration
        self.config = config or TableConfig()
        self.accessible_name = accessible_name
        self.accessible_description = accessible_description
        
        # Data model
        self._data_model: Optional[TableDataModel] = None
        self._current_view = self.config.VIEW_TABLE
        
        # View mode constants for backward compatibility
        self.VIEW_TABLE = 0
        self.VIEW_QUICK_LIST = 1
        self.VIEW_FULL_LIST = 2
        
        # Setup the widget
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
        self.table_widget.setTabKeyNavigation(self.config.tab_navigation_enabled)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.setTextElideMode(Qt.TextElideMode.ElideRight)
        
        # Apply styling
        if self.config.focus_style:
            self.table_widget.setStyleSheet(self.config.focus_style)
        
        if self.config.alternate_row_colors:
            self.table_widget.setAlternatingRowColors(True)
        
        self.table_widget.verticalHeader().setVisible(False)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(self.table_widget)
    
    def _setup_list_views(self):
        """Setup the quick list and full list views"""
        # Quick List View
        self.quick_list = QListWidget()
        self.quick_list.setAccessibleName(f"{self.accessible_name} - Quick List")
        self.quick_list.setAccessibleDescription(
            f"{self.accessible_description} in quick list format. "
            "Use up/down arrow keys to navigate, Alt+V to cycle views, Alt+T for table view."
        )
        self.quick_list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.stacked_widget.addWidget(self.quick_list)
        
        # Full List View
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
        # Set the initial view to table
        self.stacked_widget.setCurrentIndex(self.VIEW_TABLE)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Install event filter to handle keyboard shortcuts
        self.installEventFilter(self)
        self.table_widget.installEventFilter(self)
        self.quick_list.installEventFilter(self)
        self.full_list.installEventFilter(self)
    
    def set_data_model(self, model: TableDataModel):
        """
        Set the data model for this table.
        
        Args:
            model: Object implementing TableDataModel protocol
        """
        self._data_model = model
        self.refresh_data()
    
    def set_simple_data(self, headers: List[str], data: List[List[Any]]):
        """
        Set data using the simple interface (no custom model required).
        
        Args:
            headers: List of column header names
            data: List of rows, where each row is a list of cell values
        """
        model = SimpleTableDataModel(headers, data)
        self.set_data_model(model)
    
    def refresh_data(self):
        """Refresh all views with current data model."""
        if not self._data_model:
            self._clear_all_views()
            return
        
        # Get data from model
        headers = self._data_model.get_columns(self.config.VIEW_TABLE)
        data = self._data_model.get_data()
        
        # Setup columns
        self._setup_columns(headers)
        
        # Populate all views
        self._populate_table_view(data)
        self._populate_list_views(data, headers)
        
        # Emit signal
        self.data_updated.emit()
    
    def _clear_all_views(self):
        """Clear all view widgets."""
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        self.quick_list.clear()
        self.full_list.clear()
    
    def _setup_columns(self, headers: List[str]):
        """Setup table columns with headers."""
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # Configure header resize modes
        header = self.table_widget.horizontalHeader()
        if (self.config.stretch_column is not None and 
            0 <= self.config.stretch_column < len(headers)):
            # Set stretch column and resize others to contents
            for i in range(len(headers)):
                if i == self.config.stretch_column:
                    header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
                else:
                    header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        else:
            # Auto-resize all columns to contents
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def _populate_table_view(self, data: List[List[Any]]):
        """Populate the table view with data."""
        if not data:
            self.table_widget.setRowCount(0)
            return
        
        self.table_widget.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_value in enumerate(row_data):
                if col_idx < self.table_widget.columnCount():
                    # Format cell value using data model
                    if self._data_model:
                        formatted_value = self._data_model.format_cell(
                            row_idx, col_idx, cell_value, self.config.VIEW_TABLE)
                    else:
                        formatted_value = str(cell_value) if cell_value is not None else ""
                    
                    item = QTableWidgetItem(formatted_value)
                    self.table_widget.setItem(row_idx, col_idx, item)
        
        # Update accessibility for all cells
        if self.config.enable_accessibility_roles:
            for row_idx in range(self.table_widget.rowCount()):
                for col_idx in range(self.table_widget.columnCount()):
                    self._update_cell_accessibility(row_idx, col_idx)
    
    def _populate_list_views(self, data: List[List[Any]], headers: List[str]):
        """Populate both list views with data."""
        if not data or not headers:
            self.quick_list.clear()
            self.full_list.clear()
            return
        
        # Clear existing items
        self.quick_list.clear()
        self.full_list.clear()
        
        # Populate both list views
        for row_idx, row_data in enumerate(data):
            # Quick List View: formatted values joined with commas
            quick_parts = []
            for col_idx, value in enumerate(row_data):
                if self._data_model:
                    formatted_value = self._data_model.format_cell(
                        row_idx, col_idx, value, self.config.VIEW_QUICK_LIST)
                else:
                    formatted_value = str(value) if value is not None else ""
                quick_parts.append(formatted_value)
            
            quick_text = ", ".join(quick_parts)
            quick_item = QListWidgetItem(quick_text)
            if self.config.enable_accessibility_roles:
                quick_item.setData(Qt.ItemDataRole.AccessibleTextRole, quick_text)
            self.quick_list.addItem(quick_item)
            
            # Full List View: "Header: Value" pairs joined with semicolons
            full_parts = []
            for col_idx, (header, value) in enumerate(zip(headers, row_data)):
                if self._data_model:
                    formatted_value = self._data_model.format_cell(
                        row_idx, col_idx, value, self.config.VIEW_FULL_LIST)
                else:
                    formatted_value = str(value) if value is not None else ""
                full_parts.append(f"{header}: {formatted_value}")
            
            full_text = "; ".join(full_parts)
            full_item = QListWidgetItem(full_text)
            if self.config.enable_accessibility_roles:
                full_item.setData(Qt.ItemDataRole.AccessibleTextRole, full_text)
            self.full_list.addItem(full_item)
    
    def _update_cell_accessibility(self, row: int, col: int):
        """Update accessibility description for a cell."""
        if (row < 0 or row >= self.table_widget.rowCount() or 
            col < 0 or col >= self.table_widget.columnCount()):
            return
        
        current_item = self.table_widget.item(row, col)
        if not current_item:
            return
        
        # Get accessibility text from data model or generate basic text
        if self._data_model:
            accessibility_text = self._data_model.get_accessibility_text(row, col)
        else:
            # Fallback to basic accessibility text generation
            cell_value = current_item.text()
            header_item = self.table_widget.horizontalHeaderItem(col)
            column_name = header_item.text() if header_item else f"Column {col + 1}"
            
            if self.config.include_row_context and col > 0:
                first_col_item = self.table_widget.item(row, 0)
                if first_col_item:
                    row_context = first_col_item.text()
                    accessibility_text = f"{row_context}, {column_name}, {cell_value}"
                else:
                    accessibility_text = f"{column_name}, {cell_value}"
            else:
                accessibility_text = f"{column_name}, {cell_value}"
        
        # Apply accessibility attributes based on configuration
        if self.config.enable_tooltips:
            current_item.setToolTip(accessibility_text)
        
        if self.config.enable_accessibility_roles:
            current_item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, accessibility_text)
            current_item.setData(Qt.ItemDataRole.AccessibleTextRole, accessibility_text)
            current_item.setWhatsThis(accessibility_text)
    
    def eventFilter(self, obj, event):
        """Handle keyboard shortcuts for view switching"""
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            
            # Handle keyboard shortcuts based on configuration
            if modifiers == Qt.KeyboardModifier.AltModifier:
                if key == Qt.Key.Key_V:  # Alt+V (cycle views)
                    self._cycle_view()
                    return True
                elif key == Qt.Key.Key_T:  # Alt+T (table view)
                    self._switch_to_view(self.config.VIEW_TABLE)
                    return True
                elif key == Qt.Key.Key_Q:  # Alt+Q (quick list view)
                    self._switch_to_view(self.config.VIEW_QUICK_LIST)
                    return True
                elif key == Qt.Key.Key_F:  # Alt+F (full list view)
                    self._switch_to_view(self.config.VIEW_FULL_LIST)
                    return True
            
            # Handle table-specific navigation
            if obj == self.table_widget:
                return self._handle_table_navigation(event)
        
        return super().eventFilter(obj, event)
    
    def _cycle_view(self):
        """Cycle through the three view modes."""
        view_modes = [self.config.VIEW_TABLE, self.config.VIEW_QUICK_LIST, self.config.VIEW_FULL_LIST]
        current_index = view_modes.index(self._current_view)
        next_index = (current_index + 1) % len(view_modes)
        self._switch_to_view(view_modes[next_index])
    
    def _switch_to_view(self, view_mode: str):
        """Switch to the specified view mode with focus management."""
        if view_mode == self._current_view:
            return
        
        # Map string view modes to indices for stacked widget
        view_index_map = {
            self.config.VIEW_TABLE: self.VIEW_TABLE,
            self.config.VIEW_QUICK_LIST: self.VIEW_QUICK_LIST,
            self.config.VIEW_FULL_LIST: self.VIEW_FULL_LIST
        }
        
        if view_mode not in view_index_map:
            return
        
        # Get current position before switching
        current_row = self._get_current_row()
        
        # Switch the view
        old_view = self._current_view
        self._current_view = view_mode
        self.stacked_widget.setCurrentIndex(view_index_map[view_mode])
        
        # Set focus and restore position
        self._set_focus_to_current_view()
        self._restore_position(current_row)
        
        # Announce the view change
        if self.config.announce_view_changes:
            self._announce_view_change(old_view, view_mode)
        
        # Emit signal
        self.view_changed.emit(view_mode)
    
    def _get_current_row(self) -> int:
        """Get the current row/item index from the active view."""
        if self._current_view == self.config.VIEW_TABLE:
            return self.table_widget.currentRow()
        elif self._current_view == self.config.VIEW_QUICK_LIST:
            return self.quick_list.currentRow()
        elif self._current_view == self.config.VIEW_FULL_LIST:
            return self.full_list.currentRow()
        return 0
    
    def _restore_position(self, row: int):
        """Restore the position in the new view."""
        if row < 0:
            row = 0
        
        if self._current_view == self.config.VIEW_TABLE:
            if row < self.table_widget.rowCount():
                self.table_widget.setCurrentCell(row, 0)
        elif self._current_view == self.config.VIEW_QUICK_LIST:
            if row < self.quick_list.count():
                self.quick_list.setCurrentRow(row)
        elif self._current_view == self.config.VIEW_FULL_LIST:
            if row < self.full_list.count():
                self.full_list.setCurrentRow(row)
    
    def _set_focus_to_current_view(self):
        """Set focus to the currently active view."""
        if self._current_view == self.config.VIEW_TABLE:
            self.table_widget.setFocus()
        elif self._current_view == self.config.VIEW_QUICK_LIST:
            self.quick_list.setFocus()
        elif self._current_view == self.config.VIEW_FULL_LIST:
            self.full_list.setFocus()
    
    def _announce_view_change(self, old_view: str, new_view: str):
        """Announce view change for screen readers."""
        view_names = {
            self.config.VIEW_TABLE: "Table View",
            self.config.VIEW_QUICK_LIST: "Quick List View",
            self.config.VIEW_FULL_LIST: "Full List View"
        }
        
        new_view_name = view_names.get(new_view, "Unknown View")
        
        # Update accessible description to announce the change
        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
            original_desc = current_widget.accessibleDescription()
            current_widget.setAccessibleDescription(
                f"Switched to {new_view_name}. {original_desc}"
            )
    
    def _handle_table_navigation(self, event):
        """Handle keyboard navigation within the table view."""
        key = event.key()
        current_row = self.table_widget.currentRow()
        current_col = self.table_widget.currentColumn()
        
        # Handle arrow key navigation
        if key == Qt.Key.Key_Up:
            if current_row > 0:
                self.table_widget.setCurrentCell(current_row - 1, current_col)
                self.table_widget.setFocus()
                return True
            return self.config.boundary_stopping
        
        elif key == Qt.Key.Key_Down:
            if current_row < self.table_widget.rowCount() - 1:
                self.table_widget.setCurrentCell(current_row + 1, current_col)
                self.table_widget.setFocus()
                return True
            return self.config.boundary_stopping
        
        elif key == Qt.Key.Key_Left:
            if current_col > 0:
                self.table_widget.setCurrentCell(current_row, current_col - 1)
                self.table_widget.setFocus()
                return True
            return self.config.boundary_stopping
        
        elif key == Qt.Key.Key_Right:
            if current_col < self.table_widget.columnCount() - 1:
                self.table_widget.setCurrentCell(current_row, current_col + 1)
                self.table_widget.setFocus()
                return True
            return self.config.boundary_stopping
        
        elif key == Qt.Key.Key_Tab:
            # Handle tab navigation based on configuration
            return not self.config.tab_navigation_enabled
        
        return False
    
    # Public API methods for compatibility and convenience
    def get_current_view(self) -> str:
        """Get the current view mode."""
        return self._current_view
    
    def set_view(self, view_mode: str):
        """Set the current view mode."""
        self._switch_to_view(view_mode)
    
    def get_current_row(self) -> int:
        """Get the current row index."""
        return self._get_current_row()
    
    def get_current_column(self) -> int:
        """Get the current column index (table view only)."""
        if self._current_view == self.config.VIEW_TABLE:
            return self.table_widget.currentColumn()
        return 0
    
    def set_current_position(self, row: int, column: int = 0):
        """Set the current position."""
        if self._current_view == self.config.VIEW_TABLE:
            self.table_widget.setCurrentCell(row, column)
        elif self._current_view == self.config.VIEW_QUICK_LIST:
            self.quick_list.setCurrentRow(row)
        elif self._current_view == self.config.VIEW_FULL_LIST:
            self.full_list.setCurrentRow(row)
    
    def has_focus(self) -> bool:
        """Check if any of the views has focus."""
        return (self.table_widget.hasFocus() or 
                self.quick_list.hasFocus() or 
                self.full_list.hasFocus() or
                super().hasFocus())
    
    def set_focus(self):
        """Set focus to the current active view."""
        self._set_focus_to_current_view()
    
    def update_accessible_name(self, name: str):
        """Update the accessible name of all views."""
        self.accessible_name = name
        self.setAccessibleName(name)
        self.table_widget.setAccessibleName(name)
        self.quick_list.setAccessibleName(f"{name} - Quick List")
        self.full_list.setAccessibleName(f"{name} - Full List")
    
    def update_accessible_description(self, description: str):
        """Update the accessible description of all views."""
        self.accessible_description = description
        self._setup_accessibility()  # Reapply accessibility setup