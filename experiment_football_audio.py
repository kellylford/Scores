"""
Interactive Football Audio Experimentation Tool

Run this to experiment with different audio mappings for NFL plays.
You can test different games, drives, and audio parameters.
"""

import requests
from football_audio_mapper import FootballAudioMapper, FootballDrivePlayer
from audio_player import AudioPlayer

def fetch_recent_nfl_games():
    """Fetch recent NFL games"""
    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        events = data.get('events', [])
        return events
    return []

def fetch_game_summary(game_id):
    """Fetch detailed game data"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def show_game_menu():
    """Show available games to experiment with"""
    print("\n" + "="*70)
    print("FOOTBALL AUDIO EXPERIMENTATION LAB")
    print("="*70)
    print("\nFetching recent NFL games...\n")
    
    games = fetch_recent_nfl_games()
    
    if not games:
        print("No games found. Using default game ID.")
        return "401772942"  # Vikings @ Chargers
    
    completed_games = []
    for game in games:
        status = game.get('status', {}).get('type', {})
        if status.get('completed', False):
            competition = game.get('competitions', [{}])[0]
            competitors = competition.get('competitors', [])
            
            home = next((c for c in competitors if c.get('homeAway') == 'home'), {})
            away = next((c for c in competitors if c.get('homeAway') == 'away'), {})
            
            home_name = home.get('team', {}).get('abbreviation', 'HOME')
            away_name = away.get('team', {}).get('abbreviation', 'AWAY')
            home_score = home.get('score', '0')
            away_score = away.get('score', '0')
            
            completed_games.append({
                'id': game.get('id'),
                'name': f"{away_name} {away_score} @ {home_name} {home_score}",
                'home': home_name,
                'away': away_name
            })
    
    if not completed_games:
        print("No completed games found. Using default.")
        return "401772942"
    
    print("Select a game to experiment with:\n")
    for i, game in enumerate(completed_games[:10], 1):
        print(f"  {i}. {game['name']}")
    
    print(f"\n  0. Use default game (Vikings @ Chargers)")
    
    while True:
        try:
            choice = input("\nEnter game number: ").strip()
            if choice == '0':
                return "401772942"
            choice_num = int(choice)
            if 1 <= choice_num <= len(completed_games):
                return completed_games[choice_num - 1]['id']
        except (ValueError, KeyError):
            pass
        print("Invalid choice. Try again.")

def show_drive_menu(data):
    """Show drives from the game"""
    drives = data.get('drives', {}).get('previous', [])
    
    print("\n" + "="*70)
    print("DRIVES IN THIS GAME")
    print("="*70 + "\n")
    
    drive_info = []
    for i, drive in enumerate(drives, 1):
        team = drive.get('team', {})
        team_name = team.get('abbreviation', '???')
        
        plays = drive.get('plays', [])
        
        result_data = drive.get('result', 'Unknown')
        if isinstance(result_data, dict):
            result = result_data.get('text', 'Unknown')
        else:
            result = str(result_data)
        
        # Calculate yards
        yards = sum(p.get('statYardage', 0) for p in plays)
        
        drive_info.append({
            'num': i,
            'team': team_name,
            'plays': len(plays),
            'yards': yards,
            'result': result,
            'drive': drive
        })
        
        print(f"  {i:2d}. {team_name:5s} | {len(plays):2d} plays | {yards:+4d} yds | {result}")
    
    print(f"\n  TD = Scoring drives (touchdowns/field goals)")
    print(f"  FG = Field goal drives")
    print(f"  PUNT = Punts")
    
    return drive_info

def play_drive_audio(drive_info, mapper, player):
    """Show what the drive sounds like"""
    drive = drive_info['drive']
    team = drive_info['team']
    
    print("\n" + "-"*70)
    print(f"DRIVE AUDIO ANALYSIS: {team}")
    print("-"*70 + "\n")
    
    # Get summary
    summary = mapper.get_drive_summary(drive)
    print(f"Stats:")
    print(f"  Total plays: {summary['total_plays']}")
    print(f"  Rushes: {summary['rushes']}, Passes: {summary['passes']}")
    print(f"  Total yards: {summary['total_yards']}")
    print(f"  Result: {summary['result']}")
    print(f"  Audio duration: {summary['duration_estimate']:.1f} seconds\n")
    
    # Get audio sequence
    audio_sequence = mapper.map_drive_to_audio_sequence(drive)
    
    print("Audio Sequence (play by play):\n")
    
    plays = [p for p in drive.get('plays', []) 
             if 'timeout' not in p.get('type', {}).get('text', '').lower()
             and 'penalty' not in p.get('type', {}).get('text', '').lower()]
    
    # Extract field positions for stereo
    field_positions = []
    for i, (play, config) in enumerate(zip(plays, audio_sequence), 1):
        yardage = play.get('statYardage', 0)
        play_type = play.get('type', {}).get('text', 'Play')
        text = play.get('text', '')
        
        # Get field position
        field_pos = play.get('start', {}).get('yardLine', 50)
        field_positions.append(field_pos)
        
        if len(text) > 50:
            text = text[:47] + '...'
        
        # Visual representation of frequency
        freq_bar = '=' * int(config.frequency / 50)
        
        # Show field position
        print(f"  {i:2d}. Yd {field_pos:3d} | {yardage:+3d}yd | {config.frequency:6.1f}Hz {config.wave_type:8s} | {config.duration:.2f}s")
        print(f"      {freq_bar}")
        print(f"      {text}\n")
    
    print(f"\nTotal audio duration: {sum(c.duration for c in audio_sequence):.2f} seconds")
    
    # Show if it's interesting
    if summary['scoring']:
        print("\n*** SCORING DRIVE - Ends with high celebration tone! ***")
    elif summary['total_yards'] >= 60:
        print("\n*** BIG YARDAGE DRIVE - Wide frequency range! ***")
    
    # Offer to play audio
    print("\n" + "-"*70)
    print("STEREO PLAYBACK: Use headphones to hear field position!")
    print("Sound moves left-to-right as the team advances down the field.")
    choice = input("Play this drive audio? (y/n): ").strip().lower()
    if choice == 'y':
        player.play_audio_sequence(audio_sequence, silence_between=0.15, 
                                   field_positions=field_positions)
        print()
    else:
        print("Skipping playback.\n")

def compare_two_drives(drive_info_list, indices, mapper):
    """Compare audio characteristics of two drives"""
    if len(indices) != 2:
        print("Need exactly 2 drives to compare")
        return
    
    drive1_info = drive_info_list[indices[0] - 1]
    drive2_info = drive_info_list[indices[1] - 1]
    
    print("\n" + "="*70)
    print("DRIVE COMPARISON")
    print("="*70 + "\n")
    
    for idx, drive_info in enumerate([drive1_info, drive2_info], 1):
        drive = drive_info['drive']
        team = drive_info['team']
        summary = mapper.get_drive_summary(drive)
        audio_seq = mapper.map_drive_to_audio_sequence(drive)
        
        avg_freq = sum(c.frequency for c in audio_seq) / len(audio_seq) if audio_seq else 0
        max_freq = max((c.frequency for c in audio_seq), default=0)
        min_freq = min((c.frequency for c in audio_seq if c.frequency > 0), default=0)
        
        print(f"Drive {idx}: {team} (Drive #{drive_info['num']})")
        print(f"  Plays: {summary['total_plays']}")
        print(f"  Yards: {summary['total_yards']}")
        print(f"  Result: {summary['result']}")
        print(f"  Audio duration: {summary['duration_estimate']:.1f}s")
        print(f"  Frequency range: {min_freq:.0f}Hz - {max_freq:.0f}Hz")
        print(f"  Average frequency: {avg_freq:.0f}Hz")
        print(f"  Scoring: {'Yes' if summary['scoring'] else 'No'}\n")

def show_big_plays(data, mapper, min_yards=20):
    """Show all big plays from the game"""
    drives = data.get('drives', {}).get('previous', [])
    big_plays = mapper.get_interesting_plays(drives, min_yards=min_yards)
    
    print("\n" + "="*70)
    print(f"BIG PLAYS (Highlight Reel - {min_yards}+ yards)")
    print("="*70 + "\n")
    
    audio_configs = []  # Store configs for playback
    field_positions = []  # Store field positions for stereo
    
    for i, play in enumerate(big_plays, 1):
        config = mapper.map_play_to_audio(play)
        audio_configs.append(config)
        
        # Get field position
        field_pos = play.get('start', {}).get('yardLine', 50)
        field_positions.append(field_pos)
        
        yardage = play.get('statYardage', 0)
        play_type = play.get('type', {}).get('text', 'Play')
        text = play.get('text', '')
        is_scoring = play.get('scoringPlay', False)
        
        if len(text) > 55:
            text = text[:52] + '...'
        
        score_marker = "[TD] " if is_scoring else "     "
        freq_bar = '|' * int(config.frequency / 100)
        
        print(f"{i:2d}. {score_marker}Yd {field_pos:3d} | {yardage:+3d}yd | {config.frequency:6.0f}Hz {config.wave_type:8s}")
        print(f"    {freq_bar}")
        print(f"    {play_type}: {text}\n")
    
    # Offer to play all big plays
    print("\n" + "-"*70)
    print("STEREO PLAYBACK: Hear big plays from their field positions!")
    choice = input("Play all big plays as audio sequence? (y/n): ").strip().lower()
    if choice == 'y':
        from audio_player import AudioPlayer
        player = AudioPlayer()
        player.play_audio_sequence(audio_configs, silence_between=0.2, 
                                   field_positions=field_positions)
        print()
    else:
        print("Skipping playback.\n")

def experiment_with_parameters(drive_info, mapper):
    """Let user experiment with different audio parameters"""
    print("\n" + "="*70)
    print("EXPERIMENT WITH AUDIO PARAMETERS")
    print("="*70 + "\n")
    
    print("Current settings:")
    print(f"  Base duration: {mapper.base_duration} seconds")
    print(f"  Base volume: {mapper.base_volume}")
    print()
    
    # Show current mapping
    print("Frequency mapping:")
    print(f"  40+ yards:     {mapper.FREQ_TOUCHDOWN:.0f}Hz (Touchdown celebration)")
    print(f"  20-39 yards:   {mapper.FREQ_BIG_GAIN:.0f}Hz (Big play)")
    print(f"  10-19 yards:   {mapper.FREQ_FIRST_DOWN:.0f}Hz (First down)")
    print(f"  5-9 yards:     {mapper.FREQ_GOOD_GAIN:.0f}Hz (Good gain)")
    print(f"  1-4 yards:     {mapper.FREQ_SHORT_GAIN:.0f}Hz (Short gain)")
    print(f"  0 yards:       {mapper.FREQ_NO_GAIN:.0f}Hz (No gain)")
    print(f"  Negative:      {mapper.FREQ_LOSS:.0f}Hz (Loss)")
    print()
    
    while True:
        print("What would you like to try?")
        print("  1. Change base duration")
        print("  2. Change base volume")
        print("  3. See this drive with current settings")
        print("  4. Back to main menu")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            try:
                new_duration = float(input("New base duration (seconds, e.g., 0.5): "))
                mapper.base_duration = new_duration
                print(f"Base duration set to {new_duration}s")
            except ValueError:
                print("Invalid number")
        
        elif choice == '2':
            try:
                new_volume = float(input("New base volume (0.0-1.0, e.g., 0.7): "))
                mapper.base_volume = max(0.0, min(1.0, new_volume))
                print(f"Base volume set to {mapper.base_volume}")
            except ValueError:
                print("Invalid number")
        
        elif choice == '3':
            play_drive_audio(drive_info, mapper, None)
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            break

def main():
    """Main interactive loop"""
    # Get a game
    game_id = show_game_menu()
    
    print(f"\nFetching game data for ID: {game_id}...")
    data = fetch_game_summary(game_id)
    
    if not data:
        print("Failed to fetch game data. Exiting.")
        return
    
    # Get game info
    header = data.get('header', {})
    competition = header.get('competitions', [{}])[0]
    competitors = competition.get('competitors', [])
    
    home = next((c for c in competitors if c.get('homeAway') == 'home'), {})
    away = next((c for c in competitors if c.get('homeAway') == 'away'), {})
    
    home_name = home.get('team', {}).get('displayName', 'Home')
    away_name = away.get('team', {}).get('displayName', 'Away')
    home_score = home.get('score', 0)
    away_score = away.get('score', 0)
    
    print(f"\n{'='*70}")
    print(f"Game: {away_name} @ {home_name}")
    print(f"Final Score: {away_name} {away_score}, {home_name} {home_score}")
    print(f"{'='*70}")
    
    mapper = FootballAudioMapper()
    player = AudioPlayer()  # Audio player for sound generation
    drive_player = FootballDrivePlayer()
    
    # Main menu loop
    while True:
        print("\n" + "="*70)
        print("WHAT WOULD YOU LIKE TO DO?")
        print("="*70)
        print("\n  1. View all drives and pick one to analyze")
        print("  2. Show big plays (highlight reel)")
        print("  3. Compare two drives")
        print("  4. Experiment with audio parameters")
        print("  5. Pick a different game")
        print("  6. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            drive_info_list = show_drive_menu(data)
            
            while True:
                try:
                    drive_choice = input("\nPick a drive number (or 'b' to go back): ").strip()
                    if drive_choice.lower() == 'b':
                        break
                    
                    drive_num = int(drive_choice)
                    if 1 <= drive_num <= len(drive_info_list):
                        play_drive_audio(drive_info_list[drive_num - 1], mapper, player)
                        input("\nPress Enter to continue...")
                    else:
                        print("Invalid drive number")
                except ValueError:
                    print("Invalid input")
        
        elif choice == '2':
            while True:
                try:
                    min_yards = input("\nMinimum yards for 'big play' (default 20, or 'b' to go back): ").strip()
                    if min_yards.lower() == 'b':
                        break
                    
                    yards = int(min_yards) if min_yards else 20
                    show_big_plays(data, mapper, min_yards=yards)
                    input("\nPress Enter to continue...")
                    break
                except ValueError:
                    print("Invalid number")
        
        elif choice == '3':
            drive_info_list = show_drive_menu(data)
            
            try:
                drives_input = input("\nEnter two drive numbers separated by space (e.g., '1 3'): ").strip()
                indices = [int(x) for x in drives_input.split()]
                compare_two_drives(drive_info_list, indices, mapper)
                input("\nPress Enter to continue...")
            except (ValueError, IndexError):
                print("Invalid input")
        
        elif choice == '4':
            drive_info_list = show_drive_menu(data)
            
            try:
                drive_num = int(input("\nPick a drive to experiment with: ").strip())
                if 1 <= drive_num <= len(drive_info_list):
                    experiment_with_parameters(drive_info_list[drive_num - 1], mapper)
            except (ValueError, IndexError):
                print("Invalid input")
        
        elif choice == '5':
            game_id = show_game_menu()
            print(f"\nFetching new game data...")
            data = fetch_game_summary(game_id)
            if not data:
                print("Failed to fetch game data.")
                return
        
        elif choice == '6':
            print("\nThanks for experimenting! 🏈")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
