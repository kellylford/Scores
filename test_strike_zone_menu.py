#!/usr/bin/env python3
"""
Test Strike Zone Menu Audio on Focus
====================================
Test the enhanced strike zone menu that plays audio on hover/focus
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer, Qt

# Import our updated modules
try:
    from scores import StrikeZoneMenu, AudioOnFocusAction
    from simple_audio_mapper import SimpleAudioPitchMapper
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class TestWindow(QMainWindow):
    """Test window for strike zone menu"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Strike Zone Menu Test")
        self.setGeometry(300, 300, 400, 200)
        
        # Initialize audio mapper
        self.audio_mapper = SimpleAudioPitchMapper()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add test button
        test_button = QPushButton("Right-click to test Strike Zone Menu")
        test_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        test_button.customContextMenuRequested.connect(self.show_test_menu)
        layout.addWidget(test_button)
        
        # Instructions
        instructions = """
Instructions:
1. Right-click the button above
2. Hover over "Explore Strike Zone" to open submenu
3. Move mouse over different zone positions - audio should play automatically
4. Try using arrow keys to navigate - audio should play on highlight
5. Press Enter on any item - audio should play again
        """
        
        from PyQt6.QtWidgets import QLabel
        label = QLabel(instructions)
        label.setWordWrap(True)
        layout.addWidget(label)
    
    def show_test_menu(self, position):
        """Show the test context menu"""
        from PyQt6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        # Add regular item
        regular_action = menu.addAction("Regular Menu Item")
        
        # Add separator
        menu.addSeparator()
        
        # Add strike zone submenu
        explore_menu = StrikeZoneMenu("Explore Strike Zone", self, self._play_strike_zone_audio)
        
        # Create 3x3 grid of strike zone positions
        zone_positions = [
            ("High Left", "high_left"),
            ("High Center", "high_center"), 
            ("High Right", "high_right"),
            ("Center Left", "center_left"),
            ("Center Center", "center_center"),
            ("Center Right", "center_right"),
            ("Low Left", "low_left"),
            ("Low Center", "low_center"),
            ("Low Right", "low_right")
        ]
        
        for display_name, zone_id in zone_positions:
            zone_action = AudioOnFocusAction(display_name, self, self._play_strike_zone_audio, zone_id)
            zone_action.zone_id = zone_id
            zone_action.setStatusTip(f"Play audio for {display_name.lower()} strike zone")
            zone_action.triggered.connect(lambda checked, z=zone_id: self._play_strike_zone_audio(z))
            explore_menu.addAction(zone_action)
        
        menu.addMenu(explore_menu)
        
        # Show menu
        button = self.sender()
        menu.exec(button.mapToGlobal(position))
    
    def _play_strike_zone_audio(self, zone_position):
        """Play audio for a specific strike zone position"""
        if not self.audio_mapper:
            print(f"Audio mapper not available - would play: {zone_position}")
            return
            
        try:
            # Generate audio for the strike zone position
            self.audio_mapper.generate_strike_zone_audio(zone_position, batter_hand='R')
            print(f"Playing audio for: {zone_position.replace('_', ' ').title()}")
            
        except Exception as e:
            print(f"Failed to play strike zone audio: {str(e)}")

def main():
    """Run the strike zone menu test"""
    app = QApplication(sys.argv)
    
    # Create and show test window
    window = TestWindow()
    window.show()
    
    print("Strike Zone Menu Test")
    print("=" * 30)
    print("Window opened. Right-click the button to test the menu.")
    print("Move mouse over strike zone items - they should play audio automatically!")
    
    # Run the app
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
