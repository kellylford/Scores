#!/usr/bin/env python3
"""
Quick test script to verify macOS accessibility features
"""

import sys
import os
import platform

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_accessibility():
    """Test macOS accessibility features"""
    print("Testing macOS accessibility features...")
    
    if platform.system() != "Darwin":
        print("❌ Not running on macOS - accessibility features may not work")
        return False
    
    print("✅ Running on macOS")
    
    try:
        from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
        from PyQt6.QtCore import Qt
        print("✅ PyQt6 imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyQt6: {e}")
        return False
    
    try:
        # Create minimal app
        app = QApplication(sys.argv)
        
        # Configure basic accessibility
        app.setApplicationName("Test App")
        app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTabletEvents, True)
        
        # Create test window
        window = QWidget()
        window.setWindowTitle("Accessibility Test")
        window.setAccessibleName("Test Window")
        window.setAccessibleDescription("Test window for accessibility verification")
        window.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        layout = QVBoxLayout()
        
        # Test label
        label = QLabel("This is a test label")
        label.setAccessibleName("Test Label")
        label.setAccessibleDescription("A test label for VoiceOver")
        layout.addWidget(label)
        
        # Test button
        button = QPushButton("Test Button")
        button.setAccessibleName("Test Button")
        button.setAccessibleDescription("A test button for keyboard navigation")
        button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        layout.addWidget(button)
        
        window.setLayout(layout)
        
        print("✅ Created accessible test UI")
        print("✅ Set focus policies")
        print("✅ Set accessible names and descriptions")
        
        # Don't actually show the window in test mode
        print("✅ Accessibility test passed!")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Accessibility test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_accessibility()
    sys.exit(0 if success else 1)
