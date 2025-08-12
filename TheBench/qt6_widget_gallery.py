#!/usr/bin/env python3
"""
Qt6 Widget Gallery - Comprehensive demonstration of PyQt6 controls
This application showcases all major Qt6 widgets with accessibility features.

Based on Qt's official widget gallery example, adapted for PyQt6.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFormLayout, QScrollArea, QGroupBox, QLabel, QPushButton,
    QCheckBox, QRadioButton, QComboBox, QSpinBox, QDoubleSpinBox, QSlider,
    QProgressBar, QLineEdit, QTextEdit, QPlainTextEdit, QDateEdit, QTimeEdit,
    QDateTimeEdit, QCalendarWidget, QListWidget, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QTabBar, QSplitter, QFrame, QDial,
    QScrollBar, QLCDNumber, QFontComboBox, QColorDialog, QFileDialog,
    QMessageBox, QInputDialog, QButtonGroup, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QDate, QTime, QDateTime, QTimer
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette, QIcon, QAction, QKeySequence, QShortcut


class InputWidgetsTab(QWidget):
    """Tab containing input widgets (buttons, checkboxes, etc.)"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Buttons Group
        buttons_group = QGroupBox("Buttons")
        buttons_layout = QGridLayout()
        
        # Push buttons
        normal_btn = QPushButton("Normal Button")
        normal_btn.setToolTip("Standard push button")
        
        default_btn = QPushButton("Default Button")
        default_btn.setDefault(True)
        default_btn.setToolTip("Default button (activated with Enter)")
        
        checkable_btn = QPushButton("Checkable Button")
        checkable_btn.setCheckable(True)
        checkable_btn.setToolTip("Button that can be toggled on/off")
        
        disabled_btn = QPushButton("Disabled Button")
        disabled_btn.setEnabled(False)
        disabled_btn.setToolTip("This button is disabled")
        
        buttons_layout.addWidget(normal_btn, 0, 0)
        buttons_layout.addWidget(default_btn, 0, 1)
        buttons_layout.addWidget(checkable_btn, 1, 0)
        buttons_layout.addWidget(disabled_btn, 1, 1)
        buttons_group.setLayout(buttons_layout)
        
        # Checkboxes and Radio Buttons Group
        selection_group = QGroupBox("Selection Controls")
        selection_layout = QGridLayout()
        
        # Checkboxes
        checkbox1 = QCheckBox("Option 1")
        checkbox1.setChecked(True)
        checkbox1.setToolTip("First checkbox option")
        
        checkbox2 = QCheckBox("Option 2")
        checkbox2.setToolTip("Second checkbox option")
        
        checkbox3 = QCheckBox("Disabled Option")
        checkbox3.setEnabled(False)
        checkbox3.setToolTip("This checkbox is disabled")
        
        # Radio buttons
        radio_group = QButtonGroup()
        radio1 = QRadioButton("Choice A")
        radio1.setChecked(True)
        radio1.setToolTip("First radio button choice")
        
        radio2 = QRadioButton("Choice B")
        radio2.setToolTip("Second radio button choice")
        
        radio3 = QRadioButton("Choice C")
        radio3.setToolTip("Third radio button choice")
        
        radio_group.addButton(radio1)
        radio_group.addButton(radio2)
        radio_group.addButton(radio3)
        
        selection_layout.addWidget(QLabel("Checkboxes:"), 0, 0)
        selection_layout.addWidget(checkbox1, 1, 0)
        selection_layout.addWidget(checkbox2, 2, 0)
        selection_layout.addWidget(checkbox3, 3, 0)
        
        selection_layout.addWidget(QLabel("Radio Buttons:"), 0, 1)
        selection_layout.addWidget(radio1, 1, 1)
        selection_layout.addWidget(radio2, 2, 1)
        selection_layout.addWidget(radio3, 3, 1)
        
        selection_group.setLayout(selection_layout)
        
        layout.addWidget(buttons_group)
        layout.addWidget(selection_group)
        layout.addStretch()
        self.setLayout(layout)


