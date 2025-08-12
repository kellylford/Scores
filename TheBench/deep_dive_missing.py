#!/usr/bin/env python3
"""
Deep dive into specific missing MLB data fields
"""

import sys
sys.path.append('.')

import requests
import json
from espn_api import get_game_details

def deep_dive_missing_fields():
    """Detailed analysis of potentially valuable missing fields"""
    
    # Get a real game to analyze
    url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    response = requests.get(url)
    scoreboard = response.json()
    
    if not scoreboard.get("events"):
        print("No MLB games found today")
        return
    
    game_id = scoreboard["events"][0]["id"]
    game_details = get_game_details("MLB", game_id)
    
    print("=== DETAILED ANALYSIS OF MISSING HIGH-VALUE FIELDS ===\n")
    
    # 1. Rosters - Player lineups
    if "rosters" in game_details:
        print("🧑‍🤝‍🧑 ROSTERS (Player Lineups):")
        rosters = game_details["rosters"]
        print(f"   Teams with rosters: {len(rosters)}")
        
        if rosters:
            team = rosters[0]
            print(f"   Team: {team.get('team', {}).get('displayName', 'Unknown')}")
            entries = team.get("entries", [])
            print(f"   Players in roster: {len(entries)}")
            
            if entries:
                player = entries[0]
                print(f"   Sample player: {player.get('athlete', {}).get('displayName', 'Unknown')}")
                print(f"   Position: {player.get('position', {}).get('abbreviation', 'Unknown')}")
                print(f"   Jersey: {player.get('jersey', 'Unknown')}")
        print()
    
    # 2. At-Bats summary
    if "atBats" in game_details:
        print("⚾ AT-BATS (Detailed batting sequences):")
        at_bats = game_details["atBats"]
        print(f"   Structure keys: {list(at_bats.keys())[:10]}")
        
        # Look for at-bat entries
        for key, value in at_bats.items():
            if isinstance(value, list) and value:
                print(f"   {key}: {len(value)} entries")
                if isinstance(value[0], dict):
                    print(f"   Sample {key} keys: {list(value[0].keys())[:5]}")
                break
        print()
    
    # 3. Win Probability
    if "winprobability" in game_details:
        print("📊 WIN PROBABILITY (Live game odds):")
        win_prob = game_details["winprobability"]
        print(f"   Data points: {len(win_prob)}")
        
        if win_prob:
            latest = win_prob[-1]  # Most recent
            home_pct = latest.get("homeWinPercentage", 0) * 100
            print(f"   Current home win probability: {home_pct:.1f}%")
            print(f"   Associated with play ID: {latest.get('playId', 'Unknown')}")
        print()
    
    # 4. Season Series
    if "seasonseries" in game_details:
        print("🗓️ SEASON SERIES (Head-to-head record):")
        series = game_details["seasonseries"]
        print(f"   Teams: {len(series)}")
        
        if series:
            team_series = series[0]
            print(f"   Team: {team_series.get('team', {}).get('displayName', 'Unknown')}")
            print(f"   Series summary: {team_series.get('summary', 'Unknown')}")
        print()
    
    # 5. Videos
    if "videos" in game_details:
        print("🎥 VIDEOS (Game highlights):")
        videos = game_details["videos"]
        print(f"   Videos available: {len(videos)}")
        
        if videos:
            video = videos[0]
            print(f"   Sample video: {video.get('headline', 'Unknown')}")
            print(f"   Duration: {video.get('duration', 'Unknown')} seconds")
        print()
    
    # 6. Article
    if "article" in game_details:
        print("📰 ARTICLE (Game recap/preview):")
        article = game_details["article"]
        print(f"   Headline: {article.get('headline', 'Unknown')}")
        print(f"   Type: {article.get('type', 'Unknown')}")
        print(f"   Word count: {len(article.get('story', '').split()) if article.get('story') else 0} words")
        print()
    
    # 7. Against The Spread
    if "againstTheSpread" in game_details:
        print("🎰 AGAINST THE SPREAD (Betting performance):")
        ats = game_details["againstTheSpread"]
        print(f"   Teams: {len(ats)}")
        
        if ats:
            team_ats = ats[0]
            team_name = team_ats.get("team", {}).get("displayName", "Unknown")
            record = team_ats.get("summary", "Unknown")
            print(f"   {team_name} ATS record: {record}")
        print()
    
    # 8. Pick Center
    if "pickcenter" in game_details:
        print("🎯 PICK CENTER (Expert predictions):")
        picks = game_details["pickcenter"]
        print(f"   Pick data available: {len(picks)}")
        
        if picks:
            pick_data = picks[0]
            print(f"   Keys available: {list(pick_data.keys())[:5]}")
        print()

    print("=== SUMMARY OF MISSING HIGH-VALUE FEATURES ===")
    print("1. 🧑‍🤝‍🧑 ROSTERS - Starting lineups and bench players")
    print("2. ⚾ AT-BATS - Detailed at-bat summaries beyond play-by-play")
    print("3. 📊 WIN PROBABILITY - Live probability tracking throughout game")
    print("4. 🗓️ SEASON SERIES - Head-to-head record between teams")
    print("5. 🎥 VIDEOS - Game highlights and video content")
    print("6. 📰 ARTICLE - Game recaps, previews, and analysis")
    print("7. 🎰 AGAINST THE SPREAD - Team betting performance records")
    print("8. 🎯 PICK CENTER - Expert predictions and picks")

if __name__ == "__main__":
    deep_dive_missing_fields()
