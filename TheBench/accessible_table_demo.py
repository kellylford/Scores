#!/usr/bin/env python3
"""
Accessible Table Widget Demo

This demonstration shows how to use the AccessibleTableWidget with various types of data,
showcasing its flexibility and accessibility features.

Features demonstrated:
- Simple data usage with built-in model
- Custom data model implementation
- Configuration customization
- Multiple data types (business, educational, inventory)
- Accessibility optimizations
"""

import sys
from datetime import datetime, date
from typing import List, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QGroupBox, QCheckBox, QSpinBox,
    QComboBox, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from accessible_table_widget import AccessibleTableWidget
from accessible_table_core import TableDataModel, TableConfig


class BusinessDataModel:
    """Custom data model for business/sales data with advanced formatting."""
    
    def __init__(self):
        self.headers = ["Employee", "Department", "Sales", "Target", "% of Target", "Bonus"]
        self.data = [
            ["Alice Johnson", "Sales", 125000, 100000, 1.25, "Yes"],
            ["Bob Smith", "Marketing", 95000, 80000, 1.1875, "Yes"], 
            ["Carol Davis", "Sales", 110000, 100000, 1.10, "Yes"],
            ["David Wilson", "Engineering", 0, 0, 0, "N/A"],
            ["Emma Brown", "Sales", 87000, 100000, 0.87, "No"],
            ["Frank Miller", "Marketing", 72000, 80000, 0.90, "No"],
            ["Grace Lee", "Engineering", 0, 0, 0, "N/A"],
            ["Henry Taylor", "Sales", 134000, 100000, 1.34, "Yes"]
        ]
    
    def get_columns(self, view_mode: str) -> List[str]:
        """Return appropriate columns for each view mode."""
        if view_mode == "quick":
            return ["Employee", "Sales", "Bonus"]  # Simplified for quick view
        return self.headers
    
    def get_data(self) -> List[List[Any]]:
        """Return the business data."""
        return self.data
    
    def format_cell(self, row: int, column: int, value: Any, view_mode: str) -> str:
        """Format cells with business-appropriate formatting."""
        if row >= len(self.data) or column >= len(self.headers):
            return ""
        
        header = self.headers[column]
        
        # Format currency values
        if header in ["Sales", "Target"] and isinstance(value, (int, float)):
            return f"${value:,.0f}"
        
        # Format percentages
        elif header == "% of Target" and isinstance(value, (int, float)):
            return f"{value:.1%}"
        
        # Format department with emoji for quick view
        elif header == "Department" and view_mode == "quick":
            dept_icons = {
                "Sales": "💼 Sales",
                "Marketing": "📈 Marketing", 
                "Engineering": "⚙️ Engineering"
            }
            return dept_icons.get(str(value), str(value))
        
        return str(value)
    
    def get_accessibility_text(self, row: int, column: int) -> str:
        """Generate business-focused accessibility descriptions."""
        if row >= len(self.data) or column >= len(self.headers):
            return ""
        
        employee = self.data[row][0]
        header = self.headers[column]
        value = self.data[row][column]
        
        # Special accessibility descriptions for business context
        if header == "Sales":
            formatted_value = f"${value:,.0f}" if isinstance(value, (int, float)) else str(value)
            return f"{employee}, sales amount, {formatted_value}"
        elif header == "% of Target":
            formatted_value = f"{value:.1%}" if isinstance(value, (int, float)) else str(value)
            return f"{employee}, percentage of target achieved, {formatted_value}"
        elif header == "Bonus":
            return f"{employee}, bonus eligibility, {value}"
        else:
            return f"{employee}, {header.lower()}, {value}"