class DisplayWidgetsTab(QWidget):
    """Tab containing display widgets (labels, progress bars, etc.)"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Labels Group
        labels_group = QGroupBox("Labels and Displays")
        labels_layout = QGridLayout()
        
        # Regular label
        text_label = QLabel("Text Label")
        text_label.setToolTip("Simple text label")
        
        # Rich text label
        rich_label = QLabel("<b>Bold</b> <i>Italic</i> <u>Underlined</u>")
        rich_label.setToolTip("Label with rich text formatting")
        
        # Progress bars
        progress1 = QProgressBar()
        progress1.setValue(50)
        progress1.setToolTip("Progress bar at 50%")
        
        progress2 = QProgressBar()
        progress2.setRange(0, 0)  # Indeterminate progress
        progress2.setToolTip("Indeterminate progress bar")
        
        # LCD Number
        lcd = QLCDNumber(8)
        lcd.display(12345678)
        lcd.setToolTip("LCD number display")
        
        labels_layout.addWidget(QLabel("Text Labels:"), 0, 0)
        labels_layout.addWidget(text_label, 0, 1)
        labels_layout.addWidget(rich_label, 1, 1)
        labels_layout.addWidget(QLabel("Progress Bars:"), 2, 0)
        labels_layout.addWidget(progress1, 2, 1)
        labels_layout.addWidget(progress2, 3, 1)
        labels_layout.addWidget(QLabel("LCD Display:"), 4, 0)
        labels_layout.addWidget(lcd, 4, 1)
        
        labels_group.setLayout(labels_layout)
        
        # Sliders and Dials Group
        controls_group = QGroupBox("Sliders and Dials")
        controls_layout = QGridLayout()
        
        # Horizontal slider
        h_slider = QSlider(Qt.Orientation.Horizontal)
        h_slider.setRange(0, 100)
        h_slider.setValue(30)
        h_slider.setToolTip("Horizontal slider")
        
        # Vertical slider
        v_slider = QSlider(Qt.Orientation.Vertical)
        v_slider.setRange(0, 100)
        v_slider.setValue(70)
        v_slider.setToolTip("Vertical slider")
        
        # Dial
        dial = QDial()
        dial.setRange(0, 360)
        dial.setValue(45)
        dial.setToolTip("Circular dial control")
        
        # Scroll bar
        scrollbar = QScrollBar(Qt.Orientation.Horizontal)
        scrollbar.setRange(0, 100)
        scrollbar.setValue(25)
        scrollbar.setToolTip("Horizontal scroll bar")
        
        controls_layout.addWidget(QLabel("Horizontal Slider:"), 0, 0)
        controls_layout.addWidget(h_slider, 0, 1)
        controls_layout.addWidget(QLabel("Vertical Slider:"), 1, 0)
        controls_layout.addWidget(v_slider, 1, 1)
        controls_layout.addWidget(QLabel("Dial:"), 2, 0)
        controls_layout.addWidget(dial, 2, 1)
        controls_layout.addWidget(QLabel("Scroll Bar:"), 3, 0)
        controls_layout.addWidget(scrollbar, 3, 1)
        
        controls_group.setLayout(controls_layout)
        
        layout.addWidget(labels_group)
        layout.addWidget(controls_group)
        layout.addStretch()
        self.setLayout(layout)


class TextWidgetsTab(QWidget):
    """Tab containing text input widgets"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Text Input Group
        text_group = QGroupBox("Text Input Controls")
        text_layout = QFormLayout()
        
        # Line edit
        line_edit = QLineEdit("Single line text")
        line_edit.setToolTip("Single line text input")
        
        # Password field
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_edit.setPlaceholderText("Enter password...")
        password_edit.setToolTip("Password input field")
        
        # Text edit (multi-line)
        text_edit = QTextEdit()
        text_edit.setPlainText("Multi-line text area\nSecond line\nThird line")
        text_edit.setMaximumHeight(100)
        text_edit.setToolTip("Multi-line text editor")
        
        # Plain text edit
        plain_edit = QPlainTextEdit()
        plain_edit.setPlainText("Plain text editor\nFor simple text")
        plain_edit.setMaximumHeight(80)
        plain_edit.setToolTip("Plain text editor without formatting")
        
        text_layout.addRow("Line Edit:", line_edit)
        text_layout.addRow("Password:", password_edit)
        text_layout.addRow("Text Edit:", text_edit)
        text_layout.addRow("Plain Text:", plain_edit)
        
        text_group.setLayout(text_layout)
        
        # Combo Boxes Group
        combo_group = QGroupBox("Combo Boxes and Spin Boxes")
        combo_layout = QFormLayout()
        
        # Regular combo box
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        combo.setToolTip("Dropdown combo box")
        
        # Editable combo box
        editable_combo = QComboBox()
        editable_combo.setEditable(True)
        editable_combo.addItems(["Editable 1", "Editable 2", "Editable 3"])
        editable_combo.setToolTip("Editable combo box")
        
        # Font combo box
        font_combo = QFontComboBox()
        font_combo.setToolTip("Font selection combo box")
        
        # Spin box
        spin_box = QSpinBox()
        spin_box.setRange(0, 1000)
        spin_box.setValue(50)
        spin_box.setToolTip("Integer spin box")
        
        # Double spin box
        double_spin = QDoubleSpinBox()
        double_spin.setRange(0.0, 100.0)
        double_spin.setValue(25.5)
        double_spin.setDecimals(2)
        double_spin.setToolTip("Floating point spin box")
        
        combo_layout.addRow("Combo Box:", combo)
        combo_layout.addRow("Editable Combo:", editable_combo)
        combo_layout.addRow("Font Combo:", font_combo)
        combo_layout.addRow("Spin Box:", spin_box)
        combo_layout.addRow("Double Spin:", double_spin)
        
        combo_group.setLayout(combo_layout)
        
        layout.addWidget(text_group)
        layout.addWidget(combo_group)
        layout.addStretch()
        self.setLayout(layout)


