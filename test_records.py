import requests
import json

# Test getting team records from scoreboard
resp = requests.get('https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard')
data = resp.json()

events = data.get('events', [])
if events:
    event = events[0]
    comp = event['competitions'][0]
    competitors = comp['competitors']
    
    print("First competitor:")
    competitor = competitors[0]
    print("Keys:", list(competitor.keys()))
    
    if 'records' in competitor:
        print("Records found:", competitor['records'])
    
    if 'team' in competitor:
        team_keys = list(competitor['team'].keys())
        print("Team keys:", team_keys[:10])
        
    # Check if there's record info anywhere
    print("\nFull competitor structure (truncated):")
    print(json.dumps(competitor, indent=2)[:1000])
