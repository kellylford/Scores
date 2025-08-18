#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

def analyze_current_data():
    """Analyze the current data to understand the time period"""
    print("DEBUG: Analyzing current ESPN data to understand time period...")
    
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            print("=== Current Data Analysis ===")
            season = data.get('season', {})
            print(f"Season: {season}")
            print(f"Timestamp: {data.get('timestamp')}")
            
            # Look at multiple categories to understand the data scope
            categories = data.get('stats', {}).get('categories', [])
            
            analysis_cats = ['wins', 'homeRuns', 'RBIs', 'avg']
            
            for cat_name in analysis_cats:
                for cat in categories:
                    if cat.get('name') == cat_name:
                        leaders = cat.get('leaders', [])
                        if leaders:
                            print(f"\n{cat.get('displayName', cat_name)} Leaders:")
                            for i, leader in enumerate(leaders[:5]):
                                player = leader.get('athlete', {}).get('displayName', 'Unknown')
                                team = leader.get('team', {}).get('abbreviation', 'Unknown')
                                value = leader.get('value', 0)
                                display = leader.get('displayValue', '')
                                
                                print(f"  {i+1}. {player} ({team}): {value}")
                                if display and display != str(value):
                                    print(f"     Display: {display}")
                        break
            
            # Check if this looks like partial season data
            print(f"\n=== Data Analysis ===")
            
            # Look at home runs - should be 30+ for leaders in August
            hr_cat = None
            for cat in categories:
                if cat.get('name') == 'homeRuns':
                    hr_cat = cat
                    break
            
            if hr_cat:
                leaders = hr_cat.get('leaders', [])
                if leaders:
                    top_hr = leaders[0].get('value', 0)
                    print(f"Top HR total: {top_hr}")
                    if top_hr < 20:
                        print("  ⚠️  This looks like partial/recent data (expected 25+ HRs in August)")
                    elif top_hr > 40:
                        print("  ✅ This looks like full season data")
                    else:
                        print("  🤔 This could be partial season or a down year")
            
            # Look at RBIs - should be 60+ for leaders in August  
            rbi_cat = None
            for cat in categories:
                if cat.get('name') == 'RBIs':
                    rbi_cat = cat
                    break
            
            if rbi_cat:
                leaders = rbi_cat.get('leaders', [])
                if leaders:
                    top_rbi = leaders[0].get('value', 0)
                    print(f"Top RBI total: {top_rbi}")
                    if top_rbi < 40:
                        print("  ⚠️  This looks like partial/recent data (expected 50+ RBIs in August)")
                    elif top_rbi > 80:
                        print("  ✅ This looks like full season data")
                    else:
                        print("  🤔 This could be partial season or a down year")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_current_data()