class DateTimeWidgetsTab(QWidget):
    """Tab containing date and time widgets"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Date/Time Group
        datetime_group = QGroupBox("Date and Time Controls")
        datetime_layout = QFormLayout()
        
        # Date edit
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        date_edit.setToolTip("Date input with calendar popup")
        
        # Time edit
        time_edit = QTimeEdit()
        time_edit.setTime(QTime.currentTime())
        time_edit.setToolTip("Time input control")
        
        # DateTime edit
        datetime_edit = QDateTimeEdit()
        datetime_edit.setDateTime(QDateTime.currentDateTime())
        datetime_edit.setCalendarPopup(True)
        datetime_edit.setToolTip("Combined date and time input")
        
        datetime_layout.addRow("Date Edit:", date_edit)
        datetime_layout.addRow("Time Edit:", time_edit)
        datetime_layout.addRow("DateTime Edit:", datetime_edit)
        
        datetime_group.setLayout(datetime_layout)
        
        # Calendar Widget
        calendar_group = QGroupBox("Calendar Widget")
        calendar_layout = QVBoxLayout()
        
        calendar = QCalendarWidget()
        calendar.setSelectedDate(QDate.currentDate())
        calendar.setToolTip("Full calendar widget")
        
        calendar_layout.addWidget(calendar)
        calendar_group.setLayout(calendar_layout)
        
        layout.addWidget(datetime_group)
        layout.addWidget(calendar_group)
        layout.addStretch()
        self.setLayout(layout)


class ListTableWidgetsTab(QWidget):
    """Tab containing list and table widgets"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Lists and Tables Group
        container = QWidget()
        container_layout = QHBoxLayout()
        
        # List Widget
        list_group = QGroupBox("List Widget")
        list_layout = QVBoxLayout()
        
        list_widget = QListWidget()
        list_widget.addItems([
            "List Item 1", "List Item 2", "List Item 3",
            "List Item 4", "List Item 5"
        ])
        list_widget.setToolTip("List widget for selecting items")
        
        list_layout.addWidget(list_widget)
        list_group.setLayout(list_layout)
        
        # Tree Widget
        tree_group = QGroupBox("Tree Widget")
        tree_layout = QVBoxLayout()
        
        tree_widget = QTreeWidget()
        tree_widget.setHeaderLabels(["Name", "Type", "Size"])
        
        # Add tree items
        root1 = QTreeWidgetItem(tree_widget, ["Documents", "Folder", ""])
        child1 = QTreeWidgetItem(root1, ["file1.txt", "Text File", "1.2 KB"])
        child2 = QTreeWidgetItem(root1, ["file2.pdf", "PDF File", "245 KB"])
        
        root2 = QTreeWidgetItem(tree_widget, ["Pictures", "Folder", ""])
        child3 = QTreeWidgetItem(root2, ["photo1.jpg", "JPEG Image", "2.1 MB"])
        child4 = QTreeWidgetItem(root2, ["photo2.png", "PNG Image", "856 KB"])
        
        tree_widget.expandAll()
        tree_widget.setToolTip("Hierarchical tree widget")
        
        tree_layout.addWidget(tree_widget)
        tree_group.setLayout(tree_layout)
        
        container_layout.addWidget(list_group)
        container_layout.addWidget(tree_group)
        container.setLayout(container_layout)
        
        # Table Widget
        table_group = QGroupBox("Table Widget")
        table_layout = QVBoxLayout()
        
        table_widget = QTableWidget(3, 4)
        table_widget.setHorizontalHeaderLabels(["Name", "Age", "City", "Country"])
        
        # Add table data
        data = [
            ["John Doe", "25", "New York", "USA"],
            ["Jane Smith", "30", "London", "UK"],
            ["Bob Johnson", "35", "Toronto", "Canada"]
        ]
        
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                table_widget.setItem(row, col, item)
        
        table_widget.setToolTip("Table widget for tabular data")
        
        table_layout.addWidget(table_widget)
        table_group.setLayout(table_layout)
        
        layout.addWidget(container)
        layout.addWidget(table_group)
        self.setLayout(layout)


