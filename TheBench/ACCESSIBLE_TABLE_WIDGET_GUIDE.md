# Accessible Table Widget - Usage Guide

## Overview

The **Accessible Table Widget** is a standalone, reusable PyQt6 component extracted from the Scores application. It provides industry-leading accessibility features for displaying tabular data with multiple view modes optimized for screen readers and keyboard navigation.

## Key Features

### 🎯 Multiple View Modes
- **Table View**: Traditional grid layout with rows and columns
- **Quick List View**: Simplified list format showing key information
- **Full List View**: Detailed list with header-value pairs

### ⌨️ Universal Keyboard Shortcuts
- `Alt+V`: Cycle through view modes
- `Alt+T`: Switch directly to Table view
- `Alt+Q`: Switch directly to Quick List view  
- `Alt+F`: Switch directly to Full List view
- Arrow keys: Navigate within views
- Tab: Enter/exit table navigation

### ♿ Screen Reader Optimization
- Proper ARIA attributes and role assignments
- Context-aware accessibility text generation
- Screen reader announcements for view changes
- Enhanced cell descriptions with row/column context

### 🎛️ Focus Management
- Maintains user position during view switches
- Proper focus restoration and navigation
- Boundary stopping to prevent navigation confusion

### 🔄 Real-time Updates
- All views automatically sync with data changes
- Live refresh capability while preserving user position
- Signal-based notifications for data updates

## Installation & Setup

### Requirements
- Python 3.8+
- PyQt6
- typing support (Python 3.8+ built-in)

### Files Required
Copy these files to your project:

1. **`accessible_table_core.py`** - Core interfaces and data models (GUI-independent)
2. **`accessible_table_widget.py`** - Main widget implementation (requires PyQt6)
3. **`accessible_table_demo.py`** - Comprehensive demonstration (optional)

### Basic Import

```python
from accessible_table_widget import AccessibleTableWidget, TableConfig
from accessible_table_core import SimpleTableDataModel, TableDataModel
```

## Quick Start

### Simple Usage Example

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from accessible_table_widget import AccessibleTableWidget

app = QApplication(sys.argv)

# Create main window
window = QMainWindow()
widget = QWidget()
layout = QVBoxLayout(widget)

# Create accessible table
table = AccessibleTableWidget(
    accessible_name="Employee Data",
    accessible_description="Employee information with salary and performance data"
)

# Simple data setup
headers = ["Name", "Department", "Salary", "Performance"]
data = [
    ["Alice Johnson", "Engineering", "$75,000", "Excellent"],
    ["Bob Smith", "Marketing", "$65,000", "Good"],
    ["Carol Davis", "Sales", "$70,000", "Excellent"]
]

table.set_simple_data(headers, data)
layout.addWidget(table)

window.setCentralWidget(widget)
window.show()

sys.exit(app.exec())
```

## Advanced Usage

### Custom Data Models

For advanced formatting and accessibility features, implement the `TableDataModel` protocol:

```python
class CustomDataModel:
    def __init__(self, business_data):
        self.data = business_data
        self.headers = ["Employee", "Sales", "Target", "Achievement"]
    
    def get_columns(self, view_mode: str) -> List[str]:
        if view_mode == "quick":
            return ["Employee", "Achievement"]  # Simplified view
        return self.headers
    
    def get_data(self) -> List[List[Any]]:
        return self.data
    
    def format_cell(self, row: int, column: int, value: Any, view_mode: str) -> str:
        if self.headers[column] in ["Sales", "Target"]:
            return f"${value:,.0f}"  # Currency formatting
        elif self.headers[column] == "Achievement":
            return f"{value:.1%}"  # Percentage formatting
        return str(value)
    
    def get_accessibility_text(self, row: int, column: int) -> str:
        employee = self.data[row][0]
        column_name = self.headers[column]
        value = self.data[row][column]
        
        if column_name == "Sales":
            return f"{employee}, sales amount, ${value:,.0f}"
        elif column_name == "Achievement":
            return f"{employee}, achievement level, {value:.1%}"
        
        return f"{employee}, {column_name.lower()}, {value}"

# Usage
model = CustomDataModel(your_business_data)
table.set_data_model(model)
```

### Configuration Customization

```python
from accessible_table_core import TableConfig

