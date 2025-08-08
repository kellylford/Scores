from services.api_service import ApiService
from datetime import datetime, timedelta

# Try to find a completed game
for days_back in range(1, 8):  # Check last week
    date = datetime.now() - timedelta(days=days_back)
    print(f"\nChecking {days_back} days ago ({date.strftime('%Y-%m-%d')}):")
    
    try:
        scores = ApiService.get_scores('MLB', date)
        print(f"  Found {len(scores)} games")
        
        if scores:
            # Get first game and check its details
            first_game = scores[0]
            game_id = first_game.get('id')
            
            if game_id:
                print(f"  Checking game {game_id}")
                details = ApiService.get_game_details('MLB', game_id)
                
                boxscore = details.get('boxscore', {})
                if boxscore and 'players' in boxscore:
                    players = boxscore['players']
                    if len(players) > 0:
                        # Check first team's pitching
                        first_team = players[0]
                        stats_groups = first_team.get('statistics', [])
                        
                        for group in stats_groups:
                            if group.get('type') == 'pitching':
                                athletes = group.get('athletes', [])
                                print(f"    Team 1 pitchers: {len(athletes)}")
                                
                                non_zero_pitchers = 0
                                for athlete in athletes:
                                    stats = athlete.get('stats', [])
                                    # Check if they have meaningful stats (not all zeros/dashes)
                                    if stats and any(stat not in ['0', '0.0', '--', '--.--', ''] for stat in stats):
                                        non_zero_pitchers += 1
                                        player_name = athlete.get('athlete', {}).get('displayName', 'Unknown')
                                        print(f"      {player_name}: {stats[:3]}")
                                
                                print(f"    Pitchers with stats: {non_zero_pitchers}")
                                if non_zero_pitchers > 1:
                                    print(f"  *** FOUND GAME WITH MULTIPLE PITCHERS: {game_id} ***")
                                    exit()
                                break
                break
    except Exception as e:
        print(f"  Error: {e}")
        
print("\nNo games found with multiple active pitchers in the last week.")
