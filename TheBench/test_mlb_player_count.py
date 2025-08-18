#!/usr/bin/env python3
"""Test MLB API with increased player limit"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from espn_api import _get_mlb_statistics

def test_mlb_player_count():
    print("Testing MLB player count after limit fix...")
    
    try:
        mlb_stats = _get_mlb_statistics()
        
        if mlb_stats and 'player_stats' in mlb_stats:
            categories = mlb_stats['player_stats']
            print(f"\nTotal categories loaded: {len(categories)}")
            
            # Check a few categories to see player counts
            for i, category in enumerate(categories[:3]):  # Check first 3 categories
                leaders = category.get('leaders', [])
                category_name = category.get('display_name', f'Category {i+1}')
                print(f"\n{category_name}:")
                print(f"  Players returned: {len(leaders)}")
                
                # Show first 5 and last 5 players to verify we have more than 5
                if len(leaders) > 10:
                    print("  First 5 players:")
                    for j, leader in enumerate(leaders[:5]):
                        print(f"    {j+1}. {leader['name']} ({leader['team']}) - {leader['value']}")
                    print("  ...")
                    print("  Last 5 players:")
                    for j, leader in enumerate(leaders[-5:], len(leaders)-4):
                        print(f"    {j}. {leader['name']} ({leader['team']}) - {leader['value']}")
                else:
                    print("  All players:")
                    for j, leader in enumerate(leaders):
                        print(f"    {j+1}. {leader['name']} ({leader['team']}) - {leader['value']}")
                
                if len(leaders) > 5:
                    print(f"  ✅ SUCCESS: Got {len(leaders)} players (more than 5!)")
                else:
                    print(f"  ❌ ISSUE: Only got {len(leaders)} players")
            
        else:
            print("❌ No MLB stats data returned")
            
    except Exception as e:
        print(f"❌ Error testing MLB player count: {e}")

if __name__ == "__main__":
    test_mlb_player_count()
