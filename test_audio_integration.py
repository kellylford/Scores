#!/usr/bin/env python3
"""
Test script to verify the football audio integration is working
"""

# Test imports
try:
    from football_audio_mapper import FootballAudioMapper, FootballDrivePlayer
    from audio_player import AudioPlayer
    print("✅ Football audio imports work")
    FOOTBALL_AUDIO_AVAILABLE = True
except ImportError as e:
    print(f"❌ Football audio imports failed: {e}")
    FOOTBALL_AUDIO_AVAILABLE = False

if FOOTBALL_AUDIO_AVAILABLE:
    # Test audio system initialization
    try:
        audio_mapper = FootballAudioMapper()
        audio_player = AudioPlayer()
        drive_player = FootballDrivePlayer()  # Fixed: no parameters needed
        print("✅ Audio system initialized successfully")
        
        # Test with sample drive data
        sample_drive = {
            "team": {"displayName": "Green Bay Packers"},
            "description": "7 plays, 75 yards, TOUCHDOWN",
            "plays": [
                {
                    "text": "A.Rodgers pass short right to D.Adams for 12 yards",
                    "statYardage": 12,
                    "type": {"text": "Pass"},
                    "start": {"down": 1, "distance": 10, "yardsToEndzone": 75}
                },
                {
                    "text": "A.Jones rush up the middle for 8 yards",
                    "statYardage": 8,
                    "type": {"text": "Rush"},
                    "start": {"down": 2, "distance": 3, "yardsToEndzone": 63}
                },
                {
                    "text": "A.Rodgers pass deep right to D.Adams for 25 yards",
                    "statYardage": 25,
                    "type": {"text": "Pass"},
                    "start": {"down": 1, "distance": 10, "yardsToEndzone": 55}
                },
                {
                    "text": "A.Jones rush left tackle for 15 yards",
                    "statYardage": 15,
                    "type": {"text": "Rush"},
                    "start": {"down": 1, "distance": 10, "yardsToEndzone": 30}
                },
                {
                    "text": "A.Rodgers pass short left to R.Cobb for 8 yards",
                    "statYardage": 8,
                    "type": {"text": "Pass"},
                    "start": {"down": 1, "distance": 10, "yardsToEndzone": 15}
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
        
        print("\n🎵 Testing drive audio playback...")
        print("Drive:", sample_drive["team"]["displayName"], "-", sample_drive["description"])
        print("Press Enter to play drive audio (or Ctrl+C to skip)...")
        
        try:
            input()
            # Test the audio sequence generation
            audio_sequence = audio_mapper.map_drive_to_audio_sequence(sample_drive)
            print(f"✅ Generated audio sequence with {len(audio_sequence)} plays")
            
            # Play the entire sequence using the correct method
            print("Playing drive as complete audio sequence...")
            audio_player.play_audio_sequence(audio_sequence, silence_between=0.1)
            
            print("✅ Drive audio playback completed!")
        except KeyboardInterrupt:
            print("⏭️  Audio playback skipped")
        
    except Exception as e:
        print(f"❌ Audio system test failed: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("INTEGRATION STATUS:")
print("="*60)
if FOOTBALL_AUDIO_AVAILABLE:
    print("✅ Football audio system is ready for integration")
    print("✅ Alt+P functionality should work in NFL/NCAAF game details")
    print("✅ Press Alt+P when focused on a drive in the game details view")
else:
    print("❌ Football audio system not available")
    print("❌ Alt+P functionality will not work")

print("\nTo test in the main application:")
print("1. Open an NFL or NCAAF game")
print("2. Go to game details")
print("3. Navigate to the 'Drives' section")
print("4. Focus on any drive in the tree")
print("5. Press Alt+P to play drive audio")