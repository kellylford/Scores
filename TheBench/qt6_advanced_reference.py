#!/usr/bin/env python3
"""
Qt6 Advanced Controls Reference
Demonstrates advanced Qt6 widgets and accessibility best practices.

This companion to the widget gallery shows:
- Advanced accessibility features
- Custom widgets
- Graphics view framework
- Model/View programming
- Advanced layouts
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeView, QTableView, QListView, QScrollArea,
    QGroupBox, QLabel, QPushButton, QCheckBox, QComboBox,
    QProgressBar, QSlider, QGraphicsView, QGraphicsScene,
    QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsTextItem, QFrame, QTabWidget, QTextBrowser,
    QHeaderView, QAbstractItemView, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QAbstractTableModel, QAbstractListModel, QModelIndex,
    QVariant, QTimer, pyqtSignal, QRect, QRectF, QPointF
)
from PyQt6.QtGui import (
    QStandardItemModel, QStandardItem, QFont, QColor, QPen,
    QBrush, QPainter, QPixmap, QIcon, QAction, QKeySequence
)


class AccessibleTableModel(QAbstractTableModel):
    """Table model with accessibility features"""
    
    def __init__(self, data=None):
        super().__init__()
        self.headers = ['Name', 'Position', 'Office', 'Age', 'Start Date', 'Salary']
        self.table_data = data or [
            ['Airi Satou', 'Accountant', 'Tokyo', '33', '2008/11/28', '$162,700'],
            ['Angelica Ramos', 'Chief Executive Officer (CEO)', 'London', '47', '2009/10/09', '$1,200,000'],
            ['Ashton Cox', 'Junior Technical Author', 'San Francisco', '66', '2009/01/12', '$86,000'],
            ['Bradley Greer', 'Software Engineer', 'London', '41', '2012/10/13', '$132,000'],
            ['Brenden Wagner', 'Software Engineer', 'San Francisco', '28', '2011/06/07', '$206,850'],
            ['Brielle Williamson', 'Integration Specialist', 'New York', '61', '2012/12/02', '$372,000'],
            ['Bruno Nash', 'Software Engineer', 'London', '38', '2011/05/03', '$163,500'],
            ['Caesar Vance', 'Pre-Sales Support', 'New York', '21', '2011/12/12', '$106,450'],
            ['Cara Stevens', 'Sales Assistant', 'New York', '46', '2011/12/06', '$145,600'],
            ['Cedric Kelly', 'Senior Javascript Developer', 'Edinburgh', '22', '2012/03/29', '$433,060']
        ]
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.table_data)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        if role == Qt.ItemDataRole.DisplayRole:
            return self.table_data[index.row()][index.column()]
        elif role == Qt.ItemDataRole.AccessibleTextRole:
            # Provide accessible description for screen readers
            header = self.headers[index.column()]
            value = self.table_data[index.row()][index.column()]
            return f"{header}: {value}"
        elif role == Qt.ItemDataRole.AccessibleDescriptionRole:
            return f"Row {index.row() + 1}, Column {index.column() + 1}"
        elif role == Qt.ItemDataRole.ToolTipRole:
            header = self.headers[index.column()]
            value = self.table_data[index.row()][index.column()]
            return f"{header}: {value}"
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        elif orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.AccessibleTextRole:
            return f"Column header: {self.headers[section]}"
        return QVariant()


class AccessibleListModel(QAbstractListModel):
    """List model with accessibility features"""
    
    def __init__(self, items=None):
        super().__init__()
        self.items = items or [
            'Dashboard Overview',
            'User Management',
            'System Settings',
            'Reports & Analytics',
            'Data Import/Export',
            'Backup & Recovery',
            'Security Settings',
            'API Configuration',
            'Plugin Management',
            'Help & Documentation'
        ]
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.items)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        if role == Qt.ItemDataRole.DisplayRole:
            return self.items[index.row()]
        elif role == Qt.ItemDataRole.AccessibleTextRole:
            return f"Menu item {index.row() + 1}: {self.items[index.row()]}"
        elif role == Qt.ItemDataRole.AccessibleDescriptionRole:
            return f"List item {index.row() + 1} of {len(self.items)}"
        elif role == Qt.ItemDataRole.ToolTipRole:
            return f"Click to select: {self.items[index.row()]}"
        
        return QVariant()


class AccessibleGraphicsView(QGraphicsView):
    """Graphics view with accessibility support"""
    
    def __init__(self):
        super().__init__()
        self.setup_scene()
        self.setup_accessibility()
    
    def setup_scene(self):
        """Create a sample graphics scene"""
        scene = QGraphicsScene()
        scene.setSceneRect(0, 0, 400, 300)
        
        # Add various graphics items
        rect_item = QGraphicsRectItem(50, 50, 100, 80)
        rect_item.setBrush(QBrush(QColor(100, 150, 200)))
        rect_item.setPen(QPen(QColor(0, 0, 0), 2))
        rect_item.setToolTip("Blue rectangle")
        scene.addItem(rect_item)
        
        ellipse_item = QGraphicsEllipseItem(200, 100, 120, 60)
        ellipse_item.setBrush(QBrush(QColor(200, 100, 150)))
        ellipse_item.setPen(QPen(QColor(0, 0, 0), 2))
        ellipse_item.setToolTip("Pink ellipse")
        scene.addItem(ellipse_item)
        
        text_item = QGraphicsTextItem("Sample Text")
        text_item.setPos(100, 200)
        text_item.setFont(QFont("Arial", 14))
        text_item.setToolTip("Sample text item")
        scene.addItem(text_item)
        
        self.setScene(scene)
    
    def setup_accessibility(self):
        """Configure accessibility features"""
        self.setAccessibleName("Graphics View")
        self.setAccessibleDescription("Interactive graphics view with shapes and text")
        self.setToolTip("Use arrow keys to navigate, Space to select items")


class AdvancedControlsTab(QWidget):
    """Tab showing advanced controls and accessibility"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Model/View Section
        model_view_group = QGroupBox("Model/View Programming")
        model_view_layout = QHBoxLayout()
        
        # Table View with custom model
        table_container = QWidget()
        table_layout = QVBoxLayout()
        table_label = QLabel("Accessible Table View")
        table_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        table_view = QTableView()
        table_model = AccessibleTableModel()
        table_view.setModel(table_model)
        
        # Configure table accessibility
        table_view.setAccessibleName("Employee Data Table")
        table_view.setAccessibleDescription("Table showing employee information with sortable columns")
        table_view.setToolTip("Use Tab to navigate cells, Space to sort columns")
        table_view.setAlternatingRowColors(True)
        table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table_view.setSortingEnabled(True)
        
        # Set column widths
        header = table_view.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(table_model.columnCount()):
            table_view.setColumnWidth(i, 120)
        
        table_layout.addWidget(table_label)
        table_layout.addWidget(table_view)
        table_container.setLayout(table_layout)
        
        # List View with custom model
        list_container = QWidget()
        list_layout = QVBoxLayout()
        list_label = QLabel("Accessible List View")
        list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        list_view = QListView()
        list_model = AccessibleListModel()
        list_view.setModel(list_model)
        
        # Configure list accessibility
        list_view.setAccessibleName("Navigation Menu")
        list_view.setAccessibleDescription("List of application menu items")
        list_view.setToolTip("Use arrow keys to navigate, Enter to select")
        list_view.setAlternatingRowColors(True)
        
        list_layout.addWidget(list_label)
        list_layout.addWidget(list_view)
        list_container.setLayout(list_layout)
        
        model_view_layout.addWidget(table_container, 2)
        model_view_layout.addWidget(list_container, 1)
        model_view_group.setLayout(model_view_layout)
        
        # Graphics View Section
        graphics_group = QGroupBox("Graphics View Framework")
        graphics_layout = QVBoxLayout()
        
        graphics_label = QLabel("Interactive Graphics Scene")
        graphics_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        graphics_view = AccessibleGraphicsView()
        graphics_view.setMaximumHeight(200)
        
        graphics_layout.addWidget(graphics_label)
        graphics_layout.addWidget(graphics_view)
        graphics_group.setLayout(graphics_layout)
        
        layout.addWidget(model_view_group)
        layout.addWidget(graphics_group)
        self.setLayout(layout)


