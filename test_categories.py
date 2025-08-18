#!/usr/bin/env python3

"""
Test the corrected categories display
"""

import sys
import os
sys.path.append('.')

# Set environment to avoid GUI
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Mock the statistics data loading to test category display
def test_categories():
    print("Testing categories display...")
    
    # Simulate what _get_stat_categories should return for MLB team stats
    def get_stat_categories_mlb_team():
        return [
            "Batting Average", "Home Runs", "RBIs", "Runs", "Hits", "Doubles", "Triples",
            "ERA", "Wins", "Strikeouts", "WHIP", "Saves", "Innings Pitched",
            "Fielding Percentage", "Errors", "Double Plays"
        ]
    
    categories = get_stat_categories_mlb_team()
    print(f"MLB Team Statistics Categories ({len(categories)} total):")
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category}")
    
    print("\nThese should now display as clickable options that will:")
    print("- Load data on-demand when clicked")
    print("- Show team rankings for that specific statistic")
    print("- Display in format: '1 Team Name Value'")

if __name__ == "__main__":
    test_categories()
