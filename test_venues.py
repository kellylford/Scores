#!/usr/bin/env python3
"""
Test script for the new venue feature
"""

import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.venue_service import venue_service

def test_venue_feature():
    """Test the venue feature functionality"""
    
    print("=== Testing Venue Feature ===\n")
    
    # Test leagues
    test_leagues = ["NFL", "MLB", "NBA"]
    
    for league in test_leagues:
        print(f"Testing {league} venues...")
        
        try:
            venues = venue_service.get_venues_for_league(league)
            print(f"  Found {len(venues)} venues")
            
            if venues:
                # Show first few venues
                sample_venues = list(venues.values())[:3]
                for venue in sample_venues:
                    name = venue.get('name', 'Unknown')
                    city = venue.get('city', 'Unknown')
                    indoor = "Indoor" if venue.get('indoor') else "Outdoor"
                    grass = "Grass" if venue.get('grass') else "Turf" if venue.get('grass') is False else "Unknown"
                    
                    print(f"    • {name} ({city}) - {indoor}, {grass}")
                
                # Test venue details for first venue
                first_venue_id = sample_venues[0].get('id')
                if first_venue_id:
                    details = venue_service.get_venue_details(first_venue_id, league)
                    if details:
                        facts = details.get('interesting_facts', [])
                        print(f"    Details available: {len(facts)} interesting facts")
                    else:
                        print(f"    No details available for venue ID: {first_venue_id}")
            else:
                print(f"  No venues found for {league}")
                
        except Exception as e:
            print(f"  Error: {e}")
        
        print()
    
    print("=== Venue Feature Test Complete ===")

if __name__ == "__main__":
    test_venue_feature()
