from services.api_service import ApiService
from datetime import datetime, timedelta
import json

# Get games from 5 days ago
wed = datetime.now() - timedelta(days=5)
scores = ApiService.get_scores('MLB', wed)

# Find Brewers game
brewers_game = None
for game in scores:
    game_str = str(game).lower()
    if 'brewers' in game_str or 'milwaukee' in game_str:
        brewers_game = game
        break

if brewers_game:
    print("Found Brewers game:")
    print(f"Game ID: {brewers_game.get('id')}")
    print(f"Teams: {brewers_game.get('competitions', [{}])[0].get('competitors', [])}")
    
    # Get detailed game data
    game_id = brewers_game.get('id')
    if game_id:
        details = ApiService.get_game_details('MLB', game_id)
        
        # Check if there's boxscore data
        boxscore = details.get('boxscore', {})
        if boxscore:
            teams = boxscore.get('teams', [])
            print(f"\nBoxscore teams: {len(teams)}")
            
            for i, team in enumerate(teams):
                team_name = team.get('team', {}).get('displayName', f'Team {i+1}')
                print(f"\n{team_name}:")
                
                stats_groups = team.get('statistics', [])
                print(f"  Stats groups: {len(stats_groups)}")
                
                for j, group in enumerate(stats_groups):
                    group_name = group.get('displayName', group.get('name', 'Unknown'))
                    stats = group.get('stats', [])
                    print(f"    Group {j+1}: {group_name} ({len(stats)} stats)")
                    
                    # Look for runs scored
                    for stat in stats:
                        stat_name = stat.get('name', '').lower()
                        if 'run' in stat_name and 'scored' in stat_name:
                            print(f"      RUNS SCORED: {stat.get('displayValue', 'N/A')}")
                        elif 'run' in stat_name:
                            print(f"      {stat.get('displayName', stat_name)}: {stat.get('displayValue', 'N/A')}")
        else:
            print("No boxscore data found")
else:
    print("No Brewers game found")
