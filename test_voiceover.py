#!/usr/bin/env python3
"""
Simple test to verify VoiceOver functionality with basic PyQt6 elements
"""

import sys
import platform
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt

def main():
    app = QApplication(sys.argv)
    
    # Basic macOS setup
    if platform.system() == "Darwin":
        app.setApplicationName("VoiceOver Test")
        app.setApplicationDisplayName("VoiceOver Test")
    
    # Create main window
    window = QWidget()
    window.setWindowTitle("VoiceOver Test")
    window.setAccessibleName("VoiceOver Test Window")
    window.setAccessibleDescription("Test window for VoiceOver functionality")
    
    layout = QVBoxLayout()
    
    # Add a label
    label = QLabel("Test Label - VoiceOver should read this")
    label.setAccessibleName("Test Label")
    label.setAccessibleDescription("This is a test label for VoiceOver")
    layout.addWidget(label)
    
    # Add a button
    button = QPushButton("Test Button")
    button.setAccessibleName("Test Button")
    button.setAccessibleDescription("Click this button to test VoiceOver")
    button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    button.clicked.connect(lambda: print("Button clicked!"))
    layout.addWidget(button)
    
    # Add a list widget
    list_widget = QListWidget()
    list_widget.setAccessibleName("Test List")
    list_widget.setAccessibleDescription("List with test items for VoiceOver navigation")
    list_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    for i in range(5):
        item = QListWidgetItem(f"List Item {i+1}")
        item.setAccessibleText(f"List item number {i+1}")
        list_widget.addItem(item)
    
    layout.addWidget(list_widget)
    
    window.setLayout(layout)
    window.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    # Show window
    window.show()
    window.activateWindow()
    window.raise_()
    
    # Set initial focus
    label.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
    
    print("VoiceOver Test Window launched")
    print("- Try Tab to navigate between elements")
    print("- Try VoiceOver (VO + arrow keys) to navigate")
    print("- Elements should be announced by VoiceOver")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
