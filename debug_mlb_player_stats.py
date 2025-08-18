#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import espn_api

def debug_mlb_player_stats():
    """Debug the MLB player statistics issue"""
    
    print("=== DEBUGGING MLB PLAYER STATISTICS ===\n")
    
    # Test the get_statistics function directly
    print("1. Testing get_statistics('MLB') directly...")
    try:
        result = espn_api.get_statistics("MLB")
        print(f"   Result type: {type(result)}")
        print(f"   Result keys: {list(result.keys())}")
        
        player_stats = result.get('player_stats', [])
        team_stats = result.get('team_stats', [])
        
        print(f"   Player stats count: {len(player_stats)}")
        print(f"   Team stats count: {len(team_stats)}")
        
        if player_stats:
            print(f"\n   First few player stats:")
            for i, stat in enumerate(player_stats[:3]):
                print(f"     {i+1}. {stat.get('name', 'Unknown')}")
                leaders = stat.get('leaders', [])
                if leaders:
                    leader = leaders[0]
                    print(f"        Leader: {leader.get('name', 'Unknown')} = {leader.get('value', 0)}")
        else:
            print("   ❌ NO PLAYER STATS FOUND!")
            
        if team_stats:
            print(f"\n   Team stats:")
            for i, stat in enumerate(team_stats):
                print(f"     {i+1}. {stat.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"   💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def debug_mlb_api_directly():
    """Test the MLB API directly"""
    
    print("\n2. Testing MLB API directly...")
    try:
        result = espn_api._get_mlb_statistics()
        print(f"   Direct MLB API result type: {type(result)}")
        print(f"   Direct MLB API keys: {list(result.keys())}")
        
        player_stats = result.get('player_stats', [])
        print(f"   Direct player stats count: {len(player_stats)}")
        
        if player_stats:
            print(f"   Sample stats:")
            for stat in player_stats[:3]:
                print(f"     - {stat.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"   💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def test_data_format():
    """Test the data format expected by the UI"""
    
    print("\n3. Testing data format for UI...")
    
    try:
        result = espn_api.get_statistics("MLB")
        player_stats = result.get('player_stats', [])
        
        if player_stats:
            # Check the format of a stat
            stat = player_stats[0]
            print(f"   Sample stat structure:")
            print(f"     Keys: {list(stat.keys())}")
            
            # Check leaders format
            leaders = stat.get('leaders', [])
            if leaders:
                leader = leaders[0]
                print(f"     Leader structure:")
                print(f"       Keys: {list(leader.keys())}")
                print(f"       Name: {leader.get('name', 'N/A')}")
                print(f"       Value: {leader.get('value', 'N/A')}")
                print(f"       Team: {leader.get('team', 'N/A')}")
                
    except Exception as e:
        print(f"   💥 ERROR: {str(e)}")

if __name__ == "__main__":
    debug_mlb_player_stats()
    debug_mlb_api_directly()
    test_data_format()
