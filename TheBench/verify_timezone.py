#!/usr/bin/env python3
"""
Timezone Conversion Verification Script
Run this to verify that timezone conversion is working in the Scores app
"""

from datetime import datetime, timedelta
from services.api_service import ApiService
from models.game import GameData

def verify_timezone_conversion():
    print("=" * 60)
    print("TIMEZONE CONVERSION VERIFICATION")
    print("=" * 60)
    
    # Get tomorrow's MLB games (most likely to have scheduled times)
    tomorrow = datetime.now() + timedelta(days=1)
    print(f"Testing games for: {tomorrow.strftime('%A, %B %d, %Y')}")
    print()
    
    try:
        scores_data = ApiService.get_scores('MLB', tomorrow)
        
        if not scores_data:
            print("❌ No MLB games found for tomorrow")
            return
            
        print(f"✅ Found {len(scores_data)} MLB games")
        print()
        print("TIMEZONE CONVERSION RESULTS:")
        print("-" * 40)
        
        converted_count = 0
        for i, game_raw in enumerate(scores_data[:8]):  # Show up to 8 games
            game = GameData(game_raw, 'MLB')
            display_text = game.get_display_text()
            
            # Check if time was converted
            raw_start = game_raw.get('start_time', 'N/A')
            converted_start = game.start_time
            
            print(f"{i+1:2}. {display_text}")
            
            # Show conversion details if applicable
            if 'EDT' in raw_start or 'EST' in raw_start:
                if 'CDT' in converted_start or 'CST' in converted_start:
                    print(f"    ✅ CONVERTED: {raw_start} → {converted_start}")
                    converted_count += 1
                else:
                    print(f"    ❌ NOT CONVERTED: {raw_start}")
            elif 'Final' in raw_start or 'Progress' in raw_start:
                print(f"    ℹ️  Live/Final game (no conversion needed)")
            else:
                print(f"    ⚠️  Unknown format: {raw_start}")
            print()
        
        print("=" * 60)
        print(f"SUMMARY: {converted_count} games converted to your local timezone")
        
        if converted_count > 0:
            print("✅ TIMEZONE CONVERSION IS WORKING!")
            print("   Eastern times (EDT/EST) are being converted to Central (CDT/CST)")
        else:
            print("⚠️  No timezone conversions detected")
            print("   This might be because all games are live/final or already in local time")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_timezone_conversion()
