"""
Hybrid Audio Player - Option D Implementation
Combines TTS narration, musical tones, and sound effects for context-aware audio feedback.

Usage modes:
- 'single': Individual play with TTS details
- 'sequence': Drive sequence with musical tones + key moment narration
- 'tutorial': Full TTS explanations
"""

import pyttsx3
from typing import List, Optional, Dict, Any
from enhanced_audio_player import EnhancedAudioPlayer
from football_audio_mapper import PlayAudioConfig, FootballAudioMapper


class HybridAudioPlayer:
    """Smart context-aware audio that combines TTS, tones, and sound effects."""
    
    def __init__(self):
        self.audio_player = EnhancedAudioPlayer()  # Use enhanced audio for better sound
        self.mapper = FootballAudioMapper()
        
        # Initialize TTS engine
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speed
            self.tts_engine.setProperty('volume', 0.9)
            self.tts_available = True
        except Exception as e:
            print(f"Warning: TTS not available - {e}")
            self.tts_available = False
        
        # User preferences
        self.preferences = {
            'narration_enabled': True,
            'tones_enabled': True,
            'sound_effects_enabled': False,  # Not implemented yet
        }
    
    def speak(self, text: str):
        """Speak text using TTS."""
        if self.tts_available and self.preferences['narration_enabled']:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
        else:
            # Fallback to print
            print(f"[NARRATION]: {text}")
    
    def _convert_to_espn_format(self, play_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert simplified play format to ESPN API format.
        
        Simplified format:
            {'yardage': 5, 'type': 'rush', 'yardsToEndzone': 75}
        
        ESPN format:
            {'statYardage': 5, 'type': {'text': 'Rush'}, 'start': {'yardsToEndzone': 75}}
        """
        espn_play = {}
        
        # Map yardage
        if 'yardage' in play_data:
            espn_play['statYardage'] = play_data['yardage']
        
        # Map type
        if 'type' in play_data:
            type_text = play_data['type']
            if type_text.lower() == 'rush':
                type_text = 'Rush'
            elif type_text.lower() == 'pass':
                type_text = 'Pass Reception'
            espn_play['type'] = {'text': type_text}
        
        # Map field position
        if 'yardsToEndzone' in play_data:
            espn_play['start'] = {'yardsToEndzone': play_data['yardsToEndzone']}
        
        # Map scoring play
        if 'isScoringPlay' in play_data:
            espn_play['scoringPlay'] = play_data['isScoringPlay']
            if play_data.get('isScoringPlay'):
                # Assume touchdown for scoring plays
                espn_play['scoreValue'] = 6
        
        return espn_play
    
    def play_single_play(self, play_data: Dict[str, Any], with_narration: bool = True):
        """
        Play audio for a single play with TTS narration.
        
        Args:
            play_data: Dictionary with play information (description, yardage, type, etc.)
            with_narration: Whether to include TTS narration
        
        Example play_data (simplified format):
            {
                'description': 'RB rush up middle for 5 yards',
                'yardage': 5,
                'type': 'rush',
                'yardsToEndzone': 75,
                'down': 1,
                'distance': 10
            }
        """
        # Convert simplified format to ESPN API format for mapper
        espn_format = self._convert_to_espn_format(play_data)
        
        # Generate audio config
        config = self.mapper.map_play_to_audio(espn_format)
        field_position = self.mapper._calculate_field_position(espn_format)
        
        # Narrate the play details
        if with_narration:
            yardage = play_data.get('yardage', 0)
            play_type = play_data.get('type', 'play')
            description = play_data.get('description', '')
            
            # Create narration text
            if yardage >= 0:
                narration = f"{yardage} yard {play_type}. {description}"
            else:
                narration = f"Loss of {abs(yardage)} yards. {description}"
            
            self.speak(narration)
        
        # Play the tone
        if self.preferences['tones_enabled']:
            self.audio_player.play_single_play(config, field_position=field_position)
    
    def play_drive_sequence(self, drive_plays: List[Dict[str, Any]], mode: str = 'sequence'):
        """
        Play a sequence of plays with context-appropriate audio.
        
        Args:
            drive_plays: List of play data dictionaries
            mode: 'sequence' (musical tones + key moments) or 'tutorial' (full narration)
        
        Example drive_plays:
            [
                {'description': 'Pass complete for 12 yards', 'yardage': 12, 'type': 'pass', ...},
                {'description': 'Rush for 3 yards', 'yardage': 3, 'type': 'rush', ...},
                ...
            ]
        """
        if not drive_plays:
            self.speak("No plays to announce")
            return
        
        if mode == 'tutorial':
            # Full narration for each play
            self._play_tutorial_mode(drive_plays)
        else:
            # Sequence mode: tones + key moment narration
            self._play_sequence_mode(drive_plays)
    
    def _play_tutorial_mode(self, drive_plays: List[Dict[str, Any]]):
        """Tutorial mode with detailed TTS explanations."""
        self.speak(f"Playing {len(drive_plays)} plays in tutorial mode")
        
        for i, play in enumerate(drive_plays, 1):
            # Convert to ESPN format
            espn_format = self._convert_to_espn_format(play)
            
            # Generate audio config
            config = self.mapper.map_play_to_audio(espn_format)
            field_position = self.mapper._calculate_field_position(espn_format)
            
            # Detailed explanation
            play_type = play.get('type', 'play')
            yardage = play.get('yardage', 0)
            wave_type = config.wave_type
            frequency = int(config.frequency)
            
            explanation = (
                f"Play {i}. This is a {play_type}. "
                f"Notice the {wave_type} wave pattern at {frequency} hertz. "
                f"The stereo positioning represents the field location. "
            )
            
            self.speak(explanation)
            
            # Play the tone
            if self.preferences['tones_enabled']:
                self.audio_player.play_single_play(config, field_position=field_position)
    
    def _play_sequence_mode(self, drive_plays: List[Dict[str, Any]]):
        """Sequence mode with musical tones + key moment narration."""
        # Generate all configs and field positions
        configs = []
        field_positions = []
        
        for play in drive_plays:
            espn_format = self._convert_to_espn_format(play)
            config = self.mapper.map_play_to_audio(espn_format)
            field_position = self.mapper._calculate_field_position(espn_format)
            configs.append(config)
            field_positions.append(field_position)
        
        # Announce drive start
        num_plays = len(drive_plays)
        self.speak(f"Playing drive with {num_plays} plays")
        
        # Play the audio sequence with tones
        if self.preferences['tones_enabled']:
            self.audio_player.play_audio_sequence(
                configs,
                silence_between=0.1,
                field_positions=field_positions
            )
        
        # Announce key moments after the sequence
        self._announce_key_moments(drive_plays)
    
    def _announce_key_moments(self, drive_plays: List[Dict[str, Any]]):
        """Announce touchdowns, big plays, and other key moments."""
        key_moments = []
        
        for i, play in enumerate(drive_plays, 1):
            yardage = play.get('yardage', 0)
            description = play.get('description', '')
            
            # Check for touchdown
            if 'touchdown' in description.lower() or play.get('isScoringPlay', False):
                key_moments.append(f"Play {i}: Touchdown!")
            # Check for big play (20+ yards)
            elif yardage >= 20:
                key_moments.append(f"Play {i}: Big play! {yardage} yards!")
            # Check for turnover
            elif 'fumble' in description.lower() or 'interception' in description.lower():
                key_moments.append(f"Play {i}: Turnover!")
        
        # Announce key moments
        if key_moments:
            for moment in key_moments:
                self.speak(moment)
    
    def set_preference(self, key: str, value: bool):
        """Update user preferences."""
        if key in self.preferences:
            self.preferences[key] = value
            print(f"Preference '{key}' set to {value}")
        else:
            print(f"Unknown preference: {key}")
    
    def get_preferences(self) -> Dict[str, bool]:
        """Get current preferences."""
        return self.preferences.copy()
    
    def cleanup(self):
        """Clean up resources."""
        self.audio_player.cleanup()
        if self.tts_available:
            try:
                self.tts_engine.stop()
            except:
                pass


# Example usage
if __name__ == "__main__":
    player = HybridAudioPlayer()
    
    print("\n=== Testing Hybrid Audio Player ===\n")
    
    # Test 1: Single play with narration
    print("Test 1: Single play with narration")
    play = {
        'description': 'QB pass complete to WR for 15 yards',
        'yardage': 15,
        'type': 'pass',
        'yardsToEndzone': 65,
        'down': 2,
        'distance': 8
    }
    player.play_single_play(play, with_narration=True)
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Drive sequence
    print("Test 2: Drive sequence (3 plays)")
    drive = [
        {'description': 'RB rush for 4 yards', 'yardage': 4, 'type': 'rush', 'yardsToEndzone': 75},
        {'description': 'QB pass complete for 22 yards', 'yardage': 22, 'type': 'pass', 'yardsToEndzone': 71},
        {'description': 'RB rush for touchdown', 'yardage': 10, 'type': 'rush', 'yardsToEndzone': 10, 'isScoringPlay': True},
    ]
    player.play_drive_sequence(drive, mode='sequence')
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Tutorial mode
    print("Test 3: Tutorial mode (1 play)")
    tutorial_play = [
        {'description': 'QB pass for 8 yards', 'yardage': 8, 'type': 'pass', 'yardsToEndzone': 55},
    ]
    player.play_drive_sequence(tutorial_play, mode='tutorial')
    
    player.cleanup()
    print("\n=== Tests Complete ===")