# Create custom configuration
config = TableConfig()

# Accessibility settings
config.enable_tooltips = True
config.include_row_context = True
config.announce_view_changes = True

# Visual settings
config.alternate_row_colors = True
config.stretch_column = 1  # Stretch the second column (0-indexed)

# Navigation settings
config.boundary_stopping = True
config.tab_navigation_enabled = False

# Create table with custom config
table = AccessibleTableWidget(
    accessible_name="Custom Table",
    accessible_description="Table with custom configuration",
    config=config
)
```

## API Reference

### AccessibleTableWidget Class

#### Constructor
```python
AccessibleTableWidget(
    parent=None,
    accessible_name: str = "Data Table",
    accessible_description: str = "Data table with arrow key navigation",
    config: Optional[TableConfig] = None
)
```

#### Key Methods

**Data Management:**
```python
set_simple_data(headers: List[str], data: List[List[Any]])
set_data_model(model: TableDataModel)
refresh_data()
```

**View Control:**
```python
get_current_view() -> str
set_view(view_mode: str)
```

**Position Management:**
```python
get_current_row() -> int
get_current_column() -> int
set_current_position(row: int, column: int = 0)
```

**Focus and Accessibility:**
```python
has_focus() -> bool
set_focus()
update_accessible_name(name: str)
update_accessible_description(description: str)
```

#### Signals
```python
view_changed = pyqtSignal(str)  # Emitted when view mode changes
item_selected = pyqtSignal(dict)  # Emitted when item is selected
data_updated = pyqtSignal()  # Emitted when data refreshes
```

### TableConfig Class

#### Key Properties
```python
# View modes
VIEW_TABLE = "table"
VIEW_QUICK_LIST = "quick"  
VIEW_FULL_LIST = "full"

# Accessibility settings
enable_tooltips: bool = True
enable_accessibility_roles: bool = True
announce_view_changes: bool = True
include_row_context: bool = True

# Visual settings
alternate_row_colors: bool = True
stretch_column: Optional[int] = None
focus_style: str = "CSS styling for focus"

# Navigation settings
tab_navigation_enabled: bool = False
boundary_stopping: bool = True
```

### TableDataModel Protocol

Implement these methods for custom data models:

```python
def get_columns(self, view_mode: str) -> List[str]
def get_data(self) -> List[List[Any]]
def format_cell(self, row: int, column: int, value: Any, view_mode: str) -> str
def get_accessibility_text(self, row: int, column: int) -> str
```

## Integration Patterns

### With Existing Applications

1. **Replace existing QTableWidget:**
   ```python
   # Before
   table = QTableWidget()
   
   # After
   table = AccessibleTableWidget(
       accessible_name="Your Table Name",
       accessible_description="Description of table contents"
   )
   ```

2. **Add to existing layouts:**
   ```python
   layout.addWidget(table)  # Direct replacement
   ```

3. **Connect to existing data sources:**
   ```python
   def update_table_data(self, new_data):
       table.set_simple_data(self.headers, new_data)
   ```

### Signal Connections

```python
# React to view changes
table.view_changed.connect(self.on_view_changed)

def on_view_changed(self, view_mode):
    print(f"User switched to {view_mode} view")
    
# React to data updates
table.data_updated.connect(self.on_data_refreshed)

def on_data_refreshed(self):
    print("Table data has been refreshed")
