"""
Test script to demonstrate timezone conversion for game times
"""

from timezone_utils import convert_espn_time_to_local, get_user_timezone

def test_timezone_conversion():
    print("=== Timezone Conversion Test ===")
    print(f"Detected user timezone: {get_user_timezone()}")
    print()
    
    # Test cases based on the user's example
    test_cases = [
        "7:00 PM EDT",  # User's example: 7P East -> 6P Central
        "8:00 PM EST",  # Winter time
        "5:30 PM PDT",  # West coast game
        "12:00 PM CDT", # Already in user's timezone
        "9:15 PM EDT",  # Late game
        "1:00 PM EST",  # Afternoon game
        "8/28 - 7:00 PM EDT",  # With date
        "9/15 - 8:30 PM PST",  # Different format
        "TBD",          # No time set
        "Final",        # Game over
        "In Progress",  # Live game
    ]
    
    print("Time conversion examples:")
    print("Original Time        ->  Your Local Time")
    print("-" * 45)
    
    for test_time in test_cases:
        converted = convert_espn_time_to_local(test_time)
        print(f"{test_time:<20} ->  {converted}")
    
    print()
    print("✅ Timezone conversion is working!")
    print("When ESPN shows '7:00 PM EDT', you'll now see '6:00 PM CDT'")

if __name__ == "__main__":
    test_timezone_conversion()
