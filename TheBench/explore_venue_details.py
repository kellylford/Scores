#!/usr/bin/env python3
"""
Enhanced ESPN API Venue Explorer
Look deeper into game details for venue information
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

def explore_game_venue_details():
    """Look at detailed game data to see venue information"""
    
    # Get NFL games
    url = f"{BASE_URL}/football/nfl/scoreboard"
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            events = data.get('events', [])
            
            if events:
                event = events[0]  # Take first game
                event_id = event.get('id')
                print(f"Examining NFL game ID: {event_id}")
                
                # Get detailed game information
                detail_url = f"{BASE_URL}/football/nfl/summary?event={event_id}"
                detail_resp = requests.get(detail_url)
                
                if detail_resp.status_code == 200:
                    detail_data = detail_resp.json()
                    
                    # Look for venue in different places
                    print("\n=== Venue in event details ===")
                    if 'gameInfo' in detail_data:
                        game_info = detail_data['gameInfo']
                        if 'venue' in game_info:
                            venue = game_info['venue']
                            print("Venue data from gameInfo:")
                            print(json.dumps(venue, indent=2))
                    
                    # Check header for venue
                    if 'header' in detail_data:
                        header = detail_data['header']
                        if 'venue' in header:
                            venue = header['venue']
                            print("\nVenue data from header:")
                            print(json.dumps(venue, indent=2))
                    
                    # Look in competitions
                    if 'header' in detail_data and 'competitions' in detail_data['header']:
                        comps = detail_data['header']['competitions']
                        if comps and 'venue' in comps[0]:
                            venue = comps[0]['venue']
                            print("\nVenue data from competition:")
                            print(json.dumps(venue, indent=2))
                    
                    # Print all top-level keys to see structure
                    print(f"\nTop-level keys in game details: {list(detail_data.keys())}")
                    
                else:
                    print(f"Failed to get game details: {detail_resp.status_code}")
                    
    except Exception as e:
        print(f"Error: {e}")

def try_venue_endpoints():
    """Try different venue-specific endpoints"""
    
    # Known venue IDs from our exploration
    venue_ids = ["3628", "47", "3504"]  # Bank of America, PNC Park, Aviva Stadium
    
    for venue_id in venue_ids:
        print(f"\n=== Trying venue ID: {venue_id} ===")
        
        # Try various endpoint patterns
        endpoints = [
            f"https://site.api.espn.com/apis/site/v2/venues/{venue_id}",
            f"https://sports.core.api.espn.com/v2/venues/{venue_id}?lang=en&region=us",
            f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/venues/{venue_id}",
            f"https://site.api.espn.com/apis/v2/venues/{venue_id}"
        ]
        
        for endpoint in endpoints:
            try:
                resp = requests.get(endpoint)
                print(f"  {endpoint} -> {resp.status_code}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"  SUCCESS! Keys: {list(data.keys())}")
                    print(json.dumps(data, indent=2))
                    return  # Stop after first success
                    
            except Exception as e:
                print(f"  Error: {e}")

def explore_mlb_venue_data():
    """MLB often has rich venue data, let's check"""
    
    print("\n=== MLB Venue Data Deep Dive ===")
    
    # Get recent MLB games
    today = datetime.now()
    start_date = today - timedelta(days=30)  # Look back further
    end_date = today + timedelta(days=7)
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    url = f"{BASE_URL}/baseball/mlb/scoreboard?dates={start_str}-{end_str}"
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            events = data.get('events', [])
            
            if events:
                # Look at first game
                event = events[0]
                event_id = event.get('id')
                print(f"Examining MLB game ID: {event_id}")
                
                # Basic venue from scoreboard
                comp = event.get('competitions', [{}])[0]
                venue = comp.get('venue', {})
                print(f"\nBasic venue: {venue}")
                
                # Get detailed game info
                detail_url = f"{BASE_URL}/baseball/mlb/summary?event={event_id}"
                detail_resp = requests.get(detail_url)
                
                if detail_resp.status_code == 200:
                    detail_data = detail_resp.json()
                    
                    # Check all possible venue locations
                    if 'gameInfo' in detail_data and 'venue' in detail_data['gameInfo']:
                        venue_detail = detail_data['gameInfo']['venue']
                        print("\nDetailed venue from gameInfo:")
                        print(json.dumps(venue_detail, indent=2))
                        
                        # Try to get even more details with venue ID
                        venue_id = venue_detail.get('id')
                        if venue_id:
                            print(f"\nTrying MLB venue endpoint for ID {venue_id}...")
                            venue_url = f"{BASE_URL}/baseball/mlb/venues/{venue_id}"
                            venue_resp = requests.get(venue_url)
                            print(f"Venue endpoint status: {venue_resp.status_code}")
                            
                            if venue_resp.status_code == 200:
                                venue_data = venue_resp.json()
                                print("Full venue data:")
                                print(json.dumps(venue_data, indent=2))
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore_game_venue_details()
    try_venue_endpoints()
    explore_mlb_venue_data()
