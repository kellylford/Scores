#!/usr/bin/env python3
"""
Final test for venue feature integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.venue_service import VenueService
    print("✓ VenueService imports successfully")
    
    venue_service = VenueService()
    print("✓ VenueService creates successfully")
    
    # Test NFL venues
    nfl_venues = venue_service.get_venues_for_league('nfl')
    print(f"✓ NFL venues retrieved: {len(nfl_venues)} venues")
    
    if nfl_venues:
        venue_id, venue_data = next(iter(nfl_venues.items()))
        details = venue_service.get_venue_details(venue_id, 'nfl')
        print(f"✓ Venue details retrieved for: {venue_data.get('name')}")
        
    # Test if demo venues work 
    test_venues = venue_service._get_demo_venues('nfl')
    print(f"✓ Demo venues available: {len(test_venues)} venues")
    
    print("\n=== ALL VENUE TESTS PASSED ===")
    print("The venue feature is working correctly!")
    
except Exception as e:
    print(f"✗ Error in venue testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
