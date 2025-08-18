#!/usr/bin/env python3
"""
macOS-specific main entry point for Sports Scores Application
Includes macOS accessibility optimizations and VoiceOver support
"""

import sys
import os
import platform

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont

def setup_macos_accessibility(app):
    """Configure macOS-specific accessibility features"""
    if platform.system() != "Darwin":
        return
    
    # Set application properties for macOS
    app.setApplicationName("Sports Scores")
    app.setApplicationDisplayName("Sports Scores")
    app.setApplicationVersion("0.51.0")
    app.setOrganizationName("Kelly Ford")
    app.setOrganizationDomain("com.kellylford.scores")
    
    # Enable VoiceOver support and tablet events
    app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTabletEvents, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTouchEvents, True)
    
    # Don't swap Ctrl and Meta keys for macOS
    app.setAttribute(Qt.ApplicationAttribute.AA_MacDontSwapCtrlAndMeta, True)
    
    # Configure fonts for better readability
    font = QFont()
    font.setPointSize(13)  # Slightly larger for macOS
    app.setFont(font)
    
    # Set up accessibility manager
    from macos_accessibility import MacOSAccessibilityManager
    accessibility_manager = MacOSAccessibilityManager(app)
    
    return accessibility_manager

def setup_macos_window_properties(window, accessibility_manager=None):
    """Configure macOS-specific window properties"""
    if platform.system() != "Darwin":
        return
    
    # Enable native macOS window features
    window.setWindowFlags(
        Qt.WindowType.Window |
        Qt.WindowType.WindowTitleHint |
        Qt.WindowType.WindowSystemMenuHint |
        Qt.WindowType.WindowMinimizeButtonHint |
        Qt.WindowType.WindowMaximizeButtonHint |
        Qt.WindowType.WindowCloseButtonHint |
        Qt.WindowType.WindowFullscreenButtonHint
    )
    
    # Set accessibility properties
    window.setAccessibleName("Sports Scores Application")
    window.setAccessibleDescription("Sports analysis application with live scores and statistics")
    
    # Enable tab navigation
    window.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    # Set window role for accessibility
    window.setWindowRole("MainWindow")
    
    # Apply accessibility enhancements
    if accessibility_manager:
        from macos_accessibility import setup_macos_widget_accessibility
        setup_macos_widget_accessibility(window, accessibility_manager)

def parse_startup_params():
    """Parse command line arguments for macOS"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sports Scores Application - View live scores, standings, and team information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scores                    Launch home screen
  scores --live             Launch directly to Live Scores view (shorthand)
  scores --live-scores      Launch directly to Live Scores view (all sports)
  scores --mlb             Launch directly to MLB games
  scores --nfl             Launch directly to NFL games  
        """
    )
    
    sports_group = parser.add_mutually_exclusive_group()
    sports_group.add_argument('--live-scores', action='store_true', help='Launch directly to Live Scores view (all sports)')
    sports_group.add_argument('--live', action='store_true', help='Launch directly to Live Scores view (shorthand for --live-scores)')
    sports_group.add_argument('--mlb', action='store_true', help='Launch to MLB games view')
    sports_group.add_argument('--nfl', action='store_true', help='Launch to NFL games view') 
    sports_group.add_argument('--nba', action='store_true', help='Launch to NBA games view')
    sports_group.add_argument('--nhl', action='store_true', help='Launch to NHL games view')
    sports_group.add_argument('--ncaaf', action='store_true', help='Launch to NCAA Football games view')
    sports_group.add_argument('--mlb-teams', action='store_true', help='Launch to MLB teams view')
    sports_group.add_argument('--nfl-teams', action='store_true', help='Launch to NFL teams view')
    sports_group.add_argument('--nba-teams', action='store_true', help='Launch to NBA teams view')
    sports_group.add_argument('--nhl-teams', action='store_true', help='Launch to NHL teams view')
    sports_group.add_argument('--ncaaf-teams', action='store_true', help='Launch to NCAA Football teams view')
    sports_group.add_argument('--mlb-standings', action='store_true', help='Launch to MLB standings view')
    sports_group.add_argument('--nfl-standings', action='store_true', help='Launch to NFL standings view')
    sports_group.add_argument('--nba-standings', action='store_true', help='Launch to NBA standings view')
    sports_group.add_argument('--nhl-standings', action='store_true', help='Launch to NHL standings view')
    sports_group.add_argument('--ncaaf-standings', action='store_true', help='Launch to NCAA Football standings view')

    # If --help or -h is present, print help and exit before launching the app
    if '--help' in sys.argv or '-h' in sys.argv:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    
    # Determine startup parameters
    startup_params = {}
    
    if args.live_scores or args.live:
        startup_params['view'] = 'live_scores'
    elif args.mlb:
        startup_params['view'] = 'league'
        startup_params['league'] = 'mlb'
    elif args.nfl:
        startup_params['view'] = 'league'
        startup_params['league'] = 'nfl'
    elif args.nba:
        startup_params['view'] = 'league'
        startup_params['league'] = 'nba'
    elif args.nhl:
        startup_params['view'] = 'league'
        startup_params['league'] = 'nhl'
    elif args.ncaaf:
        startup_params['view'] = 'league'
        startup_params['league'] = 'ncaaf'
    # Add teams and standings views
    elif args.mlb_teams:
        startup_params['view'] = 'teams'
        startup_params['league'] = 'mlb'
    elif args.nfl_teams:
        startup_params['view'] = 'teams'
        startup_params['league'] = 'nfl'
    elif args.mlb_standings:
        startup_params['view'] = 'standings'
        startup_params['league'] = 'mlb'
    elif args.nfl_standings:
        startup_params['view'] = 'standings'
        startup_params['league'] = 'nfl'
    # Add other leagues as needed
    else:
        startup_params = None
    
    return startup_params

def main():
    """Main entry point with macOS optimizations"""
    
    # Parse command line arguments
    startup_params = parse_startup_params()
    
    # Create QApplication with macOS-specific settings
    app = QApplication(sys.argv)
    
    # Configure macOS accessibility
    accessibility_manager = setup_macos_accessibility(app)
    
    # Import and create the main window
    from scores import SportsScoresApp
    
    # Create main window
    window = SportsScoresApp(startup_params=startup_params)
    
    # Apply macOS-specific window properties
    setup_macos_window_properties(window, accessibility_manager)
    
    # Show window and run app
    window.show()
    window.activateWindow()
    window.raise_()
    
    # Set initial focus
    window.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
