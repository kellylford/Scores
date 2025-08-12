import json

# Load the game data
with open('api_exploration/game_details_401696639.json', 'r') as f:
    data = json.load(f)

# Check player statistics structure
players = data['boxscore']['players']
print(f"Teams with players: {len(players)}")

for i, team in enumerate(players):
    team_name = team.get('team', {}).get('displayName', f'Team {i+1}')
    print(f"\n{team_name}:")
    
    stats = team.get('statistics', [])
    print(f"  Stat groups: {len(stats)}")
    
    for j, stat_group in enumerate(stats):
        stat_type = stat_group.get('type', 'unknown')
        athletes = stat_group.get('athletes', [])
        active_athletes = [a for a in athletes if a.get('active', True)]
        
        print(f"  Group {j+1}: {stat_type}")
        print(f"    Total athletes: {len(athletes)}")
        print(f"    Active athletes: {len(active_athletes)}")
        
        if active_athletes:
            print(f"    First few players:")
            for k, athlete in enumerate(active_athletes[:3]):
                player_info = athlete.get('athlete', {})
                name = player_info.get('displayName', 'Unknown')
                pos = player_info.get('position', {}).get('abbreviation', 'N/A')
                print(f"      {k+1}. {name} ({pos})")
