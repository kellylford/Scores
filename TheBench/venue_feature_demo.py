#!/usr/bin/env python3
"""
Venue Feature Implementation Plan
Shows how venue browsing could work in the Scores app
"""

import requests
import json
from datetime import datetime, timedelta

class VenueExplorer:
    """
    Venue browsing feature for the Scores app
    Allows users to browse stadiums/venues by sport and view details
    """
    
    def __init__(self, espn_api):
        self.espn_api = espn_api
        self.venue_cache = {}
    
    def get_venues_for_league(self, league_key):
        """Get all venues for a specific league"""
        
        if league_key in self.venue_cache:
            return self.venue_cache[league_key]
        
        venues = {}
        
        # Get venues from recent games (more comprehensive than teams endpoint)
        today = datetime.now()
        start_date = today - timedelta(days=60)
        end_date = today + timedelta(days=30)
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
        LEAGUES = {
            "NFL": "football/nfl",
            "NBA": "basketball/nba", 
            "MLB": "baseball/mlb",
            "NHL": "hockey/nhl",
            "NCAAF": "football/college-football",
            "NCAAM": "basketball/mens-college-basketball"
        }
        
        league_path = LEAGUES.get(league_key)
        if not league_path:
            return {}
        
        url = f"{BASE_URL}/{league_path}/scoreboard?dates={start_str}-{end_str}&limit=100"
        
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                events = data.get('events', [])
                
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
                                'indoor': venue.get('indoor', False),
                                'home_teams': []  # Will be filled by finding home games
                            }
                            
                            # Get enhanced details from game details
                            self._enhance_venue_details(venue_id, venues[venue_id], league_path, event.get('id'))
                
                # Find home teams for each venue
                self._find_home_teams(venues, league_key)
                
                self.venue_cache[league_key] = venues
                
        except Exception as e:
            print(f"Error getting venues: {e}")
            
        return venues
    
    def _enhance_venue_details(self, venue_id, venue_data, league_path, event_id):
        """Get enhanced venue details from game details"""
        
        if not event_id:
            return
            
        BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
        detail_url = f"{BASE_URL}/{league_path}/summary?event={event_id}"
        
        try:
            resp = requests.get(detail_url)
            if resp.status_code == 200:
                data = resp.json()
                if 'gameInfo' in data and 'venue' in data['gameInfo']:
                    detailed_venue = data['gameInfo']['venue']
                    
                    # Add enhanced details
                    venue_data.update({
                        'grass': detailed_venue.get('grass'),
                        'capacity': detailed_venue.get('capacity'),
                        'zipCode': detailed_venue.get('address', {}).get('zipCode'),
                        'images': detailed_venue.get('images', []),
                        'guid': detailed_venue.get('guid')
                    })
                    
        except:
            pass  # Skip if can't get details
    
    def _find_home_teams(self, venues, league_key):
        """Find which teams play home games at each venue"""
        
        # This would analyze game data to determine home teams
        # For now, simplified implementation
        pass
    
    def get_venue_details(self, venue_id, league_key):
        """Get comprehensive details for a specific venue"""
        
        venues = self.get_venues_for_league(league_key)
        venue = venues.get(venue_id, {})
        
        if not venue:
            return None
        
        # Create a comprehensive venue profile
        details = {
            'basic_info': {
                'name': venue.get('name'),
                'city': venue.get('city'),
                'state': venue.get('state'),
                'zip_code': venue.get('zipCode'),
                'league': league_key
            },
            'characteristics': {
                'indoor': venue.get('indoor', False),
                'grass': venue.get('grass'),
                'capacity': venue.get('capacity')
            },
            'media': {
                'images': venue.get('images', [])
            },
            'home_teams': venue.get('home_teams', [])
        }
        
        # Add interesting facts based on available data
        details['interesting_facts'] = self._generate_interesting_facts(venue, league_key)
        
        return details
    
    def _generate_interesting_facts(self, venue, league_key):
        """Generate interesting facts about a venue"""
        
        facts = []
        
        # Surface type facts
        if venue.get('grass') is True:
            facts.append("🌱 Natural grass playing surface")
        elif venue.get('grass') is False:
            facts.append("🏈 Artificial turf playing surface")
        
        # Indoor/outdoor facts
        if venue.get('indoor'):
            facts.append("🏢 Indoor stadium with climate control")
        else:
            facts.append("🌤️ Open-air stadium exposed to weather")
        
        # Capacity facts (if available)
        capacity = venue.get('capacity')
        if capacity:
            try:
                cap_num = int(capacity)
                if cap_num > 80000:
                    facts.append(f"🏟️ Massive stadium seating {cap_num:,} fans")
                elif cap_num > 60000:
                    facts.append(f"🏟️ Large stadium seating {cap_num:,} fans")
                else:
                    facts.append(f"🏟️ Intimate venue seating {cap_num:,} fans")
            except:
                pass
        
        # League-specific facts
        if league_key == "MLB":
            facts.append("⚾ Major League Baseball venue")
            if "Field" in venue.get('name', ''):
                facts.append("⭐ Classic baseball 'Field' naming")
            elif "Park" in venue.get('name', ''):
                facts.append("⭐ Traditional baseball 'Park' naming")
        
        elif league_key == "NFL":
            facts.append("🏈 National Football League venue")
            if venue.get('indoor'):
                facts.append("❄️ Weather never affects games here")
        
        # Location facts
        city = venue.get('city', '')
        state = venue.get('state', '')
        if city and state:
            facts.append(f"📍 Located in {city}, {state}")
        
        return facts

