# Qt6 Control Library Reference & Resources

This document provides comprehensive resources for Qt6 widgets and controls, including both official documentation and practical examples.

## 📁 Sample Applications in This Repository

### 1. Basic Widget Gallery (`qt6_widget_gallery.py`)
A comprehensive demonstration of all standard PyQt6 widgets organized in tabs:

- **Input Controls**: Buttons, checkboxes, radio buttons
- **Display Widgets**: Labels, progress bars, sliders, dials
- **Text & Combo**: Line edits, text areas, combo boxes, spin boxes
- **Date & Time**: Date/time pickers, calendar widget
- **Lists & Tables**: List widgets, tree widgets, table widgets
- **Layouts**: Grid, form, and splitter layouts

**Features:**
- Complete accessibility support (tooltips, keyboard navigation)
- Screen reader compatibility
- Real-world examples of each widget type
- Menu bar and status bar examples

**Run with:** `python qt6_widget_gallery.py`

### 2. Advanced Controls Reference (`qt6_advanced_reference.py`)
Demonstrates advanced Qt6 features and accessibility best practices:

- **Model/View Programming**: Custom table and list models with accessibility
- **Graphics View Framework**: Interactive graphics scene
- **Accessibility Features**: ARIA support, keyboard navigation testing
- **Best Practices**: Guidelines for accessible application development

**Features:**
- Custom QAbstractTableModel and QAbstractListModel implementations
- Accessibility roles (AccessibleTextRole, AccessibleDescriptionRole)
- Interactive demonstrations of keyboard navigation
- Progress bar accessibility examples

**Run with:** `python qt6_advanced_reference.py`

## 🌐 Official Qt6 Documentation & Resources

