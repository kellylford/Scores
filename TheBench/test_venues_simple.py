#!/usr/bin/env python3
"""
Simple test for venue feature - just basic functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.venue_service import VenueService

def test_basic_venue_functionality():
    """Test basic venue functionality without excessive API calls"""
    print("=== Testing Basic Venue Feature ===\n")
    
    venue_service = VenueService()
    
    # Test just NFL venues (one league)
    print("Testing NFL venues...")
    try:
        venues = venue_service.get_venues_for_league('nfl')
        print(f"Found {len(venues)} NFL venues")
        
        if venues:
            # Show first 3 venues
            venue_list = list(venues.items())[:3]
            for venue_id, venue_data in venue_list:
                print(f"  {venue_data.get('name', 'Unknown')} - {venue_data.get('city', 'Unknown')}")
                
        print("✓ NFL venue retrieval working")
        
    except Exception as e:
        print(f"✗ Error getting NFL venues: {e}")
        return False
    
    # Test venue details for one venue
    if venues:
        venue_id, venue_data = next(iter(venues.items()))
        print(f"\nTesting venue details for: {venue_data.get('name')}")
        
        try:
            details = venue_service.get_venue_details(venue_id, 'nfl')
            print(f"  Capacity: {details.get('capacity', 'Unknown')}")
            print(f"  Surface: {'Grass' if details.get('grass') else 'Artificial' if details.get('grass') is not None else 'Unknown'}")
            print("✓ Venue details working")
            
        except Exception as e:
            print(f"✗ Error getting venue details: {e}")
            return False
    
    print("\n=== Basic Venue Test Complete ===")
    return True

if __name__ == "__main__":
    success = test_basic_venue_functionality()
    if success:
        print("All basic tests passed!")
    else:
        print("Some tests failed.")
        sys.exit(1)
