#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import espn_api

def test_new_mlb_statistics():
    """Test the new MLB statistics integration"""
    print("Testing new MLB statistics with official MLB API...")
    
    result = espn_api.get_statistics("MLB")
    
    print(f"\nResult keys: {list(result.keys())}")
    print(f"Player stats count: {len(result.get('player_stats', []))}")
    print(f"Team stats count: {len(result.get('team_stats', []))}")
    
    # Check a few key statistics
    player_stats = result.get('player_stats', [])
    
    for stat in player_stats:
        if stat['name'] in ['Home Runs', 'Wins', 'RBIs']:
            leaders = stat.get('leaders', [])
            if leaders:
                top_leader = leaders[0]
                print(f"\n{stat['name']}:")
                print(f"  Leader: {top_leader['name']} ({top_leader['team']}) = {top_leader['value']}")
                
                # Check if these are season values vs recent performance
                if stat['name'] == 'Home Runs' and float(top_leader['value']) > 30:
                    print(f"  🎯 SEASON DATA: {top_leader['value']} HRs (vs ~4 from ESPN)")
                elif stat['name'] == 'Wins' and float(top_leader['value']) > 10:
                    print(f"  🎯 SEASON DATA: {top_leader['value']} wins (vs ~4 from ESPN)")
                elif stat['name'] == 'RBIs' and float(top_leader['value']) > 80:
                    print(f"  🎯 SEASON DATA: {top_leader['value']} RBIs (vs ~20 from ESPN)")

if __name__ == "__main__":
    test_new_mlb_statistics()