class StudentGradesModel:
    """Educational data model for student grades."""
    
    def __init__(self):
        self.headers = ["Student", "Course", "Midterm", "Final", "Projects", "Total", "Grade"]
        self.data = [
            ["Sarah Chen", "Computer Science 101", 85, 92, 88, 89.0, "B+"],
            ["Michael Rodriguez", "Computer Science 101", 78, 85, 82, 82.3, "B"],
            ["Jennifer Kim", "Computer Science 101", 95, 98, 94, 95.7, "A"],
            ["Alex Thompson", "Computer Science 101", 72, 78, 75, 75.0, "C+"],
            ["Maria Gonzalez", "Computer Science 101", 88, 90, 85, 87.7, "B+"],
            ["James Wilson", "Computer Science 101", 82, 79, 81, 80.7, "B-"],
            ["Lisa Zhang", "Computer Science 101", 91, 94, 89, 91.3, "A-"],
            ["David Park", "Computer Science 101", 69, 74, 71, 71.3, "C"]
        ]
    
    def get_columns(self, view_mode: str) -> List[str]:
        if view_mode == "quick":
            return ["Student", "Total", "Grade"]
        return self.headers
    
    def get_data(self) -> List[List[Any]]:
        return self.data
    
    def format_cell(self, row: int, column: int, value: Any, view_mode: str) -> str:
        header = self.headers[column]
        
        # Format scores with proper precision
        if header in ["Midterm", "Final", "Projects", "Total"] and isinstance(value, (int, float)):
            return f"{value:.1f}"
        
        # Add grade icons for visual appeal
        elif header == "Grade" and view_mode in ["quick", "table"]:
            grade_icons = {
                "A": "🌟 A", "A-": "⭐ A-", "B+": "📘 B+", "B": "📙 B",
                "B-": "📒 B-", "C+": "📗 C+", "C": "📕 C", "C-": "📋 C-"
            }
            return grade_icons.get(str(value), str(value))
        
        return str(value)
    
    def get_accessibility_text(self, row: int, column: int) -> str:
        student = self.data[row][0]
        header = self.headers[column]
        value = self.data[row][column]
        
        if header in ["Midterm", "Final", "Projects", "Total"]:
            return f"{student}, {header.lower()} score, {value:.1f} points"
        elif header == "Grade":
            return f"{student}, final grade, {value}"
        else:
            return f"{student}, {header.lower()}, {value}"


class InventoryDataModel:
    """Inventory management data model."""
    
    def __init__(self):
        self.headers = ["SKU", "Product", "Category", "Stock", "Reorder Level", "Status", "Last Updated"]
        self.data = [
            ["ABC123", "Wireless Headphones", "Electronics", 45, 20, "In Stock", "2024-01-15"],
            ["DEF456", "Bluetooth Speaker", "Electronics", 12, 15, "Low Stock", "2024-01-14"],
            ["GHI789", "USB Cable", "Accessories", 156, 50, "In Stock", "2024-01-15"],
            ["JKL012", "Power Bank", "Electronics", 8, 10, "Critical", "2024-01-13"],
            ["MNO345", "Phone Case", "Accessories", 89, 25, "In Stock", "2024-01-15"],
            ["PQR678", "Screen Protector", "Accessories", 234, 100, "In Stock", "2024-01-14"],
            ["STU901", "Charging Dock", "Electronics", 3, 5, "Critical", "2024-01-12"],
            ["VWX234", "Memory Card", "Storage", 67, 30, "In Stock", "2024-01-15"]
        ]
    
    def get_columns(self, view_mode: str) -> List[str]:
        if view_mode == "quick":
            return ["Product", "Stock", "Status"]
        return self.headers
    
    def get_data(self) -> List[List[Any]]:
        return self.data
    
    def format_cell(self, row: int, column: int, value: Any, view_mode: str) -> str:
        header = self.headers[column]
        
        # Format stock levels with visual indicators
        if header == "Stock" and isinstance(value, int):
            return f"{value} units"
        
        # Color-code status
        elif header == "Status":
            status_icons = {
                "In Stock": "✅ In Stock",
                "Low Stock": "⚠️ Low Stock", 
                "Critical": "🚨 Critical"
            }
            return status_icons.get(str(value), str(value))
        
        # Format dates nicely
        elif header == "Last Updated":
            try:
                # Assuming date string format
                return f"📅 {value}"
            except:
                return str(value)
        
        return str(value)
    
    def get_accessibility_text(self, row: int, column: int) -> str:
        sku = self.data[row][0]
        product = self.data[row][1]
        header = self.headers[column]
        value = self.data[row][column]
        
        if header == "Stock":
            return f"{product}, current stock level, {value} units"
        elif header == "Status":
            return f"{product}, inventory status, {value}"
        elif header == "Reorder Level":
            return f"{product}, reorder threshold, {value} units"
        else:
            return f"{product}, {header.lower()}, {value}"


