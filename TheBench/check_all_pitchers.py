import json

# Load a known game and check ALL pitchers
with open('api_exploration/game_details_401696639.json', 'r') as f:
    data = json.load(f)

players = data['boxscore']['players']

for team_idx, team in enumerate(players):
    team_name = team.get('team', {}).get('displayName', f'Team {team_idx+1}')
    print(f"\n{team_name}:")
    
    stats_groups = team.get('statistics', [])
    
    for group in stats_groups:
        stat_type = group.get('type', 'unknown')
        if stat_type == 'pitching':
            athletes = group.get('athletes', [])
            print(f"  Pitching stats - Total athletes: {len(athletes)}")
            
            for i, athlete in enumerate(athletes):
                active = athlete.get('active', True)
                player_info = athlete.get('athlete', {})
                name = player_info.get('displayName', 'Unknown')
                pos = player_info.get('position', {}).get('abbreviation', 'N/A')
                stats = athlete.get('stats', [])
                
                print(f"    {i+1}. {name} ({pos}) - Active: {active} - Stats: {len(stats)} values")
                if len(stats) > 0:
                    print(f"        First few stats: {stats[:3]}")
                    
                # Check if there are innings pitched
                stat_names = group.get('names', [])
                if 'IP' in stat_names:
                    ip_index = stat_names.index('IP')
                    if ip_index < len(stats):
                        ip_value = stats[ip_index] if stats[ip_index] != '0' else '0.0'
                        print(f"        Innings Pitched: {ip_value}")
