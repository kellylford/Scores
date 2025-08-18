#!/usr/bin/env python3
"""
VoiceOver-specific accessibility test for PyQt6 lists
Tests different approaches to make list items readable by VoiceOver
"""

import sys
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                           QWidget, QListWidget, QListWidgetItem, QPushButton, 
                           QLabel, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

class VoiceOverListTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceOver List Test")
        self.setGeometry(100, 100, 600, 700)
        
        # Set window accessibility
        self.setAccessibleName("VoiceOver List Test Window")
        self.setAccessibleDescription("Testing different approaches for VoiceOver list reading")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add title
        title = QLabel("VoiceOver List Accessibility Test")
        title.setAccessibleName("Main Title")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Test 1: Basic QListWidget (what we tried before)
        self.add_section(layout, "Test 1: Basic QListWidget", self.create_basic_list())
        
        # Test 2: QComboBox (often works better with VoiceOver)
        self.add_section(layout, "Test 2: QComboBox (Alternative)", self.create_combo_box())
        
        # Test 3: QListWidget with explicit focus and selection
        self.add_section(layout, "Test 3: Enhanced QListWidget", self.create_enhanced_list())
        
        # Status area
        self.status_text = QTextEdit()
        self.status_text.setAccessibleName("Test Results")
        self.status_text.setAccessibleDescription("Live feedback from accessibility tests")
        self.status_text.setMaximumHeight(150)
        self.status_text.setPlainText("Test Status: Ready for testing\n\nInstructions:\n1. Use VO + Left/Right arrows to navigate between sections\n2. Use VO + Up/Down arrows within each section\n3. Watch this area for feedback")
        layout.addWidget(QLabel("Live Test Feedback:"))
        layout.addWidget(self.status_text)
        
        # Focus on first test
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def add_section(self, layout, title, widget):
        """Add a test section with title and widget"""
        section_label = QLabel(title)
        section_label.setAccessibleName(title)
        section_label.setAccessibleDescription(f"Test section: {title}")
        section_label.setStyleSheet("font-weight: bold; margin-top: 10px; padding: 5px; background: #e8f4f8;")
        layout.addWidget(section_label)
        layout.addWidget(widget)
    
    def create_basic_list(self):
        """Create basic QListWidget (original approach)"""
        list_widget = QListWidget()
        list_widget.setAccessibleName("Basic Sports List")
        list_widget.setAccessibleDescription("Simple list widget with sports items")
        list_widget.setMaximumHeight(120)
        
        sports = ["Baseball", "Football", "Basketball", "Hockey"]
        for i, sport in enumerate(sports):
            item = QListWidgetItem(sport)
            # Set accessibility data for the item
            item.setData(Qt.ItemDataRole.AccessibleTextRole, sport)
            item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"Sport option {i+1}: {sport}")
            item.setToolTip(f"Sport option {i+1}: {sport}")  # Tooltip might help
            list_widget.addItem(item)
        
        list_widget.itemSelectionChanged.connect(
            lambda: self.update_status(f"Basic list selection: {list_widget.currentItem().text() if list_widget.currentItem() else 'None'}")
        )
        
        return list_widget
    
    def create_combo_box(self):
        """Create QComboBox as alternative (often works better with screen readers)"""
        combo = QComboBox()
        combo.setAccessibleName("Sports Combo Box")
        combo.setAccessibleDescription("Dropdown list of sports - may work better with VoiceOver")
        
        sports = ["Select a sport...", "Baseball", "Football", "Basketball", "Hockey"]
        combo.addItems(sports)
        
        combo.currentTextChanged.connect(
            lambda text: self.update_status(f"Combo box selection: {text}")
        )
        
        return combo
    
    def create_enhanced_list(self):
        """Create enhanced QListWidget with more accessibility features"""
        container = QWidget()
        layout = QVBoxLayout(container)
        
        list_widget = QListWidget()
        list_widget.setAccessibleName("Enhanced Sports List")
        list_widget.setAccessibleDescription("Enhanced list with improved VoiceOver support")
        list_widget.setMaximumHeight(120)
        
        # Set additional properties that might help VoiceOver
        list_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        
        sports = ["Baseball", "Football", "Basketball", "Hockey"]
        for i, sport in enumerate(sports):
            item = QListWidgetItem(f"{i+1}. {sport}")
            # Try multiple accessibility approaches
            item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Item {i+1}: {sport}")
            item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"Sport option {i+1}: {sport}")
            item.setToolTip(f"Sport {i+1}: {sport}")
            list_widget.addItem(item)
        
        # Add selection feedback
        current_label = QLabel("Current selection: None")
        current_label.setAccessibleName("Current Selection Display")
        
        def on_selection_change():
            current = list_widget.currentItem()
            if current:
                text = current.text()
                current_label.setText(f"Current selection: {text}")
                current_label.setAccessibleDescription(f"Currently selected: {text}")
                self.update_status(f"Enhanced list selection: {text}")
                
                # Try to announce the selection (this might help VoiceOver)
                # QAccessible not available in this PyQt6 version
        
        list_widget.itemSelectionChanged.connect(on_selection_change)
        list_widget.currentItemChanged.connect(on_selection_change)
        
        layout.addWidget(list_widget)
        layout.addWidget(current_label)
        
        # Set initial selection
        if list_widget.count() > 0:
            list_widget.setCurrentRow(0)
        
        return container
    
    def update_status(self, message):
        """Update status text area"""
        current_text = self.status_text.toPlainText()
        new_text = f"{current_text}\n{message}"
        self.status_text.setPlainText(new_text)
        # Scroll to bottom
        cursor = self.status_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.status_text.setTextCursor(cursor)
        
        print(f"Status update: {message}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # macOS specific setup
    if platform.system() == "Darwin":
        app.setApplicationName("VoiceOver List Test")
        app.setApplicationDisplayName("VoiceOver List Test")
        app.setApplicationVersion("1.0")
        
        # macOS accessibility attributes
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTabletEvents, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_MacDontSwapCtrlAndMeta, True)
        except AttributeError:
            pass
        
        # Larger font
        font = QFont()
        font.setPointSize(14)
        app.setFont(font)
    
    window = VoiceOverListTest()
    window.show()
    window.activateWindow()
    window.raise_()
    
    print("=== VoiceOver List Test Started ===")
    print("This test checks 3 different approaches:")
    print("1. Basic QListWidget (what failed)")
    print("2. QComboBox (alternative approach)")
    print("3. Enhanced QListWidget (with more accessibility)")
    print("")
    print("VoiceOver Testing:")
    print("- VO + Left/Right: Move between sections")
    print("- VO + Up/Down: Navigate within sections")
    print("- Tab: Move between major elements")
    print("- Space/Enter: Activate selected items")
    print("=====================================")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
