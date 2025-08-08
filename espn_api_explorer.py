#!/usr/bin/env python3
"""
ESPN API Explorer Tool

This tool systematically explores ESPN's API to understand data structures,
available endpoints, and response formats. We'll focus on MLB first.
"""

import sys
import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ESPN API Configuration
BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
LEAGUES = {
    "mlb": "baseball/mlb",
    "nfl": "football/nfl", 
    "nba": "basketball/nba",
    "nhl": "hockey/nhl"
}

class ESPNAPIExplorer:
    """Comprehensive ESPN API exploration tool"""
    
    def __init__(self, league="mlb"):
        self.league = league
        self.league_path = LEAGUES.get(league)
        self.base_url = f"{BASE_URL}/{self.league_path}"
        self.session = requests.Session()
        self.results = {}
        
    def log(self, message, level="INFO"):
        """Simple logging function"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def safe_request(self, url: str, description: str) -> Optional[Dict]:
        """Make a safe API request with error handling"""
        try:
            self.log(f"Requesting: {description}")
            self.log(f"URL: {url}")
            
            response = self.session.get(url, timeout=10)
            self.log(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Success: Got {len(str(data))} characters of JSON")
                return data
            else:
                self.log(f"Failed: HTTP {response.status_code}", "ERROR")
                return None
                
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", "ERROR")
            return None
        except json.JSONDecodeError as e:
            self.log(f"JSON decode failed: {e}", "ERROR")
            return None
    
    def explore_endpoint_structure(self, data: Dict, path: str = "", max_depth: int = 3) -> Dict:
        """Recursively explore data structure and return summary"""
        if max_depth <= 0:
            return {"truncated": True, "type": str(type(data))}
        
        if isinstance(data, dict):
            structure = {"type": "dict", "keys": {}}
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    structure["keys"][key] = self.explore_endpoint_structure(
                        value, f"{path}.{key}", max_depth - 1
                    )
                else:
                    structure["keys"][key] = {
                        "type": str(type(value).__name__),
                        "sample": str(value)[:100] if value else None
                    }
            return structure
            
        elif isinstance(data, list):
            structure = {"type": "list", "length": len(data)}
            if data:
                structure["item_type"] = self.explore_endpoint_structure(
                    data[0], f"{path}[0]", max_depth - 1
                )
            return structure
            
        else:
            return {"type": str(type(data).__name__), "value": str(data)[:100]}
    
    def save_raw_data(self, data: Dict, filename: str):
        """Save raw JSON data to file for detailed analysis"""
        try:
            os.makedirs("api_exploration", exist_ok=True)
            filepath = f"api_exploration/{filename}"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log(f"Saved raw data to: {filepath}")
        except Exception as e:
            self.log(f"Failed to save data: {e}", "ERROR")
    
    def explore_scoreboard(self, date: datetime = None) -> Dict:
        """Explore scoreboard endpoint"""
        self.log("=== EXPLORING SCOREBOARD ENDPOINT ===")
        
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y%m%d")
        url = f"{self.base_url}/scoreboard?dates={date_str}"
        
        data = self.safe_request(url, f"Scoreboard for {date_str}")
        if not data:
            return {}
        
        # Save raw data
        self.save_raw_data(data, f"scoreboard_{date_str}.json")
        
        # Analyze structure
        structure = self.explore_endpoint_structure(data)
        
        # Extract key information
        analysis = {
            "endpoint": "scoreboard",
            "date": date_str,
            "structure": structure,
            "games_found": 0,
            "sample_game_ids": [],
            "available_game_data": {}
        }
        
        # Look for games
        events = self.find_nested_key(data, "events")
        if events and isinstance(events, list):
            analysis["games_found"] = len(events)
            self.log(f"Found {len(events)} games")
            
            # Analyze first few games
            for i, game in enumerate(events[:3]):
                if isinstance(game, dict) and "id" in game:
                    game_id = game["id"]
                    analysis["sample_game_ids"].append(game_id)
                    
                    # Analyze what data is available for this game
                    game_analysis = {
                        "id": game_id,
                        "status": game.get("status", {}).get("type", {}).get("name", "Unknown"),
                        "teams": [],
                        "available_keys": list(game.keys())
                    }
                    
                    # Extract team info
                    competitions = game.get("competitions", [])
                    if competitions:
                        competitors = competitions[0].get("competitors", [])
                        for comp in competitors:
                            if isinstance(comp, dict) and "team" in comp:
                                team = comp["team"]
                                game_analysis["teams"].append(team.get("displayName", "Unknown"))
                    
                    analysis["available_game_data"][game_id] = game_analysis
                    self.log(f"Game {i+1}: {' vs '.join(game_analysis['teams'])} ({game_analysis['status']})")
        
        return analysis
    
    def explore_game_details(self, game_id: str) -> Dict:
        """Explore detailed game information"""
        self.log(f"=== EXPLORING GAME DETAILS: {game_id} ===")
        
        url = f"{self.base_url}/summary?event={game_id}"
        data = self.safe_request(url, f"Game details for {game_id}")
        if not data:
            return {}
        
        # Save raw data
        self.save_raw_data(data, f"game_details_{game_id}.json")
        
        # Analyze structure
        structure = self.explore_endpoint_structure(data)
        
        analysis = {
            "endpoint": "game_details",
            "game_id": game_id,
            "structure": structure,
            "top_level_keys": list(data.keys()) if isinstance(data, dict) else [],
            "boxscore_analysis": {},
            "other_data": {}
        }
        
        # Specific boxscore analysis
        if "boxscore" in data:
            boxscore = data["boxscore"]
            self.log("Found boxscore data!")
            analysis["boxscore_analysis"] = {
                "exists": True,
                "type": str(type(boxscore)),
                "structure": self.explore_endpoint_structure(boxscore, max_depth=4)
            }
            
            # Look for teams and players specifically
            if isinstance(boxscore, dict):
                if "teams" in boxscore:
                    teams = boxscore["teams"]
                    analysis["boxscore_analysis"]["teams"] = {
                        "exists": True,
                        "count": len(teams) if isinstance(teams, list) else 0,
                        "sample_structure": self.explore_endpoint_structure(teams[0] if teams else {})
                    }
                
                if "players" in boxscore:
                    players = boxscore["players"]
                    analysis["boxscore_analysis"]["players"] = {
                        "exists": True,
                        "count": len(players) if isinstance(players, list) else 0,
                        "sample_structure": self.explore_endpoint_structure(players[0] if players else {})
                    }
                
                # Look for other interesting keys
                other_keys = [k for k in boxscore.keys() if k not in ["teams", "players"]]
                if other_keys:
                    analysis["boxscore_analysis"]["other_keys"] = other_keys
        else:
            analysis["boxscore_analysis"]["exists"] = False
            self.log("No boxscore data found")
        
        # Check for other interesting data
        interesting_keys = ["statistics", "leaders", "news", "odds", "broadcasts", "injuries"]
        for key in interesting_keys:
            if key in data:
                analysis["other_data"][key] = {
                    "exists": True,
                    "type": str(type(data[key])),
                    "structure": self.explore_endpoint_structure(data[key], max_depth=2)
                }
        
        return analysis
    
    def explore_standings(self) -> Dict:
        """Explore standings endpoint"""
        self.log("=== EXPLORING STANDINGS ENDPOINT ===")
        
        url = f"{self.base_url}/standings"
        data = self.safe_request(url, "Standings")
        if not data:
            return {}
        
        # Save raw data
        self.save_raw_data(data, "standings.json")
        
        # Analyze structure
        structure = self.explore_endpoint_structure(data)
        
        analysis = {
            "endpoint": "standings",
            "structure": structure,
            "divisions_found": 0,
            "teams_per_division": {},
            "sample_team_data": {}
        }
        
        # Look for standings data
        standings = self.find_nested_key(data, "standings")
        if standings:
            self.log(f"Found standings data")
            analysis["divisions_found"] = len(standings) if isinstance(standings, list) else 0
            
            # Analyze divisions
            for i, division in enumerate(standings[:3] if isinstance(standings, list) else []):
                if isinstance(division, dict):
                    div_name = division.get("name", f"Division {i}")
                    entries = division.get("entries", [])
                    analysis["teams_per_division"][div_name] = len(entries)
                    
                    if entries and isinstance(entries, list):
                        # Sample team data
                        sample_team = entries[0]
                        analysis["sample_team_data"][div_name] = self.explore_endpoint_structure(sample_team)
        
        return analysis
    
    def find_nested_key(self, data: Any, target_key: str) -> Any:
        """Recursively find a key in nested data structure"""
        if isinstance(data, dict):
            if target_key in data:
                return data[target_key]
            for value in data.values():
                result = self.find_nested_key(value, target_key)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.find_nested_key(item, target_key)
                if result is not None:
                    return result
        return None
    
    def run_comprehensive_exploration(self) -> Dict:
        """Run a comprehensive exploration of the API"""
        self.log(f"Starting comprehensive exploration of {self.league.upper()} API")
        self.log("=" * 60)
        
        results = {
            "league": self.league,
            "exploration_time": datetime.now().isoformat(),
            "endpoints": {}
        }
        
        # 1. Explore scoreboard for today
        self.log("\n1. Exploring today's scoreboard...")
        today_scoreboard = self.explore_scoreboard(datetime.now())
        results["endpoints"]["scoreboard_today"] = today_scoreboard
        
        # 2. Explore scoreboard for yesterday (more likely to have completed games)
        self.log("\n2. Exploring yesterday's scoreboard...")
        yesterday_scoreboard = self.explore_scoreboard(datetime.now() - timedelta(days=1))
        results["endpoints"]["scoreboard_yesterday"] = yesterday_scoreboard
        
        # 3. Explore scoreboard for a week ago
        self.log("\n3. Exploring scoreboard from a week ago...")
        week_ago_scoreboard = self.explore_scoreboard(datetime.now() - timedelta(days=7))
        results["endpoints"]["scoreboard_week_ago"] = week_ago_scoreboard
        
        # 4. Explore game details for sample games
        sample_game_ids = []
        for sb in [today_scoreboard, yesterday_scoreboard, week_ago_scoreboard]:
            sample_game_ids.extend(sb.get("sample_game_ids", []))
        
        if sample_game_ids:
            self.log(f"\n4. Exploring game details for {len(sample_game_ids)} sample games...")
            results["endpoints"]["game_details"] = {}
            
            for game_id in sample_game_ids[:5]:  # Limit to 5 games to avoid too many requests
                game_analysis = self.explore_game_details(game_id)
                results["endpoints"]["game_details"][game_id] = game_analysis
        
        # 5. Explore standings
        self.log("\n5. Exploring standings...")
        standings_analysis = self.explore_standings()
        results["endpoints"]["standings"] = standings_analysis
        
        # Save comprehensive results
        self.save_raw_data(results, f"comprehensive_analysis_{self.league}.json")
        
        return results
    
    def print_summary(self, results: Dict):
        """Print a human-readable summary of the exploration"""
        print("\n" + "=" * 60)
        print(f"ESPN {results['league'].upper()} API EXPLORATION SUMMARY")
        print("=" * 60)
        
        # Scoreboard summary
        print("\n📊 SCOREBOARD ENDPOINTS:")
        for period, data in results["endpoints"].items():
            if "scoreboard" in period:
                games_count = data.get("games_found", 0)
                print(f"  {period}: {games_count} games found")
        
        # Game details summary
        print("\n🎮 GAME DETAILS:")
        game_details = results["endpoints"].get("game_details", {})
        if game_details:
            boxscore_games = []
            no_boxscore_games = []
            
            for game_id, details in game_details.items():
                if details.get("boxscore_analysis", {}).get("exists", False):
                    boxscore_games.append(game_id)
                else:
                    no_boxscore_games.append(game_id)
            
            print(f"  Games with boxscore data: {len(boxscore_games)}")
            print(f"  Games without boxscore data: {len(no_boxscore_games)}")
            
            if boxscore_games:
                print("  📈 Boxscore structure found in:")
                for game_id in boxscore_games:
                    game_data = game_details[game_id]
                    boxscore = game_data.get("boxscore_analysis", {})
                    teams_count = boxscore.get("teams", {}).get("count", 0)
                    players_count = boxscore.get("players", {}).get("count", 0)
                    print(f"    {game_id}: {teams_count} teams, {players_count} player groups")
        
        # Standings summary
        print("\n🏆 STANDINGS:")
        standings = results["endpoints"].get("standings", {})
        if standings.get("divisions_found", 0) > 0:
            print(f"  Divisions found: {standings['divisions_found']}")
            for div_name, team_count in standings.get("teams_per_division", {}).items():
                print(f"    {div_name}: {team_count} teams")
        
        print(f"\n📁 Raw data saved to: api_exploration/")
        print("   Use these files for detailed analysis!")

def main():
    """Main function to run the API explorer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ESPN API Explorer")
    parser.add_argument("--league", default="mlb", choices=list(LEAGUES.keys()),
                      help="League to explore (default: mlb)")
    parser.add_argument("--game-id", help="Specific game ID to analyze")
    parser.add_argument("--quick", action="store_true", 
                      help="Quick exploration (just today's scoreboard)")
    
    args = parser.parse_args()
    
    explorer = ESPNAPIExplorer(args.league)
    
    if args.game_id:
        # Analyze specific game
        results = explorer.explore_game_details(args.game_id)
        print(json.dumps(results, indent=2))
    elif args.quick:
        # Quick exploration
        results = explorer.explore_scoreboard()
        explorer.print_summary({"league": args.league, "endpoints": {"scoreboard_today": results}})
    else:
        # Comprehensive exploration
        results = explorer.run_comprehensive_exploration()
        explorer.print_summary(results)

if __name__ == "__main__":
    main()
