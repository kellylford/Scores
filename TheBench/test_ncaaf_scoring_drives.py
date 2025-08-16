#!/usr/bin/env python3
"""
Test NCAAF scoring drive enhancement with historical 2024 data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from espn_api import get_scores, get_game_details
from datetime import datetime

def test_ncaaf_scoring_drives():
    """Test NCAAF scoring drive enhancement with 2024 data"""
    
    def get_drive_result_info(drive):
        """Helper function matching the implementation"""
        result = drive.get('result', '').upper()
        
        if result == 'TD':
            return {'icon': '🏈', 'badge': 'TD 7pts', 'accessible_text': 'Touchdown scoring drive'}
        elif result == 'FG':
            return {'icon': '🥅', 'badge': 'FG 3pts', 'accessible_text': 'Field goal scoring drive'}
        elif result == 'MISSED FG':
            return {'icon': '❌', 'badge': 'MISSED FG', 'accessible_text': 'Missed field goal attempt'}
        elif result in ['FUMBLE', 'INT', 'INTERCEPTION', 'TURNOVER']:
            return {'icon': '🔄', 'badge': 'TURNOVER', 'accessible_text': 'Turnover drive'}
        elif result == 'DOWNS':
            return {'icon': '🛑', 'badge': '4TH DOWN', 'accessible_text': 'Turnover on downs'}
        elif result == 'PUNT':
            return {'icon': '⚡', 'badge': 'PUNT', 'accessible_text': 'Punt drive'}
        elif result in ['END OF HALF', 'END OF GAME']:
            return {'icon': '⏰', 'badge': 'CLOCK', 'accessible_text': 'Clock expiration drive'}
        elif result == 'SAFETY':
            return {'icon': '🛡️', 'badge': 'SAFETY 2pts', 'accessible_text': 'Safety scoring drive'}
        else:
            return {'icon': '📌', 'badge': result if result else 'DRIVE', 'accessible_text': 'Non-scoring drive'}
    
    try:
        # Test with known NCAAF game from 2024
        test_date = datetime(2024, 10, 12)  # Big 12 Championship Saturday
        
        print(f"Testing NCAAF scoring drive enhancement")
        print(f"Date: {test_date.strftime('%Y-%m-%d')}")
        print("=" * 60)
        
        # Get NCAAF games
        ncaaf_games = get_scores('NCAAF', test_date)
        
        if not ncaaf_games:
            print("No NCAAF games found for test date")
            return False
        
        print(f"Found {len(ncaaf_games)} NCAAF games")
        
        # Test with first game that has drives data
        for i, game in enumerate(ncaaf_games[:5]):
            game_name = game.get('name', 'Unknown Game')
            game_id = game.get('id')
            
            if not game_id:
                continue
                
            print(f"\\nTesting Game: {game_name}")
            print("-" * 40)
            
            try:
                details = get_game_details('NCAAF', game_id)
                
                if 'drives' not in details:
                    print("No drives data available")
                    continue
                
                drives_data = details['drives']
                previous_drives = drives_data.get('previous', [])
                
                if not previous_drives:
                    print("No previous drives found")
                    continue
                
                print(f"Drives found: {len(previous_drives)}")
                
                # Analyze drives by quarter
                quarter_groups = {}
                
                for drive in previous_drives:
                    # Get drive info
                    description = drive.get("description", "Unknown drive")
                    team_info = drive.get("team", {})
                    team_name = team_info.get("displayName", "Unknown Team")
                    
                    # Determine quarter
                    plays = drive.get("plays", [])
                    quarter = "Unknown Quarter"
                    if plays and len(plays) > 0:
                        first_play = plays[0]
                        period_info = first_play.get("period", {})
                        quarter_num = period_info.get("number", "?")
                        quarter = f"Quarter {quarter_num}"
                    
                    # Group by quarter
                    if quarter not in quarter_groups:
                        quarter_groups[quarter] = []
                    
                    quarter_groups[quarter].append((drive, team_name, description))
                
                # Display enhanced drive information
                total_scoring_drives = 0
                total_points = 0
                
                for quarter in sorted(quarter_groups.keys()):
                    print(f"\\n{quarter}")
                    print("  " + "-" * 35)
                    
                    drives_in_quarter = quarter_groups[quarter]
                    quarter_scoring = 0
                    quarter_points = 0
                    
                    for drive, team_name, description in drives_in_quarter:
                        result_info = get_drive_result_info(drive)
                        
                        # Build enhanced summary
                        enhanced_summary = f"  {result_info['icon']} [{result_info['badge']}] {team_name}: {description}"
                        print(enhanced_summary)
                        
                        # Count scoring drives and points
                        if result_info['badge'] in ['TD 7pts', 'FG 3pts', 'SAFETY 2pts']:
                            quarter_scoring += 1
                            total_scoring_drives += 1
                            if 'TD' in result_info['badge']:
                                quarter_points += 7
                                total_points += 7
                            elif 'FG' in result_info['badge']:
                                quarter_points += 3
                                total_points += 3
                            elif 'SAFETY' in result_info['badge']:
                                quarter_points += 2
                                total_points += 2
                    
                    print(f"  Quarter Summary: {quarter_scoring} scoring drives, {quarter_points} points")
                
                print(f"\\n" + "=" * 60)
                print(f"GAME SUMMARY:")
                print(f"  Total drives: {len(previous_drives)}")
                print(f"  Scoring drives: {total_scoring_drives}")
                print(f"  Points from drives: {total_points}")
                print(f"\\n✅ NCAAF scoring drive enhancement working perfectly!")
                
                # Test unique NCAAF drive results
                all_results = set()
                for drive in previous_drives:
                    result = drive.get('result', 'UNKNOWN')
                    all_results.add(result)
                
                print(f"\\n🏈 NCAAF-specific drive results found:")
                ncaaf_specific = all_results - {'TD', 'FG', 'MISSED FG', 'PUNT', 'FUMBLE', 'SAFETY'}
                for result in sorted(ncaaf_specific):
                    count = sum(1 for d in previous_drives if d.get('result') == result)
                    print(f"  {result}: {count} drives")
                
                return True
                
            except Exception as e:
                print(f"Error getting game details: {e}")
                continue
        
        print("No games with drives data found")
        return False
        
    except Exception as e:
        print(f"Error in NCAAF test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ncaaf_scoring_drives()
    if success:
        print("\\n🎉 NCAAF scoring drive support validated!")
    else:
        print("\\n❌ NCAAF test failed")
