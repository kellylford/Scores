#!/usr/bin/env python3
"""
Sports Scores Application - Main Entry Point
A comprehensive sports analysis application supporting MLB and NFL
"""

import sys
import os
import argparse

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def parse_command_line():
    """Parse command line arguments for direct navigation to sports sections"""
    parser = argparse.ArgumentParser(
        description="Sports Scores Application - View live scores, standings, and team information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scores                    Launch home screen
  scores --mlb             Launch directly to MLB games
  scores --nfl             Launch directly to NFL games  
  scores --mlb-teams       Launch directly to MLB teams view
  scores --nfl-standings   Launch directly to NFL standings view
        """)
    
    # Create mutually exclusive group for sports
    sports_group = parser.add_mutually_exclusive_group()
    
    # Sports game views
    sports_group.add_argument('--mlb', action='store_true', help='Launch to MLB games view')
    sports_group.add_argument('--nfl', action='store_true', help='Launch to NFL games view') 
    sports_group.add_argument('--nba', action='store_true', help='Launch to NBA games view')
    sports_group.add_argument('--nhl', action='store_true', help='Launch to NHL games view')
    sports_group.add_argument('--ncaaf', action='store_true', help='Launch to NCAA Football games view')
    
    # Teams views
    sports_group.add_argument('--mlb-teams', action='store_true', help='Launch to MLB teams view')
    sports_group.add_argument('--nfl-teams', action='store_true', help='Launch to NFL teams view')
    sports_group.add_argument('--nba-teams', action='store_true', help='Launch to NBA teams view')
    sports_group.add_argument('--nhl-teams', action='store_true', help='Launch to NHL teams view')
    sports_group.add_argument('--ncaaf-teams', action='store_true', help='Launch to NCAA Football teams view')
    
    # Standings views
    sports_group.add_argument('--mlb-standings', action='store_true', help='Launch to MLB standings view')
    sports_group.add_argument('--nfl-standings', action='store_true', help='Launch to NFL standings view')
    sports_group.add_argument('--nba-standings', action='store_true', help='Launch to NBA standings view')
    sports_group.add_argument('--nhl-standings', action='store_true', help='Launch to NHL standings view')
    sports_group.add_argument('--ncaaf-standings', action='store_true', help='Launch to NCAA Football standings view')
    
    return parser.parse_args()

def determine_startup_params(args):
    """Determine startup parameters based on command line arguments"""
    # Check for league game views
    for sport in ['mlb', 'nfl', 'nba', 'nhl', 'ncaaf']:
        if getattr(args, sport, False):
            return {'action': 'league', 'league': sport.upper()}
    
    # Check for teams views
    for sport in ['mlb', 'nfl', 'nba', 'nhl', 'ncaaf']:
        if getattr(args, f'{sport}_teams', False):
            return {'action': 'teams', 'league': sport.upper()}
    
    # Check for standings views  
    for sport in ['mlb', 'nfl', 'nba', 'nhl', 'ncaaf']:
        if getattr(args, f'{sport}_standings', False):
            return {'action': 'standings', 'league': sport.upper()}
    
    # Default: no special startup action
    return None

# Import and run the main application
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from scores import SportsScoresApp

    # Comprehensive fix: handle --help and all options before launching the app
    import argparse
    parser = argparse.ArgumentParser(
        description="Sports Scores Application - View live scores, standings, and team information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scores                    Launch home screen
  scores --mlb             Launch directly to MLB games
  scores --nfl             Launch directly to NFL games  
  scores --mlb-teams       Launch directly to MLB teams view
  scores --nfl-standings   Launch directly to NFL standings view
        """
    )
    sports_group = parser.add_mutually_exclusive_group()
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
    startup_params = determine_startup_params(args)

    app = QApplication(sys.argv)
    window = SportsScoresApp(startup_params=startup_params)
    sys.exit(app.exec())
