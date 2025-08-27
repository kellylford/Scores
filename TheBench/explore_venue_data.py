#!/usr/bin/env python3
"""
ESPN API Venue Explorer
Test script to see what venue/stadium data is available from ESPN API
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

LEAGUES = {
    "NFL": "football/nfl",
    "NBA": "basketball/nba", 
    "MLB": "baseball/mlb",
    "NHL": "hockey/nhl",
    "NCAAF": "football/college-football",
    "NCAAM": "basketball/mens-college-basketball"
}

def explore_venue_data():
    """Explore what venue data is available across different sports"""
    
    print("=== ESPN API Venue Data Explorer ===\n")
    
    for league_name, league_path in LEAGUES.items():
        print(f"\n--- {league_name} Venue Data ---")
        
        # Get recent games to examine venue data
        today = datetime.now()
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=7)
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        url = f"{BASE_URL}/{league_path}/scoreboard?dates={start_str}-{end_str}"
        
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                events = data.get('events', [])
                
                if events:
                    # Look at first few events for venue data
                    for i, event in enumerate(events[:3]):
                        competitions = event.get('competitions', [])
                        if competitions:
                            comp = competitions[0]
                            venue = comp.get('venue', {})
                            
                            print(f"\nGame {i+1}:")
                            print(f"  Full Name: {venue.get('fullName', 'N/A')}")
                            print(f"  Short Name: {venue.get('shortName', 'N/A')}")
                            print(f"  ID: {venue.get('id', 'N/A')}")
                            
                            # Address info
                            address = venue.get('address', {})
                            if address:
                                print(f"  City: {address.get('city', 'N/A')}")
                                print(f"  State: {address.get('state', 'N/A')}")
                                
                            # Capacity
                            print(f"  Capacity: {venue.get('capacity', 'N/A')}")
                            
                            # Indoor/Outdoor
                            print(f"  Indoor: {venue.get('indoor', 'N/A')}")
                            
                            # Grass type
                            print(f"  Grass: {venue.get('grass', 'N/A')}")
                            
                            # Images
                            images = venue.get('images', [])
                            if images:
                                print(f"  Images available: {len(images)}")
                                
                            # All available keys
                            print(f"  Available keys: {list(venue.keys())}")
                            
                            break
                else:
                    print("  No games found in date range")
            else:
                print(f"  API Error: {resp.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")

def explore_specific_venue(venue_id):
    """Try to get detailed venue information for a specific venue"""
    print(f"\n=== Exploring Venue ID: {venue_id} ===")
    
    # Try different venue endpoint patterns
    endpoints = [
        f"https://site.api.espn.com/apis/site/v2/venues/{venue_id}",
        f"https://sports.core.api.espn.com/v2/venues/{venue_id}",
        f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/venues/{venue_id}"
    ]
    
    for endpoint in endpoints:
        try:
            resp = requests.get(endpoint)
            print(f"\nTrying: {endpoint}")
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print("Available data:")
                print(json.dumps(data, indent=2))
                return data
                
        except Exception as e:
            print(f"Error: {e}")
    
    return None

def get_teams_and_venues(league_name):
    """Get teams for a league and their home venues"""
    print(f"\n=== {league_name} Teams and Venues ===")
    
    league_path = LEAGUES.get(league_name)
    if not league_path:
        print("League not found")
        return
        
    url = f"{BASE_URL}/{league_path}/teams"
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            
            print(f"Found {len(teams)} teams:")
            
            for team in teams[:5]:  # Show first 5 teams
                team_data = team.get('team', {})
                venue = team_data.get('venue', {})
                
                print(f"\n{team_data.get('displayName', 'Unknown')}:")
                print(f"  Venue: {venue.get('fullName', 'N/A')}")
                print(f"  Venue ID: {venue.get('id', 'N/A')}")
                print(f"  City: {venue.get('address', {}).get('city', 'N/A')}")
                print(f"  Capacity: {venue.get('capacity', 'N/A')}")
                print(f"  Indoor: {venue.get('indoor', 'N/A')}")
                
                # If we have a venue ID, try to get more details
                venue_id = venue.get('id')
                if venue_id:
                    print(f"  Available venue data keys: {list(venue.keys())}")
                
        else:
            print(f"API Error: {resp.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Explore venue data in game results
    explore_venue_data()
    
    # Try to get team venue data
    get_teams_and_venues("NFL")
    
    # Try to explore a specific venue (Lambeau Field ID from NFL)
    explore_specific_venue("3")  # Lambeau Field example
