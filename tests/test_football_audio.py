"""
Test the football audio mapper with real NFL game data
"""

import requests
import json
from football_audio_mapper import FootballAudioMapper, FootballDrivePlayer

def fetch_nfl_game_data(game_id: str):
    """Fetch play-by-play data for an NFL game"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def analyze_game_audio(game_id: str, max_drives: int = 3):
    """
    Fetch and analyze audio for an NFL game
    
    Args:
        game_id: ESPN game ID
        max_drives: Maximum number of drives to analyze (for demo purposes)
    """
    print("Fetching NFL game data...")
    data = fetch_nfl_game_data(game_id)
    
    if not data:
        print("Failed to fetch game data")
        return
    
    # Get game info
    header = data.get('header', {})
    competition = header.get('competitions', [{}])[0]
    competitors = competition.get('competitors', [])
    
    home_team = next((c for c in competitors if c.get('homeAway') == 'home'), {})
    away_team = next((c for c in competitors if c.get('homeAway') == 'away'), {})
    
    home_name = home_team.get('team', {}).get('displayName', 'Home')
    away_name = away_team.get('team', {}).get('displayName', 'Away')
    home_score = home_team.get('score', 0)
    away_score = away_team.get('score', 0)
    
    print(f"\n{'='*70}")
    print(f"Game: {away_name} @ {home_name}")
    print(f"Score: {away_name} {away_score}, {home_name} {home_score}")
    print(f"{'='*70}\n")
    
    # Get drives
    drives_data = data.get('drives', {})
    previous_drives = drives_data.get('previous', [])
    
    if not previous_drives:
        print("No drive data available")
        return
    
    print(f"Total drives in game: {len(previous_drives)}")
    print(f"Analyzing first {min(max_drives, len(previous_drives))} drives...\n")
    
    mapper = FootballAudioMapper()
    player = FootballDrivePlayer()
    
    # Analyze each drive
    for i, drive in enumerate(previous_drives[:max_drives], 1):
        team = drive.get('team', {})
        team_name = team.get('displayName', 'Unknown')
        team_abbr = team.get('abbreviation', '???')
        
        plays = drive.get('plays', [])
        
        # Handle result - can be string or dict
        result_data = drive.get('result', 'No result')
        if isinstance(result_data, dict):
            result = result_data.get('text', 'No result')
        else:
            result = str(result_data)
        
        start_pos = drive.get('start', {}).get('yardLine', 0)
        end_pos = drive.get('end', {}).get('yardLine', 0)
        
        print(f"\n{'-'*70}")
        print(f"DRIVE #{i}: {team_name} ({team_abbr})")
        print(f"Result: {result}")
        print(f"Field Position: {start_pos} -> {end_pos}")
        print(f"{'-'*70}")
        
        # Get audio summary
        summary = mapper.get_drive_summary(drive)
        print(f"\nDrive Stats:")
        print(f"  Plays: {summary['total_plays']}")
        print(f"  Rushes: {summary['rushes']}, Passes: {summary['passes']}")
        print(f"  Total Yards: {summary['total_yards']}")
        print(f"  Scoring: {'Yes' if summary['scoring'] else 'No'}")
        print(f"  Audio Duration: {summary['duration_estimate']:.1f} seconds")
        
        # Show individual plays with audio mapping
        print(f"\nPlay-by-Play Audio Mapping:")
        audio_sequence = mapper.map_drive_to_audio_sequence(drive)
        
        play_count = 0
        for play in plays:
            # Skip timeouts and penalties
            play_type = play.get('type', {}).get('text', '')
            if 'timeout' in play_type.lower() or 'penalty' in play_type.lower():
                continue
            
            if play_count >= len(audio_sequence):
                break
                
            config = audio_sequence[play_count]
            play_count += 1
            
            yardage = play.get('statYardage', 0)
            text = play.get('text', '')
            
            # Truncate long play descriptions
            if len(text) > 65:
                text = text[:62] + '...'
            
            # Format with audio info
            wave_symbol = {
                'sine': '~',
                'square': '^',
                'sawtooth': '/',
                'triangle': 'v'
            }.get(config.wave_type, '*')
            
            print(f"  {wave_symbol} {yardage:+3d}yd | {config.frequency:6.1f}Hz | {text}")
        
        # Calculate interesting plays
        if summary['scoring']:
            print(f"\n  ** TOUCHDOWN DRIVE - Ends with celebration tone!")
        elif summary['total_yards'] >= 50:
            print(f"\n  ** BIG YARDAGE DRIVE - Rich harmonic progression!")
        
        print()

def find_big_plays(game_id: str, min_yards: int = 25):
    """Find and display all big plays from a game"""
    print(f"Fetching big plays ({min_yards}+ yards)...")
    data = fetch_nfl_game_data(game_id)
    
    if not data:
        print("Failed to fetch game data")
        return
    
    drives = data.get('drives', {}).get('previous', [])
    mapper = FootballAudioMapper()
    
    big_plays = mapper.get_interesting_plays(drives, min_yards=min_yards)
    
    print(f"\n{'='*70}")
    print(f"BIG PLAYS (Highlight Reel)")
    print(f"{'='*70}\n")
    
    for i, play in enumerate(big_plays, 1):
        config = mapper.map_play_to_audio(play)
        yardage = play.get('statYardage', 0)
        play_type = play.get('type', {}).get('text', 'Play')
        text = play.get('text', '')
        is_scoring = play.get('scoringPlay', False)
        
        if len(text) > 60:
            text = text[:57] + '...'
        
        score_marker = "[TD!] " if is_scoring else ""
        print(f"{i:2d}. {score_marker}{yardage:+3d} yards | {config.frequency:.0f}Hz {config.wave_type}")
        print(f"    {play_type}: {text}\n")

if __name__ == "__main__":
    # Use the completed Vikings @ Chargers game from earlier
    GAME_ID = "401772942"
    
    print("NFL Football Audio Analysis")
    print("="*70)
    
    # Analyze drives with audio mapping
    analyze_game_audio(GAME_ID, max_drives=5)
    
    print("\n" + "="*70)
    
    # Show big plays
    find_big_plays(GAME_ID, min_yards=20)
