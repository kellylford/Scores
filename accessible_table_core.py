"""
Core interfaces and data models for Accessible Table Widget

This module contains the GUI-independent parts that can be imported and tested
without requiring PyQt6 to be fully functional.
"""

from typing import List, Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod


class TableDataModel(Protocol):
    """
    Protocol defining the interface for table data models.
    
    Implement this interface to provide data to the AccessibleTableWidget.
    """
    
    def get_columns(self, view_mode: str) -> List[str]:
        """
        Get column definitions for the specified view mode.
        
        Args:
            view_mode: One of "table", "quick", "full"
            
        Returns:
            List of column header names
        """
        ...
    
    def get_data(self) -> List[List[Any]]:
        """
        Get the raw data as a list of rows.
        
        Returns:
            List where each item is a row (list of cell values)
        """
        ...
    
    def format_cell(self, row: int, column: int, value: Any, view_mode: str) -> str:
        """
        Format a cell value for display in the specified view mode.
        
        Args:
            row: Row index
            column: Column index  
            value: Raw cell value
            view_mode: One of "table", "quick", "full"
            
        Returns:
            Formatted string for display
        """
        ...
    
    def get_accessibility_text(self, row: int, column: int) -> str:
        """
        Get accessibility-enhanced text for a cell.
        
        Args:
            row: Row index
            column: Column index
            
        Returns:
            Text optimized for screen readers
        """
        ...


class TableConfig:
    """Configuration class for customizing AccessibleTableWidget behavior."""
    
    def __init__(self):
        # View mode constants
        self.VIEW_TABLE = "table"
        self.VIEW_QUICK_LIST = "quick"
        self.VIEW_FULL_LIST = "full"
        
        # Keyboard shortcuts
        self.shortcut_cycle_views = "Alt+V"
        self.shortcut_table_view = "Alt+T"
        self.shortcut_quick_view = "Alt+Q"
        self.shortcut_full_view = "Alt+F"
        
        # Accessibility settings
        self.enable_tooltips = True
        self.enable_accessibility_roles = True
        self.announce_view_changes = True
        self.include_row_context = True
        self.include_column_headers = True
        
        # Visual settings
        self.alternate_row_colors = True
        self.stretch_column = None  # None = auto-resize, int = column index to stretch
        self.focus_style = """
            QTableWidget::item:focus {
                background-color: #316AC5;
                color: white;
                border: 2px solid #FF6600;
            }
            QTableWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
        """
        
        # Navigation settings
        self.tab_navigation_enabled = False
        self.boundary_stopping = True  # Stop at table edges instead of wrapping


class SimpleTableDataModel:
    """
    Simple implementation of TableDataModel for basic use cases.
    
    This provides a straightforward way to use the AccessibleTableWidget
    without implementing the full protocol.
    """
    
    def __init__(self, headers: List[str], data: List[List[Any]]):
        """
        Initialize with headers and data.
        
        Args:
            headers: List of column header names
            data: List of rows, where each row is a list of cell values
        """
        self._headers = headers.copy()
        self._data = [row.copy() for row in data] if data else []
    
    def get_columns(self, view_mode: str) -> List[str]:
        """Return the same headers for all view modes."""
        return self._headers.copy()
    
    def get_data(self) -> List[List[Any]]:
        """Return the raw data."""
        return [row.copy() for row in self._data]
    
    def format_cell(self, row: int, column: int, value: Any, view_mode: str) -> str:
        """Basic formatting - convert to string."""
        return str(value) if value is not None else ""
    
    def get_accessibility_text(self, row: int, column: int) -> str:
        """Generate basic accessibility text."""
        if (row < 0 or row >= len(self._data) or 
            column < 0 or column >= len(self._headers)):
            return ""
        
        column_name = self._headers[column]
        cell_value = self._data[row][column]
        
        # Include row context from first column if available
        row_context = ""
        if len(self._data[row]) > 0 and column > 0:
            row_context = str(self._data[row][0])
            return f"{row_context}, {column_name}, {cell_value}"
        else:
            return f"{column_name}, {cell_value}"
    
    def update_data(self, headers: List[str], data: List[List[Any]]):
        """Update the model data."""
        self._headers = headers.copy()
        self._data = [row.copy() for row in data] if data else []