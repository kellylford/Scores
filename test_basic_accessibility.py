#!/usr/bin/env python3
"""
Basic accessibility test for macOS VoiceOver
Tests if PyQt6 list widgets work with screen readers and keyboard navigation
"""

import sys
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                           QWidget, QListWidget, QListWidgetItem, QPushButton, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class BasicAccessibilityTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic VoiceOver Test")
        self.setGeometry(100, 100, 400, 600)
        
        # Set accessibility properties for the main window
        self.setAccessibleName("Basic VoiceOver Test Window")
        self.setAccessibleDescription("Simple test window to verify VoiceOver functionality with PyQt6")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add a title label
        title = QLabel("VoiceOver Test - Sports List")
        title.setAccessibleName("Title")
        title.setAccessibleDescription("Test application title")
        title.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Add instructions
        instructions = QLabel("Use VoiceOver (VO + Arrow keys) or Tab/Arrow keys to navigate")
        instructions.setAccessibleName("Instructions")
        instructions.setAccessibleDescription("Navigation instructions for testing")
        instructions.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 5px; background: #f0f0f0;")
        layout.addWidget(instructions)
        
        # Create a simple list with sports
        self.sports_list = QListWidget()
        self.sports_list.setAccessibleName("Sports Selection List")
        self.sports_list.setAccessibleDescription("List of available sports for testing navigation")
        self.sports_list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Add sports items to the list
        sports = [
            "⚾ Major League Baseball (MLB)",
            "🏈 National Football League (NFL)", 
            "🏀 National Basketball Association (NBA)",
            "🏒 National Hockey League (NHL)",
            "⚽ Major League Soccer (MLS)",
            "🎾 Professional Tennis",
            "🏌️ Professional Golf"
        ]
        
        for sport in sports:
            item = QListWidgetItem(sport)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            # Set accessibility for each item
            item.setData(Qt.ItemDataRole.AccessibleTextRole, sport)
            item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"Sport option: {sport}")
            self.sports_list.addItem(item)
        
        # Connect selection signal
        self.sports_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.sports_list.itemClicked.connect(self.on_item_clicked)
        
        layout.addWidget(self.sports_list)
        
        # Add status label
        self.status_label = QLabel("Status: No sport selected")
        self.status_label.setAccessibleName("Status")
        self.status_label.setAccessibleDescription("Current selection status")
        self.status_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.status_label.setStyleSheet("padding: 10px; background: #e8f4f8; border: 1px solid #ccc;")
        layout.addWidget(self.status_label)
        
        # Add test button
        test_button = QPushButton("Test Button - Press Enter or Space")
        test_button.setAccessibleName("Test Button")
        test_button.setAccessibleDescription("Button to test keyboard activation")
        test_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        test_button.clicked.connect(self.on_button_clicked)
        layout.addWidget(test_button)
        
        # Set initial focus to the list
        self.sports_list.setFocus()
        if self.sports_list.count() > 0:
            self.sports_list.setCurrentRow(0)
    
    def on_selection_changed(self):
        """Handle list selection changes"""
        current_item = self.sports_list.currentItem()
        if current_item:
            text = current_item.text()
            self.status_label.setText(f"Selected: {text}")
            self.status_label.setAccessibleDescription(f"Currently selected sport: {text}")
            print(f"Selection changed to: {text}")
    
    def on_item_clicked(self, item):
        """Handle item clicks"""
        text = item.text()
        print(f"Item clicked: {text}")
        # Announce the selection
        self.status_label.setText(f"Clicked: {text}")
    
    def on_button_clicked(self):
        """Handle button clicks"""
        current_item = self.sports_list.currentItem()
        if current_item:
            text = current_item.text()
            self.status_label.setText(f"Button pressed - Current selection: {text}")
            print(f"Button clicked with selection: {text}")
        else:
            self.status_label.setText("Button pressed - No selection")
            print("Button clicked with no selection")

def main():
    """Main function to run the test"""
    app = QApplication(sys.argv)
    
    # macOS specific setup
    if platform.system() == "Darwin":
        # Set application properties
        app.setApplicationName("VoiceOver Test")
        app.setApplicationDisplayName("Basic VoiceOver Test")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("Test")
        app.setOrganizationDomain("test.local")
        
        # Set accessibility attributes for macOS
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTabletEvents, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTouchEvents, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_MacDontSwapCtrlAndMeta, True)
        except AttributeError:
            pass  # Ignore if attributes don't exist
        
        # Set larger font for better visibility
        font = QFont()
        font.setPointSize(14)
        app.setFont(font)
    
    # Create and show the test window
    window = BasicAccessibilityTest()
    window.show()
    window.activateWindow()
    window.raise_()
    window.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
    
    print("=== VoiceOver Test Started ===")
    print("Instructions:")
    print("1. Enable VoiceOver: System Preferences > Accessibility > VoiceOver")
    print("2. Use VO + Arrow keys to navigate")
    print("3. Use Tab key to move between major elements")
    print("4. Use Up/Down arrows in the list to select items")
    print("5. Press Enter or Space on the button")
    print("6. Watch console output for interaction feedback")
    print("================================")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
