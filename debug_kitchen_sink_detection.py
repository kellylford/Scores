#!/usr/bin/env python3

import json
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import ApiService

def debug_kitchen_sink_detection():
    """Debug why Kitchen Sink isn't appearing"""
    
    print("=== Kitchen Sink Detection Debug ===")
    
    # Get today's MLB games
    try:
        games = ApiService.get_scores('MLB', None)
        print(f"Found {len(games)} MLB games")
        
        if not games:
            print("No games found - testing with demo data")
            # Load demo data
            demo_file = "api_exploration/game_details_401696636.json"
            if os.path.exists(demo_file):
                with open(demo_file, 'r') as f:
                    demo_data = json.load(f)
                    print(f"Loaded demo data from {demo_file}")
                    
                    # Check Kitchen Sink data in demo
                    check_kitchen_sink_data(demo_data, "Demo Game")
            else:
                print(f"Demo file {demo_file} not found")
            return
        
        # Check first few games for Kitchen Sink data
        for i, game in enumerate(games[:3]):
            print(f"\n--- Game {i+1}: {game.get('shortName', 'Unknown')} ---")
            
            # Get detailed game data
            game_id = game.get('id')
            if game_id:
                try:
                    details = ApiService.get_game_details('MLB', game_id)
                    check_kitchen_sink_data(details, f"Game {game_id}")
                except Exception as e:
                    print(f"Error getting details for game {game_id}: {e}")
            else:
                print("No game ID found")
                
    except Exception as e:
        print(f"Error getting games: {e}")

def check_kitchen_sink_data(game_data, game_name):
    """Check what Kitchen Sink data is available"""
    
    print(f"\n=== Kitchen Sink Analysis for {game_name} ===")
    
    if not game_data:
        print("No game data provided")
        return
    
    # Check for rosters
    rosters = game_data.get('rosters')
    if rosters:
        print(f"✓ Rosters found: {len(rosters)} teams")
        for roster in rosters:
            team_name = roster.get('team', {}).get('displayName', 'Unknown')
            entries = roster.get('roster', {}).get('entries', [])
            print(f"  - {team_name}: {len(entries)} players")
    else:
        print("✗ No rosters found")
    
    # Check for season series
    season_series = game_data.get('seasonSeries')
    if season_series:
        print(f"✓ Season series found")
        events = season_series.get('events', [])
        print(f"  - {len(events)} events in series")
    else:
        print("✗ No season series found")
    
    # Check for articles
    articles = game_data.get('articles')
    if articles:
        print(f"✓ Articles found: {len(articles)} articles")
    else:
        print("✗ No articles found")
    
    # Check for odds history
    competitions = game_data.get('competitions', [])
    if competitions:
        comp = competitions[0]
        odds = comp.get('odds')
        if odds:
            print(f"✓ Odds found: {len(odds)} bookmakers")
        else:
            print("✗ No odds found")
            
        # Check for against the spread
        ats_records = []
        competitors = comp.get('competitors', [])
        for competitor in competitors:
            team = competitor.get('team', {})
            records = team.get('records', [])
            for record in records:
                if record.get('type') == 'ats':
                    ats_records.append(record)
        
        if ats_records:
            print(f"✓ ATS records found: {len(ats_records)} teams")
        else:
            print("✗ No ATS records found")
    
    # Check for expert picks
    expert_picks = game_data.get('predictor', {}).get('experts')
    if expert_picks:
        print(f"✓ Expert picks found: {len(expert_picks)} experts")
    else:
        print("✗ No expert picks found")
    
    # Summary
    has_any_kitchen_sink = any([
        rosters,
        season_series,
        articles,
        (competitions and competitions[0].get('odds')),
        expert_picks
    ])
    
    print(f"\n=== Kitchen Sink Summary ===")
    print(f"Has Kitchen Sink data: {has_any_kitchen_sink}")
    
    return has_any_kitchen_sink

if __name__ == "__main__":
    debug_kitchen_sink_detection()