class LayoutsTab(QWidget):
    """Tab demonstrating different layout managers"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Grid Layout Example
        grid_group = QGroupBox("Grid Layout")
        grid_layout = QGridLayout()
        
        for i in range(3):
            for j in range(3):
                btn = QPushButton(f"Button {i+1},{j+1}")
                btn.setToolTip(f"Grid position ({i+1}, {j+1})")
                grid_layout.addWidget(btn, i, j)
        
        grid_group.setLayout(grid_layout)
        
        # Form Layout Example
        form_group = QGroupBox("Form Layout")
        form_layout = QFormLayout()
        
        name_edit = QLineEdit()
        name_edit.setToolTip("Enter your name")
        email_edit = QLineEdit()
        email_edit.setToolTip("Enter your email")
        age_spin = QSpinBox()
        age_spin.setRange(1, 120)
        age_spin.setToolTip("Enter your age")
        
        form_layout.addRow("Name:", name_edit)
        form_layout.addRow("Email:", email_edit)
        form_layout.addRow("Age:", age_spin)
        
        form_group.setLayout(form_layout)
        
        # Splitter Example
        splitter_group = QGroupBox("Splitter")
        splitter_layout = QVBoxLayout()
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: lightblue;")
        left_label = QLabel("Left Panel")
        left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout = QVBoxLayout()
        left_layout.addWidget(left_label)
        left_widget.setLayout(left_layout)
        
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: lightgreen;")
        right_label = QLabel("Right Panel")
        right_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout = QVBoxLayout()
        right_layout.addWidget(right_label)
        right_widget.setLayout(right_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setToolTip("Resizable splitter between panels")
        
        splitter_layout.addWidget(splitter)
        splitter_group.setLayout(splitter_layout)
        
        main_layout.addWidget(grid_group)
        main_layout.addWidget(form_group)
        main_layout.addWidget(splitter_group)
        self.setLayout(main_layout)


class Qt6WidgetGallery(QMainWindow):
    """Main window showcasing Qt6 widgets organized in tabs"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()
        self.setup_navigation_shortcuts()
        self.current_focus_area = 0  # Track current focus area
    
    def init_ui(self):
        self.setWindowTitle("Qt6 Widget Gallery - PyQt6 Controls Reference")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        
        # Add tabs
        self.tab_widget.addTab(InputWidgetsTab(), "Input Controls")
        self.tab_widget.addTab(DisplayWidgetsTab(), "Display Widgets")
        self.tab_widget.addTab(TextWidgetsTab(), "Text & Combo")
        self.tab_widget.addTab(DateTimeWidgetsTab(), "Date & Time")
        self.tab_widget.addTab(ListTableWidgetsTab(), "Lists & Tables")
        self.tab_widget.addTab(LayoutsTab(), "Layouts")
        
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Add title
        title_label = QLabel("Qt6 Widget Gallery")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        info_label = QLabel("Comprehensive demonstration of PyQt6 controls with accessibility features")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: gray; margin-bottom: 10px;")
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(info_label)
        main_layout.addWidget(self.tab_widget)
        
        central_widget.setLayout(main_layout)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Use Tab key to navigate between controls, F6 to switch areas")
    
    def create_menu_bar(self):
        """Create menu bar with standard menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('&New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('Create new document')
        file_menu.addAction(new_action)
        
        open_action = QAction('&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open existing document')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        fullscreen_action = QAction('&Full Screen', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.setCheckable(True)
        fullscreen_action.setStatusTip('Toggle full screen mode')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        navigation_help_action = QAction('&Navigation Help', self)
        navigation_help_action.setShortcut('F1')
        navigation_help_action.setStatusTip('Show navigation help')
        navigation_help_action.triggered.connect(self.show_navigation_help)
        help_menu.addAction(navigation_help_action)
        
        help_menu.addSeparator()
        
        about_action = QAction('&About', self)
        about_action.setStatusTip('About this application')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_navigation_shortcuts(self):
        """Setup F6 navigation shortcuts for accessibility"""
        # F6 to cycle forward through focus areas
        f6_shortcut = QShortcut(QKeySequence("F6"), self)
        f6_shortcut.activated.connect(self.cycle_focus_areas)
        
        # Shift+F6 to cycle backward through focus areas
        shift_f6_shortcut = QShortcut(QKeySequence("Shift+F6"), self)
        shift_f6_shortcut.activated.connect(lambda: self.cycle_focus_areas(backward=True))
        
        # Escape to move focus out of edit controls
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.escape_focus)
        
        # Define focus areas (menu bar, tab bar, current tab content, status bar)
        self.focus_areas = []
    
    def cycle_focus_areas(self, backward=False):
        """Cycle through major focus areas using F6/Shift+F6"""
        # Update focus areas dynamically
        self.focus_areas = [
            self.menuBar(),
            self.tab_widget.tabBar(),
            self.tab_widget.currentWidget(),
            self.status_bar
        ]
        
        # Move to next/previous area
        if backward:
            self.current_focus_area = (self.current_focus_area - 1) % len(self.focus_areas)
        else:
            self.current_focus_area = (self.current_focus_area + 1) % len(self.focus_areas)
        
        # Set focus to the selected area
        focus_widget = self.focus_areas[self.current_focus_area]
        if focus_widget:
            focus_widget.setFocus()
            
            # Provide audio feedback about current area
            area_names = ["Menu Bar", "Tab Bar", "Tab Content", "Status Bar"]
            area_name = area_names[self.current_focus_area]
            self.status_bar.showMessage(f"Focus moved to: {area_name} - F6: Next area, Shift+F6: Previous area, Esc: Exit edit controls")
    
    def escape_focus(self):
        """Handle Escape key to move focus out of edit controls"""
        current_widget = self.focusWidget()
        if current_widget:
            # If we're in a text edit, move focus to parent or next logical widget
            if hasattr(current_widget, 'clearFocus'):
                current_widget.clearFocus()
                # Move focus to the tab widget or next suitable widget
                self.tab_widget.setFocus()
                self.status_bar.showMessage("Focus moved out of edit control - Use F6 to navigate between areas")
    
    def setup_timer(self):
        """Setup a timer to update dynamic content"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)  # Update every 5 seconds
    
    def update_status(self):
        """Update status bar with current time"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.status_bar.showMessage(f"Current time: {current_time} - F6: Switch areas, Tab: Navigate controls, F1: Help")
    
    def open_file(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
        )
        if file_path:
            self.status_bar.showMessage(f"Selected file: {file_path}")
    
    def toggle_fullscreen(self, checked):
        """Toggle full screen mode"""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()
    
    def show_navigation_help(self):
        """Show navigation help dialog"""
        QMessageBox.information(
            self,
            "Navigation Help",
            "Qt6 Widget Gallery - Keyboard Navigation\n\n"
            "🔑 Navigation Shortcuts:\n"
            "• Tab / Shift+Tab: Navigate between controls within current area\n"
            "• F6: Move to next major area (Menu → Tabs → Content → Status)\n"
            "• Shift+F6: Move to previous major area\n"
            "• Escape: Exit text edit controls and return to general navigation\n"
            "• F1: Show this help dialog\n"
            "• F11: Toggle full screen\n\n"
            "🎯 Focus Areas:\n"
            "1. Menu Bar: Access File, View, and Help menus\n"
            "2. Tab Bar: Switch between widget categories\n"
            "3. Tab Content: Interact with widgets in current tab\n"
            "4. Status Bar: View current status and time\n\n"
            "💡 Tips:\n"
            "• Use F6 when Tab gets stuck in text edit boxes\n"
            "• All widgets have tooltips - hover or use accessibility tools\n"
            "• Screen reader compatible with proper ARIA roles\n"
            "• Works with high contrast and other accessibility themes"
        )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Qt6 Widget Gallery",
            "Qt6 Widget Gallery\n\n"
            "A comprehensive demonstration of PyQt6 controls and widgets.\n"
            "This application showcases:\n"
            "• Input controls (buttons, checkboxes, radio buttons)\n"
            "• Display widgets (labels, progress bars, sliders)\n"
            "• Text input controls (line edits, text areas)\n"
            "• Date and time widgets\n"
            "• Lists, trees, and tables\n"
            "• Layout managers\n\n"
            "All controls include accessibility features like tooltips,\n"
            "keyboard navigation, and screen reader support.\n\n"
            "Built with PyQt6"
        )


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Qt6 Widget Gallery")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("PyQt6 Examples")
    
    # Create and show main window
    gallery = Qt6WidgetGallery()
    gallery.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
