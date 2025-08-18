#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.api_service import ApiService

def test_fixed_naming():
    """Test the fixed player statistics naming"""
    print("DEBUG: Testing fixed player statistics naming...")
    
    try:
        # Get the actual statistics data
        stats_data = ApiService.get_statistics("MLB")
        
        if not stats_data:
            print("No statistics data available")
            return
        
        player_stats = stats_data.get("player_stats", [])
        print(f"Found {len(player_stats)} player stat categories")
        
        # Simulate the _get_available_statistics logic for players
        available_stats = []
        
        for i, category in enumerate(player_stats):
            category_name = category.get("category", "Unknown")
            stats_list = category.get("stats", [])
            
            if not stats_list:
                continue
            
            # Group by stat types
            stat_types = {}
            for stat in stats_list:
                stat_name = stat.get("stat_name", "Unknown")
                if stat_name not in stat_types:
                    stat_types[stat_name] = []
                stat_types[stat_name].append(stat)
            
            # Add each unique stat type with NEW NAMING LOGIC
            for stat_name, stats in stat_types.items():
                # Avoid duplicate names when category and stat name are the same
                if stat_name.lower() == category_name.lower():
                    display_name = stat_name  # Just use the stat name
                else:
                    display_name = f"{stat_name} ({category_name})"  # Include category for clarity
                
                available_stats.append({
                    'name': display_name,
                    'category': category_name,
                    'stat_name': stat_name,
                    'data': stats,
                    'type': 'player'
                })
                
                print(f"  ✅ {display_name}")
        
        print(f"\nTotal available player stats: {len(available_stats)}")
        
        # Test specific problematic cases
        print(f"\n=== Testing Specific Cases ===")
        problematic_cases = ['Wins', 'Wins Above Replacement', 'Home Runs', 'Batting Average']
        
        for case in problematic_cases:
            found_stats = [stat for stat in available_stats if case in stat['name']]
            if found_stats:
                for stat in found_stats:
                    print(f"  {case} → '{stat['name']}'")
            else:
                print(f"  {case} → NOT FOUND")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_naming()
