#!/usr/bin/env python3
"""
Check which leagues have venue data available
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.venue_service import VenueService

def check_league_venues():
    """Check which leagues have venues available"""
    print("=== Checking League Venue Availability ===\n")
    
    venue_service = VenueService()
    
    leagues = ['nfl', 'mlb', 'nba', 'nhl', 'mens-college-basketball', 'college-football']
    
    for league in leagues:
        print(f"Checking {league.upper()}...")
        try:
            venues = venue_service.get_venues_for_league(league)
            print(f"  Found {len(venues)} venues")
            
            if venues:
                # Show first venue as example
                venue_id, venue_data = next(iter(venues.items()))
                print(f"  Example: {venue_data.get('name', 'Unknown')} in {venue_data.get('city', 'Unknown')}")
            else:
                print("  No venues found (likely no active games)")
                
        except Exception as e:
            print(f"  Error: {e}")
        
        print()
    
    print("=== Check Complete ===")

if __name__ == "__main__":
    check_league_venues()

