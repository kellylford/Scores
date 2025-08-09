#!/usr/bin/env python3

"""
Test script to verify play-by-play functionality works correctly
"""

from services.api_service import ApiService
from datetime import datetime

def test_plays_functionality():
    """Test that plays data can be retrieved and processed"""
    print("Testing play-by-play functionality...")
    
    try:
        # Get some MLB games
        scores = ApiService.get_scores('MLB', datetime.now())
        
        if not scores:
            print("No MLB games found for today")
            return
        
        # Get game details for the first few games
        for i, game in enumerate(scores[:3]):
            game_id = game.get('id')
            if not game_id:
                continue
                
            print(f"\nGame {i+1}: {game.get('name', 'Unknown vs Unknown')}")
            print(f"Game ID: {game_id}")
            
            try:
                details = ApiService.get_game_details('MLB', game_id)
                plays_data = details.get('plays', [])
                
                if plays_data:
                    print(f"  ✅ Found {len(plays_data)} plays")
                    
                    # Show first few plays as examples
                    for j, play in enumerate(plays_data[:3]):
                        play_text = play.get('text', 'No text')
                        period_info = play.get('period', {})
                        is_scoring = play.get('scoringPlay', False)
                        
                        period_display = period_info.get('displayValue', 'Unknown period') if period_info else 'No period'
                        scoring_indicator = " [SCORING]" if is_scoring else ""
                        
                        print(f"    Play {j+1}: [{period_display}] {play_text[:100]}{scoring_indicator}")
                        
                        if j >= 2:  # Limit output
                            break
                else:
                    print(f"  ❌ No plays data found")
                    
            except Exception as e:
                print(f"  ❌ Error getting game details: {e}")
                
            if i >= 2:  # Limit to first 3 games
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_plays_functionality()
