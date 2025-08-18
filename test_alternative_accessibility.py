#!/usr/bin/env python3
"""
Alternative VoiceOver approaches - using buttons and tables instead of lists
"""

import sys
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                           QWidget, QPushButton, QLabel, QTableWidget, 
                           QTableWidgetItem, QButtonGroup, QRadioButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class AlternativeAccessibilityTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alternative VoiceOver Approaches")
        self.setGeometry(100, 100, 600, 700)
        
        # Window accessibility
        self.setAccessibleName("Alternative VoiceOver Test")
        self.setAccessibleDescription("Testing button and table approaches for VoiceOver")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Alternative Approaches for VoiceOver")
        title.setAccessibleName("Test Title")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Status (create early so methods can use it)
        self.status = QLabel("Status: Ready for testing")
        self.status.setAccessibleName("Test Status")
        self.status.setStyleSheet("padding: 10px; background: #f0f0f0; margin-bottom: 20px;")
        layout.addWidget(self.status)
        
        # Approach 1: Radio Buttons (often work well with screen readers)
        layout.addWidget(QLabel("Approach 1: Radio Buttons"))
        self.create_radio_buttons(layout)
        
        # Approach 2: Regular Buttons
        layout.addWidget(QLabel("Approach 2: Push Buttons"))
        self.create_push_buttons(layout)
        
        # Approach 3: Table Widget (single column)
        layout.addWidget(QLabel("Approach 3: Single-Column Table"))
        self.create_table(layout)
    
    def create_radio_buttons(self, layout):
        """Create radio button group"""
        radio_container = QWidget()
        radio_layout = QVBoxLayout(radio_container)
        
        self.radio_group = QButtonGroup()
        sports = ["Baseball", "Football", "Basketball", "Hockey"]
        
        for i, sport in enumerate(sports):
            radio = QRadioButton(sport)
            radio.setAccessibleName(f"Sport Option: {sport}")
            radio.setAccessibleDescription(f"Select {sport} as your preferred sport")
            radio.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            
            # Set first one as default
            if i == 0:
                radio.setChecked(True)
            
            radio.toggled.connect(lambda checked, s=sport: 
                                self.update_status(f"Radio selected: {s}") if checked else None)
            
            self.radio_group.addButton(radio)
            radio_layout.addWidget(radio)
        
        layout.addWidget(radio_container)
    
    def create_push_buttons(self, layout):
        """Create push button group"""
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        
        sports = ["Baseball", "Football", "Basketball", "Hockey"]
        
        for sport in sports:
            btn = QPushButton(sport)
            btn.setAccessibleName(f"{sport} Button")
            btn.setAccessibleDescription(f"Click to select {sport}")
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setMinimumHeight(40)
            
            btn.clicked.connect(lambda checked, s=sport: 
                              self.update_status(f"Button clicked: {s}"))
            
            button_layout.addWidget(btn)
        
        layout.addWidget(button_container)
    
    def create_table(self, layout):
        """Create single-column table"""
        table = QTableWidget()
        table.setAccessibleName("Sports Selection Table")
        table.setAccessibleDescription("Table of sports options - use arrow keys to navigate")
        table.setMaximumHeight(150)
        
        # Set up table structure
        sports = ["Baseball", "Football", "Basketball", "Hockey"]
        table.setRowCount(len(sports))
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels(["Sport"])
        
        # Add items to table
        for i, sport in enumerate(sports):
            item = QTableWidgetItem(sport)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Sport: {sport}")
            item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"Table row {i+1}: {sport}")
            table.setItem(i, 0, item)
        
        # Configure table
        table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        
        # Connect selection signal
        table.currentItemChanged.connect(
            lambda current, previous: 
            self.update_status(f"Table selected: {current.text()}") if current else None
        )
        
        # Set initial selection
        table.selectRow(0)
        
        layout.addWidget(table)
    
    def update_status(self, message):
        """Update status display"""
        self.status.setText(f"Status: {message}")
        self.status.setAccessibleDescription(f"Current status: {message}")
        print(message)

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # macOS setup
    if platform.system() == "Darwin":
        app.setApplicationName("Alternative VoiceOver Test")
        app.setApplicationDisplayName("Alternative VoiceOver Test")
        
        # Accessibility attributes
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTabletEvents, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_MacDontSwapCtrlAndMeta, True)
        except:
            pass
        
        # Larger font for visibility
        font = QFont()
        font.setPointSize(14)
        app.setFont(font)
    
    window = AlternativeAccessibilityTest()
    window.show()
    window.activateWindow()
    window.raise_()
    
    print("=== Alternative VoiceOver Test ===")
    print("Testing alternatives to lists:")
    print("1. Radio Buttons - Tab between them")
    print("2. Push Buttons - Tab and click/press")
    print("3. Table Widget - Arrow keys to navigate")
    print("")
    print("VoiceOver navigation:")
    print("- VO + Arrow keys for exploration")
    print("- Tab to move between sections")
    print("- Space/Enter to activate buttons")
    print("- Arrow keys for table navigation")
    print("===================================")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
