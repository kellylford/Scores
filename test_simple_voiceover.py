#!/usr/bin/env python3
"""
Simple VoiceOver test focusing on different list approaches
"""

import sys
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                           QWidget, QListWidget, QListWidgetItem, 
                           QLabel, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SimpleVoiceOverTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple VoiceOver Test")
        self.setGeometry(100, 100, 500, 600)
        
        # Window accessibility
        self.setAccessibleName("VoiceOver Test Window")
        self.setAccessibleDescription("Testing PyQt6 lists with VoiceOver")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("VoiceOver Test: Three Approaches")
        title.setAccessibleName("Test Title")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Approach 1: Standard QListWidget
        layout.addWidget(QLabel("Approach 1: Standard QListWidget"))
        list1 = QListWidget()
        list1.setAccessibleName("Standard List")
        list1.setAccessibleDescription("Standard PyQt6 list widget")
        list1.setMaximumHeight(100)
        
        for sport in ["Baseball", "Football", "Basketball"]:
            item = QListWidgetItem(sport)
            list1.addItem(item)
        
        layout.addWidget(list1)
        
        # Approach 2: QComboBox 
        layout.addWidget(QLabel("Approach 2: QComboBox (Dropdown)"))
        combo = QComboBox()
        combo.setAccessibleName("Sports Dropdown")
        combo.setAccessibleDescription("Dropdown list of sports")
        combo.addItems(["Select...", "Baseball", "Football", "Basketball"])
        layout.addWidget(combo)
        
        # Approach 3: QListWidget with enhanced accessibility
        layout.addWidget(QLabel("Approach 3: Enhanced QListWidget"))
        list2 = QListWidget()
        list2.setAccessibleName("Enhanced Sports List")
        list2.setAccessibleDescription("Enhanced list with better VoiceOver support")
        list2.setMaximumHeight(100)
        list2.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        sports = ["Baseball", "Football", "Basketball"]
        for i, sport in enumerate(sports):
            item = QListWidgetItem(f"{i+1}. {sport}")
            item.setData(Qt.ItemDataRole.AccessibleTextRole, f"Option {i+1}: {sport}")
            item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f"Sport choice {i+1}: {sport}")
            item.setToolTip(f"Select {sport}")
            list2.addItem(item)
        
        layout.addWidget(list2)
        
        # Status
        self.status = QLabel("Status: Ready for testing")
        self.status.setAccessibleName("Test Status")
        self.status.setStyleSheet("padding: 10px; background: #f0f0f0; margin-top: 20px;")
        layout.addWidget(self.status)
        
        # Connect signals
        list1.currentTextChanged.connect(lambda text: self.update_status(f"Standard list: {text}"))
        combo.currentTextChanged.connect(lambda text: self.update_status(f"Combo box: {text}"))
        list2.currentTextChanged.connect(lambda text: self.update_status(f"Enhanced list: {text}"))
        
        # Set focus to first list
        list1.setFocus()
        if list1.count() > 0:
            list1.setCurrentRow(0)
    
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
        app.setApplicationName("Simple VoiceOver Test")
        app.setApplicationDisplayName("Simple VoiceOver Test")
        
        # Basic accessibility
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTabletEvents, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_MacDontSwapCtrlAndMeta, True)
        except:
            pass
        
        # Larger font
        font = QFont()
        font.setPointSize(14)
        app.setFont(font)
    
    window = SimpleVoiceOverTest()
    window.show()
    window.activateWindow()
    window.raise_()
    
    print("=== Simple VoiceOver Test ===")
    print("Test each approach with VoiceOver:")
    print("1. Standard QListWidget")
    print("2. QComboBox (dropdown)")
    print("3. Enhanced QListWidget")
    print("")
    print("VoiceOver commands:")
    print("- VO + Arrow keys to navigate")
    print("- Tab to move between sections")
    print("- Up/Down arrows in lists")
    print("===============================")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
