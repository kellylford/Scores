#!/usr/bin/env python3

"""
Check what stats are available in team categories
"""

import sys
import os
sys.path.append('.')

# Set environment to avoid GUI
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from services.api_service import ApiService

def check_team_stats():
    print("Checking team stats categories...")
    
    try:
        stats_data = ApiService.get_statistics("MLB")
        team_stats = stats_data.get('team_stats', [])
        
        print(f"Found {len(team_stats)} team stat categories:")
        for i, category in enumerate(team_stats):
            category_name = category.get('category', 'Unknown')
            teams_in_category = category.get('stats', [])
            print(f"\n{i+1}. {category_name}")
            
            if teams_in_category:
                first_team = teams_in_category[0]
                stats_dict = first_team.get('stats', {})
                print(f"   Available stats: {list(stats_dict.keys())}")
                
                # Look for save-related stats
                save_stats = [stat for stat in stats_dict.keys() if 'save' in stat.lower()]
                if save_stats:
                    print(f"   *** SAVE-RELATED: {save_stats}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_team_stats()