# Example usage for UI integration
def demo_venue_feature():
    """Demo how the venue feature would work"""
    
    print("=== VENUE BROWSER DEMO ===\n")
    
    # This would integrate with existing ESPN API
    venue_explorer = VenueExplorer(None)
    
    # Show venues for NFL
    print("📍 NFL VENUES")
    print("-" * 50)
    
    nfl_venues = venue_explorer.get_venues_for_league("NFL")
    
    # Sort by name for nice display
    sorted_venues = sorted(nfl_venues.values(), key=lambda x: x.get('name', ''))
    
    for i, venue in enumerate(sorted_venues[:10]):  # Show first 10
        name = venue.get('name', 'Unknown')
        city = venue.get('city', 'Unknown')
        state = venue.get('state', 'Unknown')
        indoor = "🏢" if venue.get('indoor') else "🌤️"
        grass = "🌱" if venue.get('grass') else "🏈" if venue.get('grass') is False else "❓"
        
        print(f"{i+1:2d}. {name}")
        print(f"    📍 {city}, {state} {indoor} {grass}")
    
    print(f"\n... and {len(sorted_venues) - 10} more venues")
    
    # Show detailed view for one venue
    if sorted_venues:
        sample_venue = sorted_venues[0]
        venue_id = sample_venue.get('id')
        
        print(f"\n" + "="*60)
        print(f"VENUE DETAILS: {sample_venue.get('name')}")
        print("="*60)
        
        details = venue_explorer.get_venue_details(venue_id, "NFL")
        
        if details:
            basic = details['basic_info']
            chars = details['characteristics']
            facts = details['interesting_facts']
            
            print(f"\n🏟️  {basic['name']}")
            print(f"📍  {basic['city']}, {basic['state']} {basic.get('zip_code', '')}")
            print(f"🏈  {basic['league']}")
            
            print(f"\n📊 CHARACTERISTICS:")
            print(f"   Indoor: {'Yes' if chars['indoor'] else 'No'}")
            print(f"   Surface: {'Natural Grass' if chars['grass'] else 'Artificial Turf' if chars['grass'] is False else 'Unknown'}")
            if chars['capacity']:
                print(f"   Capacity: {chars['capacity']:,}")
            
            if facts:
                print(f"\n✨ INTERESTING FACTS:")
                for fact in facts:
                    print(f"   • {fact}")
            
            images = details['media']['images']
            if images:
                print(f"\n📸 IMAGES: {len(images)} available")
                for img in images[:2]:  # Show first 2
                    rel = ", ".join(img.get('rel', []))
                    print(f"   • {img['href']} ({rel})")

if __name__ == "__main__":
    demo_venue_feature()