```

## Accessibility Best Practices

### Screen Reader Optimization

1. **Meaningful Names:**
   ```python
   table.update_accessible_name("Sales Performance Report")
   table.update_accessible_description("Monthly sales data showing targets and achievements")
   ```

2. **Context-Rich Descriptions:**
   ```python
   def get_accessibility_text(self, row: int, column: int) -> str:
       employee = self.data[row][0]
       column_name = self.headers[column]
       value = self.data[row][column]
       return f"{employee}, {column_name}, {value} with detailed context"
   ```

3. **View Mode Descriptions:**
   - Table View: "Traditional table with rows and columns for detailed navigation"
   - Quick List: "Simplified list showing key information only"
   - Full List: "Detailed list with all information in header-value format"

### Keyboard Navigation

1. **Standard Shortcuts:** Always use the default Alt+V, Alt+T, Alt+Q, Alt+F shortcuts
2. **Arrow Key Navigation:** Works in all view modes for consistent experience
3. **Tab Navigation:** Use Tab to enter/exit table, configurable per application needs
4. **Boundary Handling:** Enable boundary stopping to prevent user confusion

### Focus Management

1. **Position Preservation:** The widget automatically maintains user position across view switches
2. **Initial Focus:** Set focus appropriately when first displaying data
3. **Focus Restoration:** After dialogs or interruptions, restore focus to last position

## Testing and Validation

### Accessibility Testing

1. **Screen Reader Testing:**
   - Test with JAWS, NVDA, and Windows Narrator
   - Verify all content is announced correctly
   - Check navigation flow and context announcements

2. **Keyboard Testing:**
   - Test all keyboard shortcuts
   - Verify arrow key navigation in all views
   - Test boundary behavior and focus management

3. **View Mode Testing:**
   - Verify data consistency across all three views
   - Test view switching with various data types
   - Confirm position preservation works correctly

### Data Model Testing

```python
def test_custom_model():
    model = YourCustomModel(test_data)
    
    # Test required methods exist
    assert hasattr(model, 'get_columns')
    assert hasattr(model, 'get_data')
    assert hasattr(model, 'format_cell')
    assert hasattr(model, 'get_accessibility_text')
    
    # Test functionality
    columns = model.get_columns("table")
    data = model.get_data()
    formatted = model.format_cell(0, 0, data[0][0], "table")
    accessibility = model.get_accessibility_text(0, 0)
    
    assert len(columns) > 0
    assert len(data) > 0
    assert formatted is not None
    assert accessibility is not None
```

## Troubleshooting

### Common Issues

1. **Import Errors:**
   - Ensure PyQt6 is installed: `pip install PyQt6`
   - Check that all required files are in your Python path

2. **Display Issues:**
   - Verify your Qt installation supports your display system
   - Check for missing graphics libraries on Linux systems

3. **Accessibility Issues:**
   - Ensure screen reader is running before starting application
   - Check that accessibility services are enabled on your system
   - Verify TableDataModel methods return appropriate values

4. **Performance Issues:**
   - For large datasets, implement efficient data models
   - Consider pagination for very large tables
   - Use proper column sizing to avoid excessive rendering

### Debug Information

Enable debug output to troubleshoot issues:

```python
# Connect to signals for debugging
table.view_changed.connect(lambda mode: print(f"View changed to: {mode}"))
table.data_updated.connect(lambda: print("Data updated"))

# Check current state
print(f"Current view: {table.get_current_view()}")
print(f"Current position: {table.get_current_row()}, {table.get_current_column()}")
print(f"Has focus: {table.has_focus()}")
```

## Migration from Original AccessibleTable

If migrating from the original Scores application's AccessibleTable:

### Code Changes Required

1. **Import Updates:**
   ```python
   # Before
   from accessible_table import AccessibleTable
   
   # After  
   from accessible_table_widget import AccessibleTableWidget
   ```

2. **Constructor Changes:**
   ```python
   # Before
   table = AccessibleTable(parent, "Table Name", "Description")
   
   # After
   table = AccessibleTableWidget(
       parent=parent,
       accessible_name="Table Name", 
       accessible_description="Description"
   )
   ```

3. **Data Population:**
   ```python
   # Before
   table.populate_data(data)
   
   # After
   table.set_simple_data(headers, data)
   # OR
   table.set_data_model(custom_model)
   ```

### Compatibility Notes

- Most existing functionality is preserved
- View modes work identically
- Keyboard shortcuts are unchanged
- Sports-specific methods have been removed
- Generic data interface replaces sports-specific data handling

## Future Enhancements

The widget is designed for extensibility. Potential future enhancements include:

- Additional view modes
- Customizable keyboard shortcuts
- Enhanced visual themes
- Export functionality
- Advanced filtering and sorting
- Integration with web technologies for enhanced accessibility

## Support and Contributing

This widget was extracted from the Scores application to be a reusable component. For issues, enhancements, or questions:

1. Check this guide for solutions
2. Review the demo application for examples
3. Test with the validation script
4. Examine the source code for implementation details

The widget is designed to be self-contained and framework-agnostic within the PyQt6 ecosystem.