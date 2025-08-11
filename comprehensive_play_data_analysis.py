#!/usr/bin/env python3

import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.api_service import ApiService
from datetime import datetime
import json

def analyze_all_play_data():
    """Comprehensive analysis of all available play data for MLB and NFL"""
    
    print("=" * 80)
    print("COMPREHENSIVE SPORTS PLAY DATA ANALYSIS")
    print("=" * 80)
    
    # === MLB ANALYSIS ===
    print("\n" + "=" * 40)
    print("MLB PLAY DATA ANALYSIS")
    print("=" * 40)
    
    try:
        mlb_scores = ApiService.get_scores('MLB', datetime.now())
        if mlb_scores:
            mlb_game_id = mlb_scores[0].get('id')
            print(f"Analyzing MLB game: {mlb_scores[0].get('name', 'Unknown')}")
            print(f"Game ID: {mlb_game_id}")
            
            mlb_details = ApiService.get_game_details('MLB', mlb_game_id)
            mlb_plays = mlb_details.get('plays', [])
            
            if mlb_plays:
                print(f"\nTotal MLB plays found: {len(mlb_plays)}")
                
                # Analyze first few plays for structure
                print(f"\n--- MLB PLAY STRUCTURE ANALYSIS ---")
                for i, play in enumerate(mlb_plays[:3]):
                    print(f"\nMLB Play {i+1} - ALL AVAILABLE FIELDS:")
                    print(f"{'Field':<25} {'Value':<50}")
                    print("-" * 75)
                    
                    # Show all top-level fields
                    for key, value in play.items():
                        if isinstance(value, dict):
                            print(f"{key:<25} <dict with {len(value)} keys>")
                        elif isinstance(value, list):
                            print(f"{key:<25} <list with {len(value)} items>")
                        else:
                            str_value = str(value)[:45] + "..." if len(str(value)) > 45 else str(value)
                            print(f"{key:<25} {str_value:<50}")
                
                # Deep dive into nested structures
                if mlb_plays:
                    sample_play = mlb_plays[0]
                    
                    print(f"\n--- MLB NESTED STRUCTURE DEEP DIVE ---")
                    
                    # Participants (batters, pitchers, etc.)
                    participants = sample_play.get('participants', [])
                    if participants:
                        print(f"\nPARTICIPANTS ({len(participants)} found):")
                        for p in participants[:2]:  # Show first 2
                            print(f"  Participant fields: {list(p.keys())}")
                            if 'athlete' in p:
                                athlete = p['athlete']
                                print(f"    Athlete fields: {list(athlete.keys())}")
                    
                    # Play details
                    if 'period' in sample_play:
                        print(f"\nPERIOD structure: {sample_play['period']}")
                    
                    if 'team' in sample_play:
                        print(f"\nTEAM structure: {sample_play['team']}")
                    
                    # Look for baseball-specific fields
                    baseball_fields = ['atBat', 'batting', 'pitching', 'count', 'bases', 'outs', 'innings']
                    print(f"\nBASEBALL-SPECIFIC FIELDS:")
                    for field in baseball_fields:
                        if field in sample_play:
                            print(f"  {field}: {sample_play[field]}")
            
            else:
                print("No MLB plays found in this game")
        else:
            print("No MLB games found today")
    
    except Exception as e:
        print(f"Error analyzing MLB: {e}")
    
    # === NFL ANALYSIS ===
    print("\n" + "=" * 40)
    print("NFL PLAY DATA ANALYSIS")
    print("=" * 40)
    
    try:
        nfl_scores = ApiService.get_scores('NFL', datetime.now())
        if nfl_scores:
            nfl_game_id = nfl_scores[0].get('id')
            print(f"Analyzing NFL game: {nfl_scores[0].get('name', 'Unknown')}")
            print(f"Game ID: {nfl_game_id}")
            
            nfl_details = ApiService.get_game_details('NFL', nfl_game_id)
            
            # Analyze drives structure
            drives_data = nfl_details.get('drives', {})
            print(f"\n--- NFL DRIVES STRUCTURE ---")
            print(f"Current drive exists: {'current' in drives_data}")
            print(f"Previous drives count: {len(drives_data.get('previous', []))}")
            
            if 'current' in drives_data:
                current_drive = drives_data['current']
                print(f"\nCURRENT DRIVE - ALL FIELDS:")
                print(f"{'Field':<25} {'Value':<50}")
                print("-" * 75)
                for key, value in current_drive.items():
                    if isinstance(value, dict):
                        print(f"{key:<25} <dict with {len(value)} keys>")
                    elif isinstance(value, list):
                        print(f"{key:<25} <list with {len(value)} items>")
                    else:
                        str_value = str(value)[:45] + "..." if len(str(value)) > 45 else str(value)
                        print(f"{key:<25} {str_value:<50}")
            
            # Analyze individual plays within drives
            all_drives = []
            if 'current' in drives_data:
                all_drives.append(drives_data['current'])
            all_drives.extend(drives_data.get('previous', []))
            
            if all_drives:
                sample_drive = all_drives[0]
                plays = sample_drive.get('plays', [])
                
                if plays:
                    print(f"\n--- NFL PLAY STRUCTURE ANALYSIS ---")
                    print(f"Analyzing {len(plays)} plays from sample drive")
                    
                    for i, play in enumerate(plays[:3]):
                        print(f"\nNFL Play {i+1} - ALL AVAILABLE FIELDS:")
                        print(f"{'Field':<25} {'Value':<50}")
                        print("-" * 75)
                        
                        for key, value in play.items():
                            if isinstance(value, dict):
                                print(f"{key:<25} <dict with {len(value)} keys>")
                            elif isinstance(value, list):
                                print(f"{key:<25} <list with {len(value)} items>")
                            else:
                                str_value = str(value)[:45] + "..." if len(str(value)) > 45 else str(value)
                                print(f"{key:<25} {str_value:<50}")
                    
                    # Deep dive into nested structures
                    sample_play = plays[0]
                    
                    print(f"\n--- NFL NESTED STRUCTURE DEEP DIVE ---")
                    
                    # Start/End details
                    if 'start' in sample_play:
                        start = sample_play['start']
                        print(f"\nSTART structure fields: {list(start.keys())}")
                        for key, value in start.items():
                            print(f"  start.{key}: {value}")
                    
                    if 'end' in sample_play:
                        end = sample_play['end']
                        print(f"\nEND structure fields: {list(end.keys())}")
                        for key, value in end.items():
                            print(f"  end.{key}: {value}")
                    
                    # Type information
                    if 'type' in sample_play:
                        play_type = sample_play['type']
                        print(f"\nTYPE structure: {play_type}")
                    
                    # Period/timing
                    if 'period' in sample_play:
                        print(f"\nPERIOD structure: {sample_play['period']}")
                    
                    if 'clock' in sample_play:
                        print(f"\nCLOCK structure: {sample_play['clock']}")
            
            # Check for regular plays structure (non-drives)
            nfl_plays = nfl_details.get('plays', [])
            if nfl_plays:
                print(f"\n--- NFL REGULAR PLAYS STRUCTURE ---")
                print(f"Found {len(nfl_plays)} regular plays (non-drives format)")
                sample_regular_play = nfl_plays[0]
                print(f"Regular play fields: {list(sample_regular_play.keys())}")
            
        else:
            print("No NFL games found today")
    
    except Exception as e:
        print(f"Error analyzing NFL: {e}")
    
    # === SUMMARY AND RECOMMENDATIONS ===
    print("\n" + "=" * 40)
    print("POTENTIAL ENHANCEMENTS SUMMARY")
    print("=" * 40)
    
    print("\nBased on available data, we could potentially add:")
    print("\nMLB Enhancements:")
    print("- Batter/pitcher detailed stats and info")
    print("- Ball/strike count details")
    print("- Base runner information")
    print("- Fielding positions and assists")
    print("- Pitch type, speed, location details")
    print("- At-bat context (RBI, runs scored, etc.)")
    
    print("\nNFL Enhancements:")
    print("- Player involvement details (rushers, receivers, tacklers)")
    print("- Formation information")
    print("- Penalty details and enforcement")
    print("- Weather/field conditions")
    print("- Drive efficiency stats")
    print("- Red zone/goal line context")
    print("- Time of possession details")
    
    print("\nBoth Sports:")
    print("- Win probability changes")
    print("- Leverage index or clutch situations")
    print("- Historical context (career stats, season stats)")
    print("- Video/highlight links")
    print("- Advanced analytics and metrics")

if __name__ == "__main__":
    analyze_all_play_data()
