#!/usr/bin/env python3
"""
ESPN API Reference Generator
Generates comprehensive documentation of ESPN API endpoints and data structures
for MLB and NFL with live examples.
"""

import requests
import json
import datetime
from typing import Dict, Any, List
from dataclasses import dataclass
import time

# ESPN API Configuration
BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

LEAGUES = {
    "MLB": "baseball/mlb",
    "NFL": "football/nfl"
}

ENDPOINTS = {
    "scoreboard": "/scoreboard",
    "standings": "/standings", 
    "teams": "/teams",
    "news": "/news",
    "game_summary": "/summary?event={game_id}",
    "athletes": "/athletes",
    "schedule": "/scoreboard?dates={date}",
    "venues": "/venues"
}

@dataclass
class APIExample:
    endpoint: str
    description: str
    url: str
    response_structure: Dict[str, Any]
    sample_data: Dict[str, Any]
    key_fields: List[str]

class ESPNAPIExplorer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ESPN-API-Reference-Generator/1.0'
        })
        
    def make_request(self, url: str, description: str = "") -> Dict[str, Any]:
        """Make a request to the ESPN API with error handling"""
        try:
            print(f"Fetching: {description} - {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return {}
    
    def analyze_structure(self, data: Any, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """Recursively analyze the structure of API response data"""
        if current_depth >= max_depth:
            return {"type": str(type(data)), "truncated": True}
        
        if isinstance(data, dict):
            structure = {"type": "dict", "keys": {}}
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    structure["keys"][key] = self.analyze_structure(value, max_depth, current_depth + 1)
                else:
                    structure["keys"][key] = {
                        "type": type(value).__name__,
                        "sample": str(value)[:100] if isinstance(value, str) else value
                    }
            return structure
        elif isinstance(data, list):
            structure = {"type": "list", "length": len(data)}
            if data and current_depth < max_depth:
                structure["item_type"] = self.analyze_structure(data[0], max_depth, current_depth + 1)
            return structure
        else:
            return {"type": type(data).__name__, "value": data}
    
    def get_current_games(self, league: str) -> List[str]:
        """Get list of current game IDs for detailed analysis"""
        league_path = LEAGUES.get(league)
        if not league_path:
            return []
        
        url = f"{BASE_URL}/{league_path}/scoreboard"
        data = self.make_request(url, f"{league} Current Scoreboard")
        
        game_ids = []
        events = data.get("events", [])
        for event in events[:3]:  # Limit to first 3 games for detailed analysis
            game_ids.append(event.get("id", ""))
        
        return [gid for gid in game_ids if gid]
    
    def explore_league(self, league: str) -> Dict[str, Any]:
        """Comprehensive exploration of a league's API endpoints"""
        league_path = LEAGUES.get(league)
        if not league_path:
            return {}
        
        exploration = {
            "league": league.lower(),
            "exploration_time": datetime.datetime.now().isoformat(),
            "endpoints": {}
        }
        
        # 1. Scoreboard (Today)
        print(f"\n=== Exploring {league} API ===")
        scoreboard_url = f"{BASE_URL}/{league_path}/scoreboard"
        scoreboard_data = self.make_request(scoreboard_url, f"{league} Scoreboard")
        if scoreboard_data:
            exploration["endpoints"]["scoreboard_today"] = {
                "endpoint": "scoreboard",
                "url": scoreboard_url,
                "description": "Current day's games, scores, and basic information",
                "structure": self.analyze_structure(scoreboard_data),
                "sample_data": self.extract_sample_data(scoreboard_data),
                "key_fields": self.identify_key_fields(scoreboard_data)
            }
        
        # 2. Standings
        standings_url = f"{BASE_URL}/{league_path}/standings"
        standings_data = self.make_request(standings_url, f"{league} Standings")
        if standings_data:
            exploration["endpoints"]["standings"] = {
                "endpoint": "standings",
                "url": standings_url,
                "description": "League standings and team records",
                "structure": self.analyze_structure(standings_data),
                "sample_data": self.extract_sample_data(standings_data),
                "key_fields": self.identify_key_fields(standings_data)
            }
        
        # 3. Teams
        teams_url = f"{BASE_URL}/{league_path}/teams"
        teams_data = self.make_request(teams_url, f"{league} Teams")
        if teams_data:
            exploration["endpoints"]["teams"] = {
                "endpoint": "teams",
                "url": teams_url,
                "description": "All teams in the league with detailed information",
                "structure": self.analyze_structure(teams_data),
                "sample_data": self.extract_sample_data(teams_data),
                "key_fields": self.identify_key_fields(teams_data)
            }
        
        # 4. News
        news_url = f"{BASE_URL}/{league_path}/news"
        news_data = self.make_request(news_url, f"{league} News")
        if news_data:
            exploration["endpoints"]["news"] = {
                "endpoint": "news", 
                "url": news_url,
                "description": "Recent news articles for the league",
                "structure": self.analyze_structure(news_data),
                "sample_data": self.extract_sample_data(news_data),
                "key_fields": self.identify_key_fields(news_data)
            }
        
        # 5. Athletes (for team-based analysis)
        if scoreboard_data and "events" in scoreboard_data and scoreboard_data["events"]:
            # Get athletes from first team
            first_event = scoreboard_data["events"][0]
            competitions = first_event.get("competitions", [])
            if competitions:
                competitors = competitions[0].get("competitors", [])
                if competitors:
                    team_id = competitors[0].get("team", {}).get("id", "")
                    if team_id:
                        athletes_url = f"{BASE_URL}/{league_path}/teams/{team_id}/athletes"
                        athletes_data = self.make_request(athletes_url, f"{league} Team Athletes")
                        if athletes_data:
                            exploration["endpoints"]["team_athletes"] = {
                                "endpoint": f"teams/{team_id}/athletes",
                                "url": athletes_url,
                                "description": "Athletes/players for a specific team",
                                "structure": self.analyze_structure(athletes_data),
                                "sample_data": self.extract_sample_data(athletes_data),
                                "key_fields": self.identify_key_fields(athletes_data)
                            }
        
        # 6. Game Details (Multiple examples)
        game_ids = self.get_current_games(league)
        exploration["endpoints"]["game_details_examples"] = []
        
        for i, game_id in enumerate(game_ids[:2]):  # Limit to 2 games for space
            game_detail_url = f"{BASE_URL}/{league_path}/summary?event={game_id}"
            game_detail_data = self.make_request(game_detail_url, f"{league} Game {game_id} Details")
            if game_detail_data:
                exploration["endpoints"]["game_details_examples"].append({
                    "game_id": game_id,
                    "endpoint": f"summary?event={game_id}",
                    "url": game_detail_url,
                    "description": f"Detailed game information for game {game_id}",
                    "structure": self.analyze_structure(game_detail_data),
                    "sample_data": self.extract_sample_data(game_detail_data),
                    "key_fields": self.identify_key_fields(game_detail_data)
                })
        
        # 7. Schedule (Previous day for completed games)
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        schedule_url = f"{BASE_URL}/{league_path}/scoreboard?dates={yesterday}"
        schedule_data = self.make_request(schedule_url, f"{league} Schedule {yesterday}")
        if schedule_data:
            exploration["endpoints"]["schedule_historical"] = {
                "endpoint": f"scoreboard?dates={yesterday}",
                "url": schedule_url,
                "description": f"Games for specific date ({yesterday})",
                "structure": self.analyze_structure(schedule_data),
                "sample_data": self.extract_sample_data(schedule_data),
                "key_fields": self.identify_key_fields(schedule_data)
            }
        
        return exploration
    
    def extract_sample_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meaningful sample data for documentation"""
        samples = {}
        
        if isinstance(data, dict):
            # Extract top-level structure info
            samples["top_level_keys"] = list(data.keys())[:10]
            
            # Extract sample events if available
            if "events" in data and isinstance(data["events"], list) and data["events"]:
                event = data["events"][0]
                samples["sample_event"] = {
                    "id": event.get("id", ""),
                    "name": event.get("name", ""),
                    "status": event.get("status", {}).get("type", {}).get("description", ""),
                    "teams": [comp.get("team", {}).get("displayName", "") 
                             for comp in event.get("competitions", [{}])[0].get("competitors", [])]
                }
            
            # Extract sample team if available
            if "teams" in data and isinstance(data["teams"], list) and data["teams"]:
                team = data["teams"][0]
                samples["sample_team"] = {
                    "id": team.get("id", ""),
                    "displayName": team.get("displayName", ""),
                    "abbreviation": team.get("abbreviation", ""),
                    "location": team.get("location", "")
                }
            
            # Extract sample article if available
            if "articles" in data and isinstance(data["articles"], list) and data["articles"]:
                article = data["articles"][0]
                samples["sample_article"] = {
                    "headline": article.get("headline", ""),
                    "description": article.get("description", "")[:100] + "...",
                    "published": article.get("published", "")
                }
        
        return samples
    
    def identify_key_fields(self, data: Dict[str, Any]) -> List[str]:
        """Identify the most important fields in the API response"""
        key_fields = []
        
        if isinstance(data, dict):
            # Always important
            always_key = ["id", "name", "displayName", "status", "events", "teams", "competitions"]
            for field in always_key:
                if field in data:
                    key_fields.append(field)
            
            # Context-specific important fields
            if "events" in data:
                key_fields.extend(["season", "week", "leagues"])
            if "teams" in data:
                key_fields.extend(["sports", "leagues"])
            if "articles" in data:
                key_fields.extend(["header", "results"])
            if "children" in data:  # Standings
                key_fields.extend(["standings", "children"])
        
        return key_fields

def main():
    """Generate comprehensive ESPN API reference documentation"""
    explorer = ESPNAPIExplorer()
    
    # Create comprehensive reference for each league
    for league in ["MLB", "NFL"]:
        print(f"\n{'='*50}")
        print(f"EXPLORING {league} API")
        print(f"{'='*50}")
        
        exploration = explorer.explore_league(league)
        
        # Save individual league exploration
        output_file = f"c:\\Users\\kelly\\GitHub\\Scores\\ESPN_API_REFERENCE_{league}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(exploration, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {league} API reference to: {output_file}")
        
        # Brief pause between leagues
        time.sleep(1)
    
    print(f"\n{'='*50}")
    print("EXPLORATION COMPLETE")
    print(f"{'='*50}")
    print("Generated files:")
    print("- ESPN_API_REFERENCE_MLB.json")
    print("- ESPN_API_REFERENCE_NFL.json")

if __name__ == "__main__":
    main()
