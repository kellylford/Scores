#!/usr/bin/env python3
"""
Quick test to verify GameDetailsDialog audio integration without full GUI
"""

class MockGameDetailsView:
    """Mock game details view for testing"""
    def __init__(self):
        self.current_drives_data = {
            "current": None,
            "previous": [
                {
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
                            "text": "A.Jones rush right end for 7 yards TOUCHDOWN",
                            "statYardage": 7,
                            "type": {"text": "Rush"},
                            "start": {"down": 2, "distance": 7, "yardsToEndzone": 7},
                            "scoringPlay": True
                        }
                    ]
                }
            ]
        }
        
    def findChildren(self, widget_type):
        """Mock finding children - return empty list since we'll test fallback"""
        return []

class MockTreeWidget:
    """Mock tree widget for testing"""
    def __init__(self):
        self.current_item_data = None
        
    def accessibleName(self):
        return "NFL Drives Tree"
        
    def currentItem(self):
        return None  # Simulate no selection to test fallback

# Test the focus detection logic
try:
    # Import what we need
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from football_audio_mapper import FootballAudioMapper, FootballDrivePlayer
    from audio_player import AudioPlayer
    
    print("✅ Audio imports successful")
    
    # Test the drive data extraction logic
    mock_view = MockGameDetailsView()
    
    # Simulate the GameDetailsDialog logic
    drives_data = mock_view.current_drives_data
    
    if drives_data:
        print("✅ Found drives data")
        current_drive = drives_data.get("current")
        previous_drives = drives_data.get("previous", [])
        
        if current_drive:
            test_drive = current_drive
            print("✅ Using current drive")
        elif previous_drives:
            test_drive = previous_drives[0]
            print(f"✅ Using first of {len(previous_drives)} previous drives")
        else:
            test_drive = None
            print("❌ No drives available")
        
        if test_drive:
            print(f"Drive: {test_drive['team']['displayName']} - {test_drive['description']}")
            print(f"Plays: {len(test_drive['plays'])}")
            
            # Test audio generation
            mapper = FootballAudioMapper()
            audio_sequence = mapper.map_drive_to_audio_sequence(test_drive)
            print(f"✅ Generated {len(audio_sequence)} audio configs")
            
            # Test audio playback
            player = AudioPlayer()
            print("🎵 Playing test drive audio...")
            player.play_audio_sequence(audio_sequence, silence_between=0.1)
            print("✅ Audio playback completed")
            
    else:
        print("❌ No drives data available")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Focus Detection Test Summary:")
print("="*50)
print("The integration should work by:")
print("1. Detecting drives in GameDetailsDialog") 
print("2. Using fallback logic when no specific drive is focused")
print("3. Playing audio for the available drive data")
print("4. Providing debug information in console")
print("\nTry pressing Alt+P in an NFL game's drives section!")