#!/usr/bin/env python3
"""
Simplified macOS entry point for Sports Scores Application
Focuses on core accessibility without complex imports
"""

import sys
import os
import platform

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point with basic macOS optimizations"""
    
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Basic macOS optimizations
    if platform.system() == "Darwin":
        # Set application properties
        app.setApplicationName("Sports Scores")
        app.setApplicationDisplayName("Sports Scores")
        app.setApplicationVersion("0.51.0")
        app.setOrganizationName("Kelly Ford")
        app.setOrganizationDomain("com.kellylford.scores")
        
        # Basic accessibility attributes
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTabletEvents, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTouchEvents, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_MacDontSwapCtrlAndMeta, True)
        except:
            pass  # Ignore if attributes don't exist
        
        # Larger font for better readability
        font = QFont()
        font.setPointSize(13)
        app.setFont(font)
    
    # Import and create the main window
    from scores import SportsScoresApp
    
    # Parse command line arguments (simplified)
    startup_params = None
    if len(sys.argv) > 1:
        if '--live' in sys.argv or '--live-scores' in sys.argv:
            startup_params = {'view': 'live_scores'}
        elif '--mlb' in sys.argv:
            startup_params = {'view': 'league', 'league': 'mlb'}
        elif '--nfl' in sys.argv:
            startup_params = {'view': 'league', 'league': 'nfl'}
    
    # Create main window
    window = SportsScoresApp(startup_params=startup_params)
    
    # Basic macOS window setup
    if platform.system() == "Darwin":
        window.setAccessibleName("Sports Scores Application")
        window.setAccessibleDescription("Sports analysis application with live scores and statistics")
        window.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Ensure window can be resized and has proper controls
        window.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
    
    # Show and run
    window.show()
    window.activateWindow()
    window.raise_()
    window.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
