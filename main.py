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

def create_argument_parser():
    """Create and configure the command line argument parser"""
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
  scores --mlb-teams       Launch directly to MLB teams view
  scores --nfl-standings   Launch directly to NFL standings view
        """)
    
    # Create mutually exclusive group for sports
    sports_group = parser.add_mutually_exclusive_group()
    
    # Live Scores view (all sports)
    sports_group.add_argument('--live-scores', action='store_true', help='Launch directly to Live Scores view (all sports)')
    sports_group.add_argument('--live', action='store_true', help='Launch directly to Live Scores view (shorthand for --live-scores)')
    
    # Sports game views
    sports_group.add_argument('--mlb', action='store_true', help='Launch to MLB games view')
    sports_group.add_argument('--nfl', action='store_true', help='Launch to NFL games view') 
    sports_group.add_argument('--nba', action='store_true', help='Launch to NBA games view')
    sports_group.add_argument('--nhl', action='store_true', help='Launch to NHL games view')
    sports_group.add_argument('--ncaaf', action='store_true', help='Launch to NCAA Football games view')
    sports_group.add_argument('--ncaam', action='store_true', help='Launch to NCAA Men\'s Basketball games view')
    sports_group.add_argument('--ncaawb', action='store_true', help='Launch to NCAA Women\'s Basketball games view')
    
    # Teams views
    sports_group.add_argument('--mlb-teams', action='store_true', help='Launch to MLB teams view')
    sports_group.add_argument('--nfl-teams', action='store_true', help='Launch to NFL teams view')
    sports_group.add_argument('--nba-teams', action='store_true', help='Launch to NBA teams view')
    sports_group.add_argument('--nhl-teams', action='store_true', help='Launch to NHL teams view')
    sports_group.add_argument('--ncaaf-teams', action='store_true', help='Launch to NCAA Football teams view')
    sports_group.add_argument('--ncaam-teams', action='store_true', help='Launch to NCAA Men\'s Basketball teams view')
    sports_group.add_argument('--ncaawb-teams', action='store_true', help='Launch to NCAA Women\'s Basketball teams view')
    
    # Standings views
    sports_group.add_argument('--mlb-standings', action='store_true', help='Launch to MLB standings view')
    sports_group.add_argument('--nfl-standings', action='store_true', help='Launch to NFL standings view')
    sports_group.add_argument('--nba-standings', action='store_true', help='Launch to NBA standings view')
    sports_group.add_argument('--nhl-standings', action='store_true', help='Launch to NHL standings view')
    sports_group.add_argument('--ncaaf-standings', action='store_true', help='Launch to NCAA Football standings view')
    sports_group.add_argument('--ncaam-standings', action='store_true', help='Launch to NCAA Men\'s Basketball standings view')
    sports_group.add_argument('--ncaawb-standings', action='store_true', help='Launch to NCAA Women\'s Basketball standings view')
    
    return parser

def determine_startup_params(args):
    """Determine startup parameters based on command line arguments"""
    # Check for live scores view (both --live-scores and --live)
    if getattr(args, 'live_scores', False) or getattr(args, 'live', False):
        return {'action': 'live_scores'}
    
    # Check for league game views
    for sport in ['mlb', 'nfl', 'nba', 'nhl', 'ncaaf', 'ncaam', 'ncaawb']:
        if getattr(args, sport, False):
            return {'action': 'league', 'league': sport.upper()}
    
    # Check for teams views
    for sport in ['mlb', 'nfl', 'nba', 'nhl', 'ncaaf', 'ncaam', 'ncaawb']:
        if getattr(args, f'{sport}_teams', False):
            return {'action': 'teams', 'league': sport.upper()}
    
    # Check for standings views  
    for sport in ['mlb', 'nfl', 'nba', 'nhl', 'ncaaf', 'ncaam', 'ncaawb']:
        if getattr(args, f'{sport}_standings', False):
            return {'action': 'standings', 'league': sport.upper()}
    
    # Default: no special startup action
    return None

def main():
    """Main entry point for the application"""
    # Handle --help and all options before launching the app
    parser = create_argument_parser()
    
    # If --help or -h is present, print help and exit before launching the app
    if '--help' in sys.argv or '-h' in sys.argv:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    startup_params = determine_startup_params(args)

    # Import and run the main application
    from PyQt6.QtWidgets import QApplication
    from scores import SportsScoresApp

    app = QApplication(sys.argv)
    window = SportsScoresApp(startup_params=startup_params)
    sys.exit(app.exec())

# Import and run the main application
if __name__ == "__main__":
    main()
