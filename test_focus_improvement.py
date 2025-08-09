#!/usr/bin/env python3
"""
Test script to verify that date navigation properly sets focus to the first item
"""

import sys
sys.path.append('.')

from PyQt6.QtWidgets import QApplication, QListWidget
from PyQt6.QtCore import QTimer
from scores import BaseView

def test_focus_and_select_first():
    """Test the new focus and select first method"""
    app = QApplication(sys.argv)
    
    # Create a BaseView instance to test the method
    base_view = BaseView()
    
    # Create a test list widget
    test_list = QListWidget()
    test_list.addItem("Item 1")
    test_list.addItem("Item 2") 
    test_list.addItem("Item 3")
    
    # Initially no item should be selected
    print(f"Initial current row: {test_list.currentRow()}")
    assert test_list.currentRow() == -1, "Initially no item should be selected"
    
    # Test the new method
    base_view.set_focus_and_select_first(test_list)
    
    # Use QTimer to check after the delay
    def check_selection():
        print(f"After set_focus_and_select_first: {test_list.currentRow()}")
        assert test_list.currentRow() == 0, "First item should be selected"
        print("✅ Test passed: First item is selected after focus")
        app.quit()
    
    QTimer.singleShot(100, check_selection)  # Check after 100ms
    
    app.exec()

if __name__ == "__main__":
    test_focus_and_select_first()
    print("All tests passed!")
