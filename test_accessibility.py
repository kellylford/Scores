"""
Test script to verify accessibility improvements are working
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from accessible_table import BoxscoreTable

def test_accessibility():
    app = QApplication(sys.argv)
    
    # Create a test table
    table = BoxscoreTable(title="Test Player Stats")
    table.setup_columns(["Player", "Pos", "AB", "H", "RBI"])
    
    # Add test data
    test_data = [
        ["TJ Friedl", "CF", "4", "1", "0"],
        ["Jonathan India", "2B", "3", "2", "1"],
        ["Tyler Stephenson", "C", "4", "0", "0"]
    ]
    
    table.populate_data(test_data, set_focus=True)
    
    # Test accessibility of a specific cell
    item = table.item(0, 2)  # TJ Friedl's AB
    if item:
        desc = item.data(0x00000100)  # AccessibleDescriptionRole
        tooltip = item.toolTip()
        print(f"Cell accessibility description: '{desc}'")
        print(f"Cell tooltip: '{tooltip}'")
        print(f"Cell text: '{item.text()}'")
    else:
        print("Could not get item")
    
    # Test navigation update
    table.setCurrentCell(1, 3)  # Jonathan India's H
    item = table.item(1, 3)
    if item:
        desc = item.data(0x00000100)
        tooltip = item.toolTip()
        print(f"After navigation - accessibility description: '{desc}'")
        print(f"After navigation - tooltip: '{tooltip}'")
    
    print("Accessibility test completed")

if __name__ == "__main__":
    test_accessibility()