### Primary Documentation
- **[Qt Widgets Index](https://doc.qt.io/qt-6/qtwidgets-index.html)** - Main Qt6 widgets documentation
- **[Qt Widgets Examples](https://doc.qt.io/qt-6/examples-widgets.html)** - Official widget examples
- **[Widget Classes Reference](https://doc.qt.io/qt-6/widget-classes.html)** - Complete widget class listing

### Key Widget Categories

#### Basic Widgets
- **QWidget** - Base class for all UI objects
- **QLabel** - Text or image display
- **QPushButton** - Command button
- **QCheckBox** - Checkbox with text label
- **QRadioButton** - Radio button with text label
- **QComboBox** - Combined button and popup list
- **QLineEdit** - Single-line text editor
- **QTextEdit** - Multi-line rich text editor

#### Display Widgets
- **QProgressBar** - Horizontal or vertical progress bar
- **QSlider** - Vertical or horizontal slider
- **QScrollBar** - Scroll bar control
- **QDial** - Rounded range control
- **QLCDNumber** - LCD-like number display
- **QCalendarWidget** - Calendar widget

#### Container Widgets
- **QGroupBox** - Group box frame with title
- **QScrollArea** - Scrolling area with scroll bars
- **QTabWidget** - Tab widget providing tabs
- **QSplitter** - Resizable splitter widget
- **QFrame** - Base class for widgets that can have frames

#### Item Views (Model/View)
- **QListView** - List or icon view onto a model
- **QTreeView** - Tree view onto a model
- **QTableView** - Table view onto a model
- **QListWidget** - Convenience list widget
- **QTreeWidget** - Convenience tree widget
- **QTableWidget** - Convenience table widget

### Layout Management
- **QVBoxLayout** - Vertical box layout
- **QHBoxLayout** - Horizontal box layout
- **QGridLayout** - Grid layout
- **QFormLayout** - Form layout for two-column forms
- **QStackedLayout** - Stack layout

## 🎯 Specific Qt6 Examples from Official Documentation

### Essential Examples to Study

1. **[Calculator Example](https://doc.qt.io/qt-6/qtwidgets-widgets-calculator-example.html)**
   - Demonstrates signals and slots
   - Grid layout usage
   - Button interactions

2. **[Calendar Widget Example](https://doc.qt.io/qt-6/qtwidgets-widgets-calendarwidget-example.html)**
   - QCalendarWidget usage
   - Date/time handling
   - Widget customization

3. **[Line Edits Example](https://doc.qt.io/qt-6/qtwidgets-widgets-lineedits-example.html)**
   - Various QLineEdit configurations
   - Input validation
   - Echo modes (password fields)

4. **[Sliders Example](https://doc.qt.io/qt-6/qtwidgets-widgets-sliders-example.html)**
   - QSlider, QScrollBar, QDial usage
   - Value synchronization
   - Orientation handling

5. **[Spin Boxes Example](https://doc.qt.io/qt-6/qtwidgets-widgets-spinboxes-example.html)**
   - QSpinBox and QDoubleSpinBox
   - Custom formatting
   - Range validation

## 🔧 PyQt6-Specific Resources

### Installation
```bash
pip install PyQt6
```

### Key Differences from PyQt5
- **Namespacing**: `from PyQt6.QtWidgets import *`
- **Enums**: `Qt.AlignmentFlag.AlignCenter` instead of `Qt.AlignCenter`
- **Signals**: Same syntax, but better type hints
- **New Features**: Better accessibility support, improved performance

### Essential PyQt6 Imports
```python
# Core widgets
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QCheckBox, QRadioButton, QSlider, QProgressBar
)

# Core functionality
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread

# GUI elements
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon, QAction
```

## ♿ Accessibility Features in Qt6

### Built-in Accessibility Support
Qt6 provides excellent accessibility support out of the box:

1. **Keyboard Navigation**
   - Tab/Shift+Tab for focus movement
   - Arrow keys for list/tree navigation
   - Space/Enter for activation

2. **Screen Reader Support**
   - Automatic role detection
   - AccessibleTextRole for custom descriptions
   - AccessibleDescriptionRole for additional context

3. **Visual Accessibility**
   - High contrast theme support
   - Focus indicators
   - Customizable fonts and colors

### Implementing Accessibility
```python
# Set accessible properties
widget.setAccessibleName("User Name Input")
widget.setAccessibleDescription("Enter your full name here")
widget.setToolTip("Type your name and press Tab to continue")

# Custom accessible text in models
def data(self, index, role):
    if role == Qt.ItemDataRole.AccessibleTextRole:
        return f"Row {index.row()}: {self.data_value}"
    elif role == Qt.ItemDataRole.AccessibleDescriptionRole:
        return f"Item {index.row() + 1} of {self.rowCount()}"
```

## 🎨 Styling and Themes

### Qt Style Sheets
Qt6 supports CSS-like styling:
```python
widget.setStyleSheet("""
    QPushButton {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
""")
```

### System Theme Integration
Qt6 automatically adapts to system themes:
- Dark mode support
- High contrast modes
- Platform-native styling

## 📚 Additional Learning Resources

### Online Tutorials
- **[Qt for Python Documentation](https://doc.qt.io/qtforpython/)** - Official PyQt6/PySide6 docs
- **[Real Python Qt Tutorial](https://realpython.com/python-pyqt-gui-calculator/)** - Practical PyQt6 tutorial
- **[ZetCode PyQt6 Tutorial](https://zetcode.com/pyqt6/)** - Comprehensive PyQt6 guide

### Code Examples Repositories
- **[Qt Official Examples](https://github.com/qt/qtbase/tree/6.5/examples/widgets)** - Official Qt C++ examples
- **[PyQt6 Examples](https://github.com/PyQt6/examples)** - Community PyQt6 examples

### Books
- "Rapid GUI Programming with Python and Qt" - Mark Summerfield
- "Creating GUI Applications with Qt6 and Python" - Martin Fitzpatrick

## 🚀 Quick Start Template

Here's a minimal Qt6 application template:

```python
#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Qt6 App")
        self.setGeometry(100, 100, 400, 300)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout()
        
        # Widgets
        label = QLabel("Hello, Qt6!")
        button = QPushButton("Click Me")
        button.clicked.connect(self.button_clicked)
        
        # Add to layout
        layout.addWidget(label)
        layout.addWidget(button)
        central_widget.setLayout(layout)
    
    def button_clicked(self):
        print("Button clicked!")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
```

## 🔍 Testing Your Qt6 Applications

### Accessibility Testing
1. **Keyboard-only navigation**: Unplug your mouse and navigate using only Tab, arrows, Space, and Enter
2. **Screen reader testing**: Use NVDA (free) on Windows or VoiceOver on macOS
3. **High contrast testing**: Enable high contrast mode in your OS
4. **Focus visibility**: Ensure all focusable elements have clear focus indicators

### Performance Testing
- Use Qt's built-in profiling tools
- Monitor memory usage with large datasets
- Test responsiveness with background operations

This reference provides everything you need to get started with Qt6 widgets and create accessible, professional applications!
