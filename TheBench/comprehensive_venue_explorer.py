#!/usr/bin/env python3
"""
ESPN API Team Venues Explorer
Find all teams and their home venues for each sport
"""

import requests
import json

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

LEAGUES = {
    "NFL": "football/nfl",
    "NBA": "basketball/nba", 
    "MLB": "baseball/mlb",
    "NHL": "hockey/nhl",
    "NCAAF": "football/college-football",
    "NCAAM": "basketball/mens-college-basketball"
}

def get_comprehensive_venue_list(league_name):
    """Get all venues for a sport by examining recent games"""
    
    print(f"\n=== {league_name} Comprehensive Venue List ===")
    
    league_path = LEAGUES.get(league_name)
    if not league_path:
        return {}
        
    venues = {}
    
    # Method 1: Get from recent games
    from datetime import datetime, timedelta
    today = datetime.now()
    start_date = today - timedelta(days=60)  # Look back 2 months
    end_date = today + timedelta(days=30)   # Look ahead 1 month
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    url = f"{BASE_URL}/{league_path}/scoreboard?dates={start_str}-{end_str}&limit=100"
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            events = data.get('events', [])
            
            print(f"Found {len(events)} games to examine")
            
            for event in events:
                competitions = event.get('competitions', [])
                if competitions:
                    comp = competitions[0]
                    venue = comp.get('venue', {})
                    
                    venue_id = venue.get('id')
                    if venue_id and venue_id not in venues:
                        venues[venue_id] = {
                            'id': venue_id,
                            'name': venue.get('fullName', 'Unknown'),
                            'city': venue.get('address', {}).get('city', 'Unknown'),
                            'state': venue.get('address', {}).get('state', 'Unknown'),
                            'indoor': venue.get('indoor', False)
                        }
                        
                        # Try to get additional details from a game at this venue
                        event_id = event.get('id')
                        if event_id:
                            detail_url = f"{BASE_URL}/{league_path}/summary?event={event_id}"
                            try:
                                detail_resp = requests.get(detail_url)
                                if detail_resp.status_code == 200:
                                    detail_data = detail_resp.json()
                                    if 'gameInfo' in detail_data and 'venue' in detail_data['gameInfo']:
                                        detailed_venue = detail_data['gameInfo']['venue']
                                        
                                        # Add additional details
                                        venues[venue_id].update({
                                            'grass': detailed_venue.get('grass'),
                                            'capacity': detailed_venue.get('capacity'),
                                            'zipCode': detailed_venue.get('address', {}).get('zipCode'),
                                            'images': detailed_venue.get('images', []),
                                            'guid': detailed_venue.get('guid')
                                        })
                                        
                                        print(f"  Enhanced venue: {venues[venue_id]['name']}")
                                        
                            except:
                                pass  # Skip if can't get details
    
    except Exception as e:
        print(f"Error: {e}")
    
    return venues

def try_teams_endpoint_for_venues(league_name):
    """Try teams endpoint to see if venue data is there"""
    
    print(f"\n=== {league_name} Teams Endpoint Venues ===")
    
    league_path = LEAGUES.get(league_name)
    if not league_path:
        return {}
    
    venues = {}
    
    url = f"{BASE_URL}/{league_path}/teams"
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            
            # Navigate the nested structure
            sports = data.get('sports', [])
            if sports:
                leagues = sports[0].get('leagues', [])
                if leagues:
                    teams = leagues[0].get('teams', [])
                    
                    print(f"Found {len(teams)} teams")
                    
                    for team_entry in teams:
                        team = team_entry.get('team', {})
                        venue = team.get('venue', {})
                        
                        if venue and venue.get('id'):
                            venue_id = venue.get('id')
                            venues[venue_id] = {
                                'id': venue_id,
                                'name': venue.get('fullName', venue.get('name', 'Unknown')),
                                'city': venue.get('address', {}).get('city', 'Unknown'),
                                'state': venue.get('address', {}).get('state', 'Unknown'),
                                'team': team.get('displayName', 'Unknown'),
                                'team_id': team.get('id'),
                                'indoor': venue.get('indoor'),
                                'capacity': venue.get('capacity'),
                                'grass': venue.get('grass')
                            }
                            
                            print(f"  {team.get('displayName', 'Unknown')}: {venue.get('fullName', 'Unknown')}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    return venues

def analyze_venue_features():
    """Analyze what interesting features venues have"""
    
    print("\n=== Venue Feature Analysis ===")
    
    # Collect venues from multiple sports
    all_venues = {}
    
    for league in ["NFL", "MLB", "NBA"]:
        print(f"\nCollecting {league} venues...")
        
        # Try both methods
        game_venues = get_comprehensive_venue_list(league)
        team_venues = try_teams_endpoint_for_venues(league)
        
        # Merge the data
        for venue_id, venue_data in {**team_venues, **game_venues}.items():
            if venue_id not in all_venues:
                all_venues[venue_id] = venue_data
                all_venues[venue_id]['league'] = league
            else:
                # Merge additional data
                all_venues[venue_id].update(venue_data)
    
    print(f"\n=== Summary: Found {len(all_venues)} unique venues ===")
    
    # Show sample venues with most data
    sorted_venues = sorted(all_venues.values(), 
                          key=lambda x: len([v for v in x.values() if v is not None]), 
                          reverse=True)
    
    for i, venue in enumerate(sorted_venues[:5]):
        print(f"\n{i+1}. {venue.get('name', 'Unknown')}")
        for key, value in venue.items():
            if value is not None and key != 'images':
                print(f"   {key}: {value}")
        
        images = venue.get('images', [])
        if images:
            print(f"   images: {len(images)} available")
    
    return all_venues

if __name__ == "__main__":
    venues = analyze_venue_features()
    
    # Save the results
    with open('venue_analysis_results.json', 'w') as f:
        json.dump(venues, f, indent=2)
    
    print(f"\nResults saved to venue_analysis_results.json")