class AccessibleTableDemo(QMainWindow):
    """Main demo application showcasing the AccessibleTableWidget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accessible Table Widget Demo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create data models
        self.business_model = BusinessDataModel()
        self.student_model = StudentGradesModel()
        self.inventory_model = InventoryDataModel()
        
        self.setup_ui()
        self.setup_tables()
        
        # Start with business data
        self.show_business_data()
    
    def setup_ui(self):
        """Setup the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title and description
        title = QLabel("Accessible Table Widget Demo")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        desc = QLabel(
            "Demonstration of a reusable accessible table widget with multiple view modes.\n"
            "Keyboard shortcuts: Alt+V (cycle views), Alt+T (table), Alt+Q (quick list), Alt+F (full list)"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #666; margin: 10px;")
        main_layout.addWidget(desc)
        
        # Create horizontal splitter for controls and table
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel: Controls
        self.setup_control_panel(splitter)
        
        # Right panel: Table display
        self.setup_table_panel(splitter)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 1)  # Control panel
        splitter.setStretchFactor(1, 3)  # Table panel
    
    def setup_control_panel(self, parent):
        """Setup the control panel."""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # Data selection
        data_group = QGroupBox("Data Sources")
        data_layout = QVBoxLayout(data_group)
        
        business_btn = QPushButton("Business Sales Data")
        business_btn.clicked.connect(self.show_business_data)
        business_btn.setAccessibleDescription("Show business sales performance data")
        data_layout.addWidget(business_btn)
        
        student_btn = QPushButton("Student Grades Data")
        student_btn.clicked.connect(self.show_student_data)
        student_btn.setAccessibleDescription("Show student course grades data")
        data_layout.addWidget(student_btn)
        
        inventory_btn = QPushButton("Inventory Data")
        inventory_btn.clicked.connect(self.show_inventory_data)
        inventory_btn.setAccessibleDescription("Show inventory management data")
        data_layout.addWidget(inventory_btn)
        
        control_layout.addWidget(data_group)
        
        # Configuration options
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Accessibility options
        self.tooltips_cb = QCheckBox("Enable Tooltips")
        self.tooltips_cb.setChecked(True)
        self.tooltips_cb.toggled.connect(self.update_config)
        config_layout.addWidget(self.tooltips_cb)
        
        self.row_context_cb = QCheckBox("Include Row Context")
        self.row_context_cb.setChecked(True)
        self.row_context_cb.toggled.connect(self.update_config)
        config_layout.addWidget(self.row_context_cb)
        
        self.announce_changes_cb = QCheckBox("Announce View Changes")
        self.announce_changes_cb.setChecked(True)
        self.announce_changes_cb.toggled.connect(self.update_config)
        config_layout.addWidget(self.announce_changes_cb)
        
        # Visual options
        self.alternate_rows_cb = QCheckBox("Alternate Row Colors")
        self.alternate_rows_cb.setChecked(True)
        self.alternate_rows_cb.toggled.connect(self.update_config)
        config_layout.addWidget(self.alternate_rows_cb)
        
        # Stretch column selection
        stretch_layout = QHBoxLayout()
        stretch_layout.addWidget(QLabel("Stretch Column:"))
        self.stretch_combo = QComboBox()
        self.stretch_combo.addItems(["Auto-resize", "0", "1", "2", "3", "4", "5"])
        self.stretch_combo.currentTextChanged.connect(self.update_config)
        stretch_layout.addWidget(self.stretch_combo)
        config_layout.addLayout(stretch_layout)
        
        control_layout.addWidget(config_group)
        
        # View control
        view_group = QGroupBox("View Controls")
        view_layout = QVBoxLayout(view_group)
        
        table_view_btn = QPushButton("Table View (Alt+T)")
        table_view_btn.clicked.connect(lambda: self.table.set_view("table"))
        view_layout.addWidget(table_view_btn)
        
        quick_view_btn = QPushButton("Quick List View (Alt+Q)")
        quick_view_btn.clicked.connect(lambda: self.table.set_view("quick"))
        view_layout.addWidget(quick_view_btn)
        
        full_view_btn = QPushButton("Full List View (Alt+F)")
        full_view_btn.clicked.connect(lambda: self.table.set_view("full"))
        view_layout.addWidget(full_view_btn)
        
        control_layout.addWidget(view_group)
        
        # Status display
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(200)
        self.status_text.setAccessibleName("Status Log")
        self.status_text.append("Demo application started.")
        status_layout.addWidget(self.status_text)
        
        control_layout.addWidget(status_group)
        
        control_layout.addStretch()
        parent.addWidget(control_widget)
    
    def setup_table_panel(self, parent):
        """Setup the table display panel."""
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        # Current view indicator
        self.view_indicator = QLabel("Current View: Table")
        self.view_indicator.setStyleSheet("font-weight: bold; padding: 5px;")
        table_layout.addWidget(self.view_indicator)
        
        # Create the accessible table
        self.config = TableConfig()
        self.table = AccessibleTableWidget(
            accessible_name="Demo Data Table",
            accessible_description="Demonstration table with sample business data",
            config=self.config
        )
        
        # Connect signals
        self.table.view_changed.connect(self.on_view_changed)
        self.table.data_updated.connect(self.on_data_updated)
        
        table_layout.addWidget(self.table)
        parent.addWidget(table_widget)
    
    def setup_tables(self):
        """Setup table configurations."""
        # Configure stretch column for better display
        self.config.stretch_column = 1  # Usually the name/description column
    
    def show_business_data(self):
        """Show business sales data."""
        self.table.set_data_model(self.business_model)
        self.table.update_accessible_name("Business Sales Data")
        self.table.update_accessible_description("Sales performance data for employees")
        self.status_text.append("Loaded business sales data with custom formatting.")
        
        # Update stretch column dropdown
        self.stretch_combo.setCurrentText("1")  # Employee name column
    
    def show_student_data(self):
        """Show student grades data."""
        self.table.set_data_model(self.student_model)
        self.table.update_accessible_name("Student Grades")
        self.table.update_accessible_description("Student course grades and performance")
        self.status_text.append("Loaded student grades data with educational formatting.")
        
        # Update stretch column dropdown
        self.stretch_combo.setCurrentText("0")  # Student name column
    
    def show_inventory_data(self):
        """Show inventory data."""
        self.table.set_data_model(self.inventory_model)
        self.table.update_accessible_name("Inventory Management")
        self.table.update_accessible_description("Product inventory levels and status")
        self.status_text.append("Loaded inventory data with status indicators.")
        
        # Update stretch column dropdown
        self.stretch_combo.setCurrentText("1")  # Product name column
    
    def update_config(self):
        """Update table configuration based on control panel settings."""
        # Update accessibility settings
        self.config.enable_tooltips = self.tooltips_cb.isChecked()
        self.config.include_row_context = self.row_context_cb.isChecked()
        self.config.announce_view_changes = self.announce_changes_cb.isChecked()
        self.config.alternate_row_colors = self.alternate_rows_cb.isChecked()
        
        # Update stretch column
        stretch_text = self.stretch_combo.currentText()
        if stretch_text == "Auto-resize":
            self.config.stretch_column = None
        else:
            try:
                self.config.stretch_column = int(stretch_text)
            except ValueError:
                self.config.stretch_column = None
        
        # Refresh the table to apply changes
        self.table.refresh_data()
        self.status_text.append(f"Configuration updated: tooltips={self.config.enable_tooltips}, "
                               f"row_context={self.config.include_row_context}")
    
    def on_view_changed(self, view_mode: str):
        """Handle view mode changes."""
        view_names = {
            "table": "Table View",
            "quick": "Quick List View", 
            "full": "Full List View"
        }
        view_name = view_names.get(view_mode, view_mode)
        self.view_indicator.setText(f"Current View: {view_name}")
        self.status_text.append(f"View changed to: {view_name}")
    
    def on_data_updated(self):
        """Handle data updates."""
        self.status_text.append("Table data refreshed.")


