import requests
import json

# Try to find division standings using different endpoints
endpoints = [
    'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/standings',
    'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/standings/groups'
]

for url in endpoints:
    print(f"\n--- Checking {url} ---")
    try:
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print("Top-level keys:", list(data.keys()))
            
            # Look for division/conference structure
            if 'children' in data:
                print(f"Found {len(data['children'])} children (likely divisions)")
                for i, child in enumerate(data['children'][:3]):
                    print(f"Child {i}: {child.get('name', 'No name')}")
                    if 'standings' in child:
                        print(f"  Has standings with {len(child['standings'].get('entries', []))} teams")
            
            if 'groups' in data:
                print("Groups found:", data['groups'])
                
    except Exception as e:
        print(f"Error: {e}")

# Also try the groups endpoint directly
print("\n--- Checking groups endpoint ---")
try:
    resp = requests.get('https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/groups')
    print(f"Groups status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("Groups data keys:", list(data.keys()))
except Exception as e:
    print(f"Groups error: {e}")
