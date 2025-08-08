import json

# Load the game data
with open('api_exploration/game_details_401696639.json', 'r') as f:
    data = json.load(f)

# Examine team stats structure
teams = data['boxscore']['teams']
print(f"Number of teams: {len(teams)}")

for team_idx, team in enumerate(teams):
    print(f"\nTeam {team_idx + 1}:")
    print(f"  Team name: {team.get('team', {}).get('displayName', 'Unknown')}")
    
    stats_groups = team.get('statistics', [])
    print(f"  Stats groups: {len(stats_groups)}")
    
    for group_idx, group in enumerate(stats_groups):
        print(f"    Group {group_idx + 1}:")
        print(f"      Name: {group.get('name', 'N/A')}")
        print(f"      Display Name: {group.get('displayName', 'N/A')}")
        
        stats = group.get('stats', [])
        print(f"      Stats count: {len(stats)}")
        if stats:
            print(f"      First stat: {stats[0]}")
            print(f"      Stats structure keys: {list(stats[0].keys()) if stats[0] else 'None'}")
        break  # Just show first group
    break  # Just show first team
