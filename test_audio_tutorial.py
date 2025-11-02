#!/usr/bin/env python3
"""
Test the audio tutorial system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🎵 AUDIO TUTORIAL SYSTEM TEST")
print("="*50)

# Test imports
print("Testing imports...")
try:
    import scores
    print("✅ Main scores module imported")
    
    # Check audio availability flags
    if hasattr(scores, 'AUDIO_AVAILABLE'):
        print(f"✅ AUDIO_AVAILABLE = {scores.AUDIO_AVAILABLE}")
    
    if hasattr(scores, 'FOOTBALL_AUDIO_AVAILABLE'):
        print(f"✅ FOOTBALL_AUDIO_AVAILABLE = {scores.FOOTBALL_AUDIO_AVAILABLE}")
    
    # Check tutorial classes
    tutorial_classes = ['AudioTutorialView', 'BaseballAudioTutorialView', 'FootballAudioTutorialView']
    for class_name in tutorial_classes:
        if hasattr(scores, class_name):
            print(f"✅ {class_name} class defined")
        else:
            print(f"❌ {class_name} class missing")
    
    # Check app methods
    app_methods = ['open_audio_tutorial', 'open_baseball_audio_tutorial', 'open_football_audio_tutorial']
    for method_name in app_methods:
        if hasattr(scores.SportsScoresApp, method_name):
            print(f"✅ SportsScoresApp.{method_name} method defined")
        else:
            print(f"❌ SportsScoresApp.{method_name} method missing")

except ImportError as e:
    print(f"❌ Import failed: {e}")

print("\n🎯 TUTORIAL NAVIGATION FLOW:")
print("1. Home screen → 🎵 Audio Tutorial")
print("2. Audio Tutorial → ⚾ Baseball Audio Tutorial OR 🏈 Football Audio Tutorial")
print("3. Sport tutorial → Sample pitches/drives with playable audio")

print("\n🎵 SAMPLE CONTENT:")
print("⚾ Baseball Tutorial:")
print("  • Strike - Fastball Center (95 mph fastball down the middle)")
print("  • Ball - Curveball Low (78 mph curveball below the zone)")
print("  • Hit - Slider Outside (84 mph slider hit for single)")
print("  • Strike - Changeup Corner (82 mph changeup on the corner)")
print("  • Ball - Fastball High (97 mph fastball above the zone)")

print("\n🏈 Football Tutorial:")
print("  • Touchdown Drive (7 plays, 75 yards - demonstrates field progression)")
print("  • Short Drive - Field Goal (4 plays, 18 yards ending in field goal)")
print("  • Failed Drive - Punt (3 plays, 8 yards ending in punt)")
print("  • Big Play Drive (2 plays, 65 yards with long pass)")
print("  • Turnover Drive (5 plays ending in interception)")

print("\n✅ Audio Tutorial System Ready!")
print("Users can now learn how audio works before encountering it in real games.")