class SimpleUsageExample(QWidget):
    """Simple example showing basic usage without custom models."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Usage Example")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Simple Usage Example")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "This example shows the simplest way to use AccessibleTableWidget.\n"
            "Use Alt+V to cycle through view modes, arrow keys to navigate."
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        # Create table with simple data
        self.table = AccessibleTableWidget(
            accessible_name="Simple Example Table",
            accessible_description="Basic table showing simple data"
        )
        
        # Simple sample data
        headers = ["Name", "Age", "City", "Occupation"]
        data = [
            ["John Doe", 30, "New York", "Software Engineer"],
            ["Jane Smith", 25, "San Francisco", "Designer"],
            ["Bob Johnson", 35, "Chicago", "Teacher"],
            ["Alice Wilson", 28, "Seattle", "Doctor"],
            ["Charlie Brown", 32, "Boston", "Lawyer"]
        ]
        
        # Set data using the simple interface
        self.table.set_simple_data(headers, data)
        
        layout.addWidget(self.table)


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties for better accessibility
    app.setApplicationName("Accessible Table Widget Demo")
    app.setApplicationDisplayName("Accessible Table Widget Demo")
    app.setApplicationVersion("1.0")
    
    # Show the main demo
    demo = AccessibleTableDemo()
    demo.show()
    
    # Also show simple example in a separate window
    simple_example = SimpleUsageExample()
    simple_example.show()
    
    print("🎯 Accessible Table Widget Demo Started")
    print("✅ Two demo windows opened:")
    print("   1. Full-featured demo with custom data models")
    print("   2. Simple usage example")
    print("📋 Try the keyboard shortcuts:")
    print("   - Alt+V: Cycle through view modes")
    print("   - Alt+T: Table view")
    print("   - Alt+Q: Quick list view") 
    print("   - Alt+F: Full list view")
    print("   - Arrow keys: Navigate within views")
    print("🎫 Test different data types and configuration options")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()