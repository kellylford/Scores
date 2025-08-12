import espn_api

standings = espn_api.get_standings('MLB')
print(f'Found {len(standings)} teams')
print('First few teams by division:')

for i, team in enumerate(standings[:10]):
    print(f'{i+1}. {team["team_name"]} ({team["abbreviation"]}) - {team["division"]} - {team["wins"]}-{team["losses"]} ({team["games_back"]} GB)')
