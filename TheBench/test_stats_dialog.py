#!/usr/bin/env python3
"""
Minimal test for Statistics Dialog functionality
"""

import sys
import os
sys.path.append('.')

from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
from scores import StatisticsChoiceDialog, StatisticsViewDialog

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Statistics Dialog Test")
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        
        test_btn = QPushButton("Test Statistics Flow")
        test_btn.clicked.connect(self.test_statistics)
        layout.addWidget(test_btn)
        
        self.setLayout(layout)
    
    def test_statistics(self):
        print("🧪 Testing Statistics Flow...")
        
        # Step 1: Choice dialog
        choice_dialog = StatisticsChoiceDialog("mlb", self)
        print("✅ Choice dialog created")
        
        if choice_dialog.exec() == choice_dialog.DialogCode.Accepted:
            choice = choice_dialog.get_choice()
            print(f"✅ User chose: {choice}")
            
            if choice:
                # Step 2: View dialog
                print("🔍 Creating view dialog...")
                stats_dialog = StatisticsViewDialog("mlb", choice, self)
                print("✅ View dialog created, executing...")
                stats_dialog.exec()
                print("✅ View dialog completed")
        else:
            print("❌ Choice dialog was cancelled")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())
