#!/usr/bin/env python3
"""
Test the exact dialog logic to find the issue
"""

import sys
sys.path.append('.')

from services.api_service import ApiService

print("=== TESTING DIALOG LOGIC ===")

# Step 1: Load data exactly like the dialog
print("1. Loading statistics data...")
try:
    statistics_data = ApiService.get_statistics('mlb')
    print("   Data loaded successfully")
    print("   Player stats:", len(statistics_data.get('player_stats', [])))
    print("   Team stats:", len(statistics_data.get('team_stats', [])))
except Exception as e:
    print("   Data loading failed:", str(e))
    exit()

# Step 2: Check if data exists
if not statistics_data:
    print("2. No statistics_data")
    exit()

print("2. statistics_data exists")

# Step 3: Simulate _get_available_statistics logic
print("3. Extracting available statistics for player type...")
stat_type = 'player'
available_stats = []

if stat_type == "player":
    player_stats = statistics_data.get("player_stats", [])
    print(f"   Found {len(player_stats)} player stat categories")
    
    for i, category in enumerate(player_stats):
        category_name = category.get("category", "Unknown")
        stats_list = category.get("stats", [])
        print(f"   Category {i+1}: {category_name} with {len(stats_list)} stats")
        
        # Group by stat types
        stat_types = {}
        for stat in stats_list:
            stat_name = stat.get("stat_name", "Unknown")
            if stat_name not in stat_types:
                stat_types[stat_name] = []
            stat_types[stat_name].append(stat)
        
        # Add each unique stat type
        for stat_name, stats in stat_types.items():
            available_stats.append({
                'name': f"{stat_name} ({category_name})",
                'category': category_name,
                'stat_name': stat_name,
                'data': stats,
                'type': 'player'
            })

print(f"4. Total available stats created: {len(available_stats)}")

if available_stats:
    print("   Sample stats:")
    for i, stat in enumerate(available_stats[:3]):
        print(f"      {i+1}. {stat['name']} ({len(stat['data'])} players)")
else:
    print("   NO AVAILABLE STATS CREATED!")
    
    # Debug why no stats were created
    print("\n   DEBUGGING:")
    player_stats = statistics_data.get("player_stats", [])
    if player_stats:
        first_cat = player_stats[0]
        print(f"   First category: {first_cat}")
        stats_list = first_cat.get("stats", [])
        if stats_list:
            first_stat = stats_list[0]
            print(f"   First stat: {first_stat}")
            print(f"   stat_name in first stat: {'stat_name' in first_stat}")
            print(f"   stat_name value: {first_stat.get('stat_name')}")
