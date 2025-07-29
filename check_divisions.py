import requests
import json

# Check for division/conference info in teams API
resp = requests.get('https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams')
data = resp.json()

teams = data['sports'][0]['leagues'][0]['teams']
first_team = teams[0]['team']

print("Team keys:", list(first_team.keys()))

# Check if there's any division/conference info
if 'groups' in first_team:
    print("Groups found:", first_team['groups'])

# Check for divisions at league level
league = data['sports'][0]['leagues'][0]
print("League keys:", list(league.keys()))

if 'groups' in league:
    print("League groups:", league['groups'])

# Also check the scoreboard for any division info
print("\n--- Checking scoreboard ---")
scoreboard_resp = requests.get('https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard')
scoreboard_data = scoreboard_resp.json()

if 'leagues' in scoreboard_data:
    print("Scoreboard leagues:", scoreboard_data['leagues'])
