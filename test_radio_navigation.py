#!/usr/bin/env python3
"""
Test radio button navigation behavior
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QRadioButton, QButtonGroup, QLabel
from PyQt6.QtCore import Qt

class RadioButtonTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radio Button Navigation Test")
        self.setGeometry(100, 100, 400, 200)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        layout.addWidget(QLabel("Test radio button navigation with arrow keys:"))
        layout.addWidget(QLabel("• Left/Right arrows should work"))
        layout.addWidget(QLabel("• Up/Down arrows should also work"))
        layout.addWidget(QLabel("• Tab should move between radio button group and other controls"))
        layout.addWidget(QLabel(""))
        
        # Create radio button group
        self.view_group = QButtonGroup()
        
        self.basic_radio = QRadioButton("Basic View")
        self.expanded_radio = QRadioButton("Expanded View")
        self.third_radio = QRadioButton("Third Option (test)")
        
        # Set up radio button group
        self.view_group.addButton(self.basic_radio, 0)
        self.view_group.addButton(self.expanded_radio, 1)
        self.view_group.addButton(self.third_radio, 2)
        self.basic_radio.setChecked(True)
        
        # Ensure proper focus policy for arrow key navigation
        self.basic_radio.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.expanded_radio.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.third_radio.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Set accessibility properties
        self.basic_radio.setAccessibleName("Basic view option")
        self.expanded_radio.setAccessibleName("Expanded view option")
        self.third_radio.setAccessibleName("Third option")
        
        layout.addWidget(self.basic_radio)
        layout.addWidget(self.expanded_radio)
        layout.addWidget(self.third_radio)
        
        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("Instructions:"))
        layout.addWidget(QLabel("1. Click on any radio button to focus the group"))
        layout.addWidget(QLabel("2. Use arrow keys (↑↓←→) to navigate between options"))
        layout.addWidget(QLabel("3. All four arrow keys should work for navigation"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RadioButtonTest()
    window.show()
    sys.exit(app.exec())
