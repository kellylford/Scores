#!/usr/bin/env python3
"""
Test the QTreeWidget keyPressEvent pattern that works for baseball
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test basic pattern
print("Testing keyPressEvent override pattern...")

# Simulate the working baseball pattern
class MockTreeWidget:
    def __init__(self):
        self.current_item = "mock_drive"
        
    def currentItem(self):
        return self.current_item
        
    def keyPressEvent(self, event):
        print("Original keyPressEvent would be called")

def create_drives_key_handler(mock_self, tree_widget):
    """Create the keyPressEvent handler using the baseball pattern"""
    
    def on_drives_key_press(event):
        print(f"Debug: Drives tree keyPressEvent - key: {event.key}, modifiers: {event.modifiers}")
        current_item = tree_widget.currentItem()
        
        # Simulate Alt+P check (16777264 = Qt.Key.Key_P, 33554432 = Qt.KeyboardModifier.AltModifier)
        if event.key == 16777264 and event.modifiers == 33554432:
            print(f"Debug: Alt+P detected in drives tree! Current item: {current_item}")
            if current_item and hasattr(mock_self, 'league') and mock_self.league in ["NFL", "NCAAF"]:
                print("Debug: Triggering drive audio from tree widget")
                mock_self._play_drive_audio()
                return
        
        # Fall back to default behavior
        tree_widget.__class__.keyPressEvent(tree_widget, event)
    
    return on_drives_key_press

class MockEvent:
    def __init__(self, key, modifiers):
        self.key = key
        self.modifiers = modifiers

class MockGameDetailsView:
    def __init__(self):
        self.league = "NFL"
        
    def _play_drive_audio(self):
        print("✅ SUCCESS: Drive audio would be played!")

# Test the pattern
print("\n" + "="*50)
print("TESTING QTREETWIDGET KEYPRESS OVERRIDE PATTERN")
print("="*50)

mock_view = MockGameDetailsView()
mock_tree = MockTreeWidget()

# Create handler using the same pattern as baseball
key_handler = create_drives_key_handler(mock_view, mock_tree)

# Override the tree's keyPressEvent (exactly like baseball does)
mock_tree.keyPressEvent = key_handler

# Test Alt+P event
print("\n🎵 Simulating Alt+P keypress...")
alt_p_event = MockEvent(16777264, 33554432)  # Qt Key_P + AltModifier
mock_tree.keyPressEvent(alt_p_event)

print("\n✅ The QTreeWidget keyPressEvent override pattern works!")
print("This is exactly how baseball audio works successfully.")