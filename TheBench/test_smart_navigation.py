#!/usr/bin/env python3
"""
Simple test to verify the smart navigation enhancement works
"""

import sys
import os

# Add the TheBench directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Test that the enhanced accessible_table_explorer can be imported"""
    try:
        from accessible_table_explorer import AccessibleTableExplorer, SmartNavigationTable
        print("✓ Successfully imported enhanced accessible_table_explorer")
        print("✓ SmartNavigationTable class is available")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_functionality():
    """Test basic functionality without starting the GUI"""
    try:
        from accessible_table_explorer import SmartNavigationTable, AccessibilityTestResults, AccessibilityControlPanel
        from PyQt6.QtWidgets import QApplication
        
        # Create minimal Qt application
        app = QApplication([])
        
        # Test SmartNavigationTable creation
        table = SmartNavigationTable()
        print("✓ SmartNavigationTable created successfully")
        
        # Test control panel with new mode
        results = AccessibilityTestResults()
        control_panel = AccessibilityControlPanel(results)
        
        # Check that the new navigation mode is available
        nav_modes = [control_panel.nav_mode.itemText(i) for i in range(control_panel.nav_mode.count())]
        smart_mode = "Smart Navigation (Column header on row move, Row header on column move)"
        
        if smart_mode in nav_modes:
            print("✓ Smart Navigation mode is available in control panel")
        else:
            print("✗ Smart Navigation mode not found in control panel")
            print(f"Available modes: {nav_modes}")
            return False
            
        print("✓ All functionality tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Smart Navigation Enhancement")
    print("=" * 40)
    
    success = True
    
    # Test imports
    if not test_import():
        success = False
    
    # Test functionality
    if not test_functionality():
        success = False
    
    print("=" * 40)
    if success:
        print("✓ All tests passed! Smart Navigation enhancement is working.")
        print("\nTo test the full application, run:")
        print("python accessible_table_explorer.py")
    else:
        print("✗ Some tests failed. Check the errors above.")
    
    sys.exit(0 if success else 1)