class AccessibilityFeaturesTab(QWidget):
    """Tab demonstrating accessibility best practices"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Accessibility Guidelines
        guidelines_group = QGroupBox("Accessibility Best Practices")
        guidelines_layout = QVBoxLayout()
        
        guidelines_text = QTextBrowser()
        guidelines_text.setMaximumHeight(200)
        guidelines_content = """
<h3>Qt6 Accessibility Features Demonstrated:</h3>
<ul>
<li><b>Keyboard Navigation:</b> All controls support Tab/Shift+Tab navigation</li>
<li><b>Screen Reader Support:</b> AccessibleTextRole and AccessibleDescriptionRole provide context</li>
<li><b>Tooltips:</b> Hover help text for all interactive elements</li>
<li><b>Focus Indicators:</b> Clear visual focus indicators for keyboard users</li>
<li><b>High Contrast:</b> Works with system high contrast themes</li>
<li><b>Semantic Structure:</b> Proper widget hierarchy and grouping</li>
</ul>

<h3>Testing Your Application:</h3>
<ul>
<li>Test with Tab-only navigation (no mouse)</li>
<li>Test with screen readers (NVDA, JAWS, VoiceOver)</li>
<li>Test with high contrast mode enabled</li>
<li>Verify all interactive elements have tooltips</li>
<li>Check that focus is clearly visible</li>
</ul>
        """
        guidelines_text.setHtml(guidelines_content)
        guidelines_text.setAccessibleName("Accessibility Guidelines")
        guidelines_text.setAccessibleDescription("Guidelines for creating accessible Qt applications")
        
        guidelines_layout.addWidget(guidelines_text)
        guidelines_group.setLayout(guidelines_layout)
        
        # Interactive Accessibility Demo
        demo_group = QGroupBox("Interactive Accessibility Demo")
        demo_layout = QVBoxLayout()
        
        # Keyboard navigation demo
        nav_label = QLabel("Keyboard Navigation Test:")
        nav_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        nav_container = QWidget()
        nav_layout = QHBoxLayout()
        
        for i in range(5):
            btn = QPushButton(f"Button {i+1}")
            btn.setAccessibleName(f"Navigation Button {i+1}")
            btn.setAccessibleDescription(f"Test button {i+1} for keyboard navigation")
            btn.setToolTip(f"Button {i+1} - Use Tab to navigate, Space/Enter to activate")
            btn.clicked.connect(lambda checked, num=i+1: self.button_clicked(num))
            nav_layout.addWidget(btn)
        
        nav_container.setLayout(nav_layout)
        
        # Screen reader test elements
        sr_label = QLabel("Screen Reader Test Elements:")
        sr_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.status_label = QLabel("Click any button to test accessibility")
        self.status_label.setAccessibleName("Status Message")
        self.status_label.setAccessibleDescription("Displays the result of button interactions")
        self.status_label.setStyleSheet("border: 1px solid gray; padding: 5px; background-color: #f0f0f0;")
        
        # Progress indicator with accessibility
        progress_label = QLabel("Progress Indicator:")
        progress_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setAccessibleName("Demo Progress Bar")
        self.progress.setAccessibleDescription("Shows progress of demo operation")
        self.progress.setToolTip("Progress indicator - use Space to start/stop")
        
        progress_btn = QPushButton("Start Progress Demo")
        progress_btn.setAccessibleName("Start Progress")
        progress_btn.setAccessibleDescription("Starts the progress bar demonstration")
        progress_btn.setToolTip("Click to start progress bar animation")
        progress_btn.clicked.connect(self.start_progress)
        
        demo_layout.addWidget(nav_label)
        demo_layout.addWidget(nav_container)
        demo_layout.addWidget(sr_label)
        demo_layout.addWidget(self.status_label)
        demo_layout.addWidget(progress_label)
        demo_layout.addWidget(self.progress)
        demo_layout.addWidget(progress_btn)
        
        demo_group.setLayout(demo_layout)
        
        layout.addWidget(guidelines_group)
        layout.addWidget(demo_group)
        layout.addStretch()
        self.setLayout(layout)
        
        # Setup progress timer
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_value = 0
    
    def button_clicked(self, button_num):
        """Handle button click with accessibility feedback"""
        message = f"Button {button_num} was activated!"
        self.status_label.setText(message)
        self.status_label.setAccessibleDescription(f"Status updated: {message}")
        
        # Visual feedback
        sender = self.sender()
        original_style = sender.styleSheet()
        sender.setStyleSheet("background-color: lightgreen;")
        
        # Reset style after 1 second
        QTimer.singleShot(1000, lambda: sender.setStyleSheet(original_style))
    
    def start_progress(self):
        """Start progress bar demonstration"""
        if self.progress_timer.isActive():
            self.progress_timer.stop()
            self.sender().setText("Start Progress Demo")
            self.status_label.setText("Progress stopped")
        else:
            self.progress_value = 0
            self.progress.setValue(0)
            self.progress_timer.start(100)  # Update every 100ms
            self.sender().setText("Stop Progress Demo")
            self.status_label.setText("Progress started")
    
    def update_progress(self):
        """Update progress bar value"""
        self.progress_value += 2
        self.progress.setValue(self.progress_value)
        
        if self.progress_value >= 100:
            self.progress_timer.stop()
            self.sender().setText("Start Progress Demo")
            self.status_label.setText("Progress completed!")
            self.progress_value = 0


class Qt6AdvancedReference(QMainWindow):
    """Advanced Qt6 controls and accessibility reference"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Qt6 Advanced Controls & Accessibility Reference")
        self.setGeometry(150, 150, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Add tabs
        tab_widget.addTab(AdvancedControlsTab(), "Advanced Controls")
        tab_widget.addTab(AccessibilityFeaturesTab(), "Accessibility Demo")
        
        # Main layout
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Qt6 Advanced Controls & Accessibility Reference")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        subtitle_label = QLabel("Model/View programming, Graphics View, and accessibility best practices")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: gray; margin-bottom: 10px;")
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(tab_widget)
        
        central_widget.setLayout(layout)
        
        # Status bar
        self.statusBar().showMessage("Advanced Qt6 features - All controls support keyboard navigation and screen readers")
        
        # Configure window accessibility
        self.setAccessibleName("Qt6 Advanced Reference")
        self.setAccessibleDescription("Demonstration of advanced Qt6 controls and accessibility features")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Qt6 Advanced Reference")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("PyQt6 Examples")
    
    # Create and show main window
    reference = Qt6AdvancedReference()
    reference.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
