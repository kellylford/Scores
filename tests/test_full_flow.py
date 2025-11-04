"""
Test the full flow of opening the Football Audio Tutorial
This simulates what happens when you press Enter on the menu item
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

try:
    from scores import SportsScoresApp
    
    print("Creating app...")
    qt_app = QApplication(sys.argv)
    app = SportsScoresApp()
    
    print("Opening audio tutorial...")
    app.open_audio_tutorial()
    
    # Check current view
    print(f"Current view index: {app.stack.currentIndex()}")
    current_widget = app.stack.currentWidget()
    print(f"Current widget: {type(current_widget).__name__}")
    
    # Try to get the tutorial list
    if hasattr(current_widget, 'tutorial_list'):
        print(f"✓ Tutorial list found with {current_widget.tutorial_list.count()} items")
        
        # Simulate selecting football tutorial
        print("\nSimulating selection of Football Audio Tutorial...")
        for i in range(current_widget.tutorial_list.count()):
            item = current_widget.tutorial_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == "football":
                print(f"Found football item at index {i}")
                # Simulate activation
                current_widget._on_tutorial_selected(item)
                break
        
        # Check if view changed
        print(f"\nAfter selection:")
        print(f"Current view index: {app.stack.currentIndex()}")
        new_widget = app.stack.currentWidget()
        print(f"Current widget: {type(new_widget).__name__}")
        
        if hasattr(new_widget, 'drives_list'):
            print(f"✓ Football tutorial loaded! Drives list has {new_widget.drives_list.count()} items")
        else:
            print("✗ Football tutorial did not load properly")
    else:
        print("✗ Tutorial list not found")
    
    print("\n✅ Test complete!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
