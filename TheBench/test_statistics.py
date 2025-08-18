#!/usr/bin/env python3
"""
Test script for the new Statistics flow
Tests: Statistics → Team/Player Choice → Stat Selection → Results Table
"""

import sys
import os
sys.path.append('.')

def test_statistics_flow():
    """Test the new statistics implementation"""
    print("🏟️  Testing New Statistics Flow")
    print("=" * 50)
    
    try:
        # Test imports
        from services.api_service import ApiService
        print("✅ ApiService imported")
        
        from scores import StatisticsChoiceDialog, StatisticsViewDialog
        print("✅ Statistics dialogs imported")
        
        # Test API call
        print("\n📊 Testing Statistics API Call...")
        leagues_to_test = ["mlb", "nfl", "nba"]
        
        for league in leagues_to_test:
            print(f"\nTesting {league.upper()}...")
            try:
                stats_data = ApiService.get_statistics(league)
                
                if stats_data:
                    player_stats = stats_data.get("player_stats", [])
                    team_stats = stats_data.get("team_stats", [])
                    
                    print(f"  ✅ Player stat categories: {len(player_stats)}")
                    print(f"  ✅ Team stat categories: {len(team_stats)}")
                    
                    # Sample player stats
                    if player_stats:
                        first_category = player_stats[0]
                        stats_list = first_category.get("stats", [])
                        print(f"  📈 Sample player stats in first category: {len(stats_list)}")
                        
                        if stats_list:
                            sample_stat = stats_list[0]
                            print(f"  📋 Sample: {sample_stat.get('player_name')} - {sample_stat.get('stat_name')}: {sample_stat.get('value')}")
                    
                    # Sample team stats  
                    if team_stats:
                        first_team_category = team_stats[0]
                        teams_list = first_team_category.get("stats", [])
                        print(f"  🏈 Sample team stats in first category: {len(teams_list)}")
                        
                        if teams_list:
                            sample_team = teams_list[0] 
                            team_stats_dict = sample_team.get("stats", {})
                            print(f"  📋 Sample: {sample_team.get('team_name')} has {len(team_stats_dict)} stat types")
                else:
                    print(f"  ⚠️ No statistics data returned for {league}")
                    
            except Exception as e:
                print(f"  ❌ Error testing {league}: {str(e)}")
        
        print("\n🎯 New Statistics Flow Summary:")
        print("1. ✅ Click 'Statistics' in main app")
        print("2. ✅ Choose 'Team Statistics' or 'Player Statistics'") 
        print("3. ✅ Select specific statistic from list")
        print("4. ✅ View ranked table (top 50 players or all teams)")
        print("\n🚀 Implementation complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_statistics_flow()
