#!/usr/bin/env python3
"""
Debug the drive audio issue - check what drive data is being processed
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from football_audio_mapper import FootballAudioMapper
    print("✅ FootballAudioMapper imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Create test drive data that mimics real ESPN API structure
test_drive = {
    "team": {"displayName": "Green Bay Packers"},
    "description": "7 plays, 75 yards, TOUCHDOWN",
    "plays": [
        {
            "text": "A.Rodgers pass short right to D.Adams for 12 yards",
            "statYardage": 12,
            "type": {"text": "Pass Reception"},
            "start": {"down": 1, "distance": 10, "yardsToEndzone": 75}
        },
        {
            "text": "A.Jones rush up the middle for 8 yards",
            "statYardage": 8,
            "type": {"text": "Rush"},  
            "start": {"down": 2, "distance": 3, "yardsToEndzone": 63}
        },
        {
            "text": "A.Jones rush right end for 7 yards TOUCHDOWN",
            "statYardage": 7,
            "type": {"text": "Rush"},
            "start": {"down": 2, "distance": 7, "yardsToEndzone": 7},
            "scoringPlay": True
        }
    ]
}

print("\n" + "="*70)
print("🐛 DEBUGGING DRIVE AUDIO PROCESSING")
print("="*70)

mapper = FootballAudioMapper()
print(f"\nProcessing test drive: {test_drive['team']['displayName']} - {test_drive['description']}")
print("-" * 50)

audio_sequence = mapper.map_drive_to_audio_sequence(test_drive)

print(f"\n📊 RESULTS:")
print(f"Input: {len(test_drive['plays'])} plays")
print(f"Output: {len(audio_sequence)} audio configs")

if len(audio_sequence) != len(test_drive['plays']):
    print("❌ MISMATCH: Different number of plays vs audio configs!")
else:
    print("✅ Correct: Same number of plays and audio configs")

print("\n🎵 Audio sequence details:")
for i, config in enumerate(audio_sequence):
    print(f"  {i+1}. {config.frequency:.1f}Hz {config.wave_type} (field pos: {config.field_position})")

print("\n💡 If this works correctly but the real app doesn't,")
print("   the issue is in the drive data extraction, not the audio mapper!")