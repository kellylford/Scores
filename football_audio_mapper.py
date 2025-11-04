"""
Football Audio Mapper - Sonify NFL plays and drives
Maps play yardage, type, and game situation to audio frequencies and patterns
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PlayAudioConfig:
    """Configuration for a single play's audio"""
    frequency: float  # Hz
    duration: float   # seconds
    volume: float     # 0.0 to 1.0
    wave_type: str    # 'sine', 'square', 'sawtooth', 'triangle'
    attack: float     # seconds
    decay: float      # seconds
    field_position: Optional[float] = None  # 0-100, start position (0=left endzone, 50=center, 100=right endzone)
    end_field_position: Optional[float] = None  # 0-100, end position (for animated panning)
    play_type: Optional[str] = None  # For enhanced audio: 'rush', 'pass', 'touchdown', 'field_goal', 'sack', etc.
    
class FootballAudioMapper:
    """
    Maps NFL play data to audio parameters
    
    Philosophy:
    - Yardage maps to pitch (higher yards = higher pitch)
    - Play type affects timbre (wave shape)
    - Game situation affects volume/intensity
    - Drives create musical phrases
    """
    
    # Frequency ranges for different play outcomes
    FREQ_TOUCHDOWN = 880.0       # A5 - celebration
    FREQ_BIG_GAIN = 659.25       # E5 - 20+ yards
    FREQ_FIRST_DOWN = 523.25     # C5 - 10+ yards
    FREQ_GOOD_GAIN = 440.0       # A4 - 5-9 yards
    FREQ_SHORT_GAIN = 349.23     # F4 - 1-4 yards
    FREQ_NO_GAIN = 261.63        # C4 - 0 yards
    FREQ_LOSS = 196.0            # G3 - negative yards
    FREQ_TURNOVER = 130.81       # C3 - interception/fumble
    
    # Play type wave forms
    WAVE_RUSH = 'square'         # Percussive for running plays
    WAVE_PASS = 'sine'           # Smooth for passes
    WAVE_KICK = 'triangle'       # Special teams
    WAVE_SCORE = 'sawtooth'      # Scoring plays (bright)
    WAVE_TURNOVER = 'square'     # Negative events
    
    def __init__(self):
        """Initialize the football audio mapper"""
        self.base_duration = 0.3  # seconds per play
        self.base_volume = 0.6
        
    def map_play_to_audio(self, play: Dict) -> PlayAudioConfig:
        """
        Convert a single play to audio parameters
        
        Args:
            play: Play data from ESPN API with keys like:
                - statYardage: Yards gained/lost
                - type: {text: 'Rush', 'Pass Reception', etc.}
                - scoringPlay: Boolean
                - start/end: Field position data
                
        Returns:
            PlayAudioConfig with audio parameters
        """
        yardage = play.get('statYardage', 0)
        play_type = play.get('type', {}).get('text', '')
        is_scoring = play.get('scoringPlay', False)
        score_value = play.get('scoreValue', 0)
        
        # Determine frequency based on yardage and scoring
        frequency = self._yardage_to_frequency(yardage, is_scoring, score_value)
        
        # Determine wave type based on play type
        wave_type = self._play_type_to_wave(play_type, is_scoring)
        
        # Duration based on significance
        duration = self._calculate_duration(yardage, is_scoring)
        
        # Volume based on game situation and play importance
        volume = self._calculate_volume(play, yardage, is_scoring)
        
        # Envelope (attack/decay) for expressiveness
        attack, decay = self._calculate_envelope(play_type, is_scoring)
        
        # Calculate field position for stereo panning (start and end)
        field_position = self._calculate_field_position(play)
        end_field_position = self._calculate_end_field_position(play, yardage)
        
        return PlayAudioConfig(
            frequency=frequency,
            duration=duration,
            volume=volume,
            wave_type=wave_type,
            attack=attack,
            decay=decay,
            field_position=field_position,
            end_field_position=end_field_position
        )
    
    def _yardage_to_frequency(self, yardage: int, is_scoring: bool, score_value: int) -> float:
        """
        Map yardage to frequency
        
        Scale: Bigger plays = higher pitches
        Special handling for scores and turnovers
        """
        if is_scoring and score_value > 0:
            # Touchdown or field goal
            return self.FREQ_TOUCHDOWN
        elif 'interception' in str(yardage).lower() or 'fumble' in str(yardage).lower():
            # Turnover
            return self.FREQ_TURNOVER
        elif yardage >= 40:
            # Huge play - really high
            return self.FREQ_TOUCHDOWN
        elif yardage >= 20:
            # Big play
            return self.FREQ_BIG_GAIN
        elif yardage >= 10:
            # First down range
            return self.FREQ_FIRST_DOWN
        elif yardage >= 5:
            # Good gain
            return self.FREQ_GOOD_GAIN
        elif yardage >= 1:
            # Short gain
            return self.FREQ_SHORT_GAIN
        elif yardage == 0:
            # No gain
            return self.FREQ_NO_GAIN
        else:
            # Loss - map negative yards to lower frequencies
            # -1 to -10 yards maps to range below NO_GAIN
            freq = self.FREQ_LOSS - (abs(yardage) * 10)
            return max(freq, 100.0)  # Don't go too low
    
    def _play_type_to_wave(self, play_type: str, is_scoring: bool) -> str:
        """Map play type to waveform"""
        if is_scoring:
            return self.WAVE_SCORE
        
        play_lower = play_type.lower()
        
        if 'rush' in play_lower or 'run' in play_lower:
            return self.WAVE_RUSH
        elif 'pass' in play_lower or 'reception' in play_lower:
            return self.WAVE_PASS
        elif 'kick' in play_lower or 'punt' in play_lower:
            return self.WAVE_KICK
        elif 'interception' in play_lower or 'fumble' in play_lower:
            return self.WAVE_TURNOVER
        elif 'sack' in play_lower:
            return self.WAVE_TURNOVER
        else:
            return 'sine'  # Default
    
    def _calculate_duration(self, yardage: int, is_scoring: bool) -> float:
        """
        Calculate note duration based on play significance
        Bigger plays = longer notes
        """
        if is_scoring:
            return self.base_duration * 3.0  # Long celebration
        elif abs(yardage) >= 20:
            return self.base_duration * 2.0  # Big play
        elif abs(yardage) >= 10:
            return self.base_duration * 1.5  # First down
        else:
            return self.base_duration
    
    def _calculate_volume(self, play: Dict, yardage: int, is_scoring: bool) -> float:
        """
        Calculate volume based on play importance and game situation
        """
        volume = self.base_volume
        
        # Boost for big plays
        if is_scoring:
            volume = 1.0
        elif abs(yardage) >= 20:
            volume = 0.9
        elif abs(yardage) >= 10:
            volume = 0.8
        
        # Boost for critical downs
        end_data = play.get('end', {})
        down = end_data.get('down', 0)
        if down == 3 or down == 4:
            volume = min(volume * 1.2, 1.0)
        
        # Boost for red zone (inside 20)
        yards_to_endzone = end_data.get('yardsToEndzone', 100)
        if yards_to_endzone <= 20:
            volume = min(volume * 1.1, 1.0)
        
        return volume
    
    def _calculate_envelope(self, play_type: str, is_scoring: bool) -> Tuple[float, float]:
        """
        Calculate attack and decay times for note envelope
        
        Returns:
            (attack, decay) in seconds
        """
        play_lower = play_type.lower()
        
        if is_scoring:
            # Scoring plays: slow attack, long decay for celebration
            return (0.1, 0.5)
        elif 'rush' in play_lower:
            # Quick attack for running plays
            return (0.01, 0.1)
        elif 'pass' in play_lower:
            # Moderate attack for passes
            return (0.05, 0.15)
        elif 'kick' in play_lower or 'punt' in play_lower:
            # Sustained for kicks
            return (0.05, 0.2)
        else:
            # Default
            return (0.05, 0.1)
    
    def _calculate_field_position(self, play: Dict) -> Optional[float]:
        """
        Calculate field position for stereo panning based on play data
        
        Maps field position to 0-100 scale for stereo positioning:
        - 0 = left speaker (team's own endzone)
        - 50 = center (midfield)
        - 100 = right speaker (opponent's endzone)
        
        Args:
            play: Play data from ESPN API
            
        Returns:
            Field position 0-100, or None if position can't be determined
        """
        # Try to get starting field position
        start = play.get('start', {})
        yards_to_endzone = start.get('yardsToEndzone')
        
        if yards_to_endzone is not None:
            # yardsToEndzone is distance to opponent's endzone (0-100)
            # Convert to 0-100 scale where 100 = opponent's endzone
            # No enhancement multiplier - use raw position for accurate stereo
            # The audio_player.py stereo panning handles the spatial effect
            field_position = 100 - yards_to_endzone
            
            # Clamp to valid range 0-100 (should already be in range, but just in case)
            result = max(0, min(100, field_position))
            
            # Log to file
            with open('drive_audio_debug.log', 'a') as log:
                log.write(f"  [FIELD_POS] yardsToEndzone={yards_to_endzone} -> position={result:.1f}\n")
            
            print(f"Debug: Field position calc - yardsToEndzone={yards_to_endzone} -> position={result:.1f}")
            return result
        
        # Fallback: try to parse field position from play text
        text = play.get('text', '').lower()
        
        # Look for yard line references like "to MIN 32" or "at DAL 15"
        import re
        
        # Pattern for "to TEAM XX" or "at TEAM XX" 
        yard_pattern = r'(?:to|at)\s+[a-z]{2,4}\s+(\d+)'
        match = re.search(yard_pattern, text)
        
        if match:
            yard_line = int(match.group(1))
            # Assume this is yards from the team's own goal line
            # Convert to 0-100 scale
            return min(100, yard_line)
        
        # If we can't determine position, return center field
        return 50.0
    
    def _calculate_end_field_position(self, play: Dict, yardage: int) -> Optional[float]:
        """
        Calculate ending field position after the play completes.
        This creates animated stereo panning from start to end position.
        
        Args:
            play: Play data from ESPN API
            yardage: Yards gained/lost on the play
            
        Returns:
            End field position 0-100, or None if can't be determined
        """
        # Get the starting position
        start_position = self._calculate_field_position(play)
        if start_position is None:
            return None
        
        # Try to get end position from play data (if available)
        end = play.get('end', {})
        end_yards_to_endzone = end.get('yardsToEndzone')
        
        if end_yards_to_endzone is not None:
            # Use actual end position from API
            end_position = 100 - end_yards_to_endzone
            result = max(0, min(100, end_position))
            print(f"Debug: End position from API - yardsToEndzone={end_yards_to_endzone} -> position={result:.1f}")
            return result
        
        # Calculate end position from start + yardage
        # Convert start position (0-100) to yards to endzone
        start_yards_to_endzone = 100 - start_position
        
        # Subtract yardage (positive yardage moves toward endzone, negative moves away)
        end_yards_to_endzone = start_yards_to_endzone - yardage
        
        # Clamp to field boundaries
        end_yards_to_endzone = max(0, min(100, end_yards_to_endzone))
        
        # Convert back to 0-100 position
        end_position = 100 - end_yards_to_endzone
        
        print(f"Debug: End position calculated - yardage={yardage}, start={start_position:.1f} -> end={end_position:.1f}")
        return end_position
    
    def map_drive_to_audio_sequence(self, drive: Dict) -> List[PlayAudioConfig]:
        """
        Map an entire drive to a sequence of audio configs
        
        This creates a "musical phrase" from a drive
        
        Args:
            drive: Drive data with 'plays' list
            
        Returns:
            List of PlayAudioConfig objects
        """
        plays = drive.get('plays', [])
        audio_sequence = []
        
        print(f"\n=== DEBUG: Processing drive with {len(plays)} total plays ===")
        
        for i, play in enumerate(plays, 1):
            # Skip non-action plays (timeouts, penalties, warnings, quarter ends, etc.)
            play_type = play.get('type', {}).get('text', '').lower()
            play_text = play.get('text', '').lower()
            stat_yardage = play.get('statYardage')
            
            print(f"Play {i}: type='{play_type}', yardage={stat_yardage}, text='{play_text[:50]}'")
            
            # Skip administrative plays without actual field action
            skip_keywords = ['timeout', 'penalty', 'warning', 'end quarter', 'end half', 
                           'end game', 'two-minute warning', 'coin toss']
            
            if any(keyword in play_type for keyword in skip_keywords):
                print(f"  -> SKIPPED (type has skip keyword)")
                continue
            if any(keyword in play_text for keyword in skip_keywords):
                print(f"  -> SKIPPED (text has skip keyword)")
                continue
            
            # Skip plays with no yardage (likely administrative)
            # BUT: Include plays with 0 yardage if they have a real play type (like incomplete pass, sack)
            if stat_yardage is None or stat_yardage == 0:
                # Check if it's a real play with a type (pass/rush/kick/sack)
                if not any(action in play_type for action in ['pass', 'rush', 'run', 'kick', 'punt', 'field goal', 'sack']):
                    print(f"  -> SKIPPED (no/zero yardage and not a real play type)")
                    continue
                else:
                    print(f"  -> KEPT despite 0 yardage (has real play type: {play_type})")
            
            print(f"  -> INCLUDED in audio sequence")
            config = self.map_play_to_audio(play)
            audio_sequence.append(config)
        
        print(f"=== Result: {len(audio_sequence)} plays in audio sequence ===\n")
        return audio_sequence
    
    def get_drive_summary(self, drive: Dict) -> Dict:
        """
        Get a text summary of drive audio characteristics
        
        Useful for UI display
        """
        plays = drive.get('plays', [])
        total_plays = len(plays)
        
        # Count play types
        rushes = sum(1 for p in plays if 'rush' in p.get('type', {}).get('text', '').lower())
        passes = sum(1 for p in plays if 'pass' in p.get('type', {}).get('text', '').lower())
        
        # Calculate total yardage
        total_yards = sum(p.get('statYardage', 0) for p in plays)
        
        # Check for scoring
        scoring_play = any(p.get('scoringPlay', False) for p in plays)
        
        # Get drive result - can be string or dict
        result_data = drive.get('result', 'Unknown')
        if isinstance(result_data, dict):
            drive_result = result_data.get('text', 'Unknown')
        else:
            drive_result = str(result_data)
        
        return {
            'total_plays': total_plays,
            'rushes': rushes,
            'passes': passes,
            'total_yards': total_yards,
            'scoring': scoring_play,
            'result': drive_result,
            'duration_estimate': total_plays * self.base_duration
        }
    
    def create_game_flow_audio(self, all_drives: List[Dict], team_id: str = None) -> List[PlayAudioConfig]:
        """
        Create audio for an entire game or one team's drives
        
        Args:
            all_drives: List of drive dictionaries
            team_id: Optional team ID to filter (only that team's drives)
            
        Returns:
            Complete audio sequence for the game/team
        """
        audio_sequence = []
        
        for drive in all_drives:
            # Filter by team if requested
            if team_id and drive.get('team', {}).get('id') != team_id:
                continue
            
            # Add drive's plays
            drive_audio = self.map_drive_to_audio_sequence(drive)
            audio_sequence.extend(drive_audio)
            
            # Add brief silence between drives
            silence = PlayAudioConfig(
                frequency=0,
                duration=0.2,
                volume=0,
                wave_type='sine',
                attack=0,
                decay=0
            )
            audio_sequence.append(silence)
        
        return audio_sequence
    
    def get_interesting_plays(self, drives: List[Dict], min_yards: int = 20) -> List[Dict]:
        """
        Extract interesting/big plays from drives
        
        Useful for creating highlight reels
        
        Args:
            drives: List of drive dictionaries
            min_yards: Minimum yardage to be considered "interesting"
            
        Returns:
            List of play dictionaries
        """
        interesting = []
        
        for drive in drives:
            for play in drive.get('plays', []):
                yardage = play.get('statYardage', 0)
                is_scoring = play.get('scoringPlay', False)
                play_type = play.get('type', {}).get('text', '').lower()
                
                # Big plays
                if abs(yardage) >= min_yards:
                    interesting.append(play)
                # Scoring plays
                elif is_scoring:
                    interesting.append(play)
                # Turnovers
                elif 'interception' in play_type or 'fumble' in play_type:
                    interesting.append(play)
                # Sacks
                elif 'sack' in play_type:
                    interesting.append(play)
        
        return interesting


class FootballDrivePlayer:
    """
    Helper class to play back football drives with timing information
    Useful for UI integration
    """
    
    def __init__(self):
        self.mapper = FootballAudioMapper()
    
    def prepare_drive_playback(self, drive: Dict) -> Dict:
        """
        Prepare a drive for audio playback with timing
        
        Returns:
            Dictionary with audio configs and timing information
        """
        audio_sequence = self.mapper.map_drive_to_audio_sequence(drive)
        summary = self.mapper.get_drive_summary(drive)
        
        # Calculate timing for each play
        timing = []
        current_time = 0.0
        
        for i, config in enumerate(audio_sequence):
            timing.append({
                'start_time': current_time,
                'end_time': current_time + config.duration,
                'config': config
            })
            current_time += config.duration + 0.05  # Small gap between plays
        
        return {
            'audio_sequence': audio_sequence,
            'timing': timing,
            'summary': summary,
            'total_duration': current_time
        }
    
    def get_play_description(self, play: Dict, config: PlayAudioConfig) -> str:
        """
        Create a human-readable description of what the audio represents
        """
        yardage = play.get('statYardage', 0)
        play_type = play.get('type', {}).get('text', 'Play')
        text = play.get('text', '')
        
        # Truncate long descriptions
        if len(text) > 60:
            text = text[:57] + '...'
        
        return f"{play_type}: {yardage} yards | {config.frequency:.0f}Hz {config.wave_type} | {text}"


# Example usage and testing
if __name__ == "__main__":
    # Example play data (from ESPN API)
    example_plays = [
        {
            'statYardage': 16,
            'type': {'text': 'Pass Reception'},
            'scoringPlay': False,
            'text': 'C.Wentz pass deep left to J.Jefferson to MIN 32 for 16 yards',
            'end': {'down': 1, 'yardsToEndzone': 68}
        },
        {
            'statYardage': 2,
            'type': {'text': 'Rush'},
            'scoringPlay': False,
            'text': 'J.Mason left tackle to MIN 34 for 2 yards',
            'end': {'down': 2, 'yardsToEndzone': 66}
        },
        {
            'statYardage': 0,
            'type': {'text': 'Pass Incompletion'},
            'scoringPlay': False,
            'text': 'C.Wentz pass incomplete short right',
            'end': {'down': 3, 'yardsToEndzone': 66}
        },
        {
            'statYardage': 45,
            'type': {'text': 'Pass Reception'},
            'scoringPlay': True,
            'scoreValue': 6,
            'text': 'K.Vidal pass from Herbert for 45 yard touchdown!',
            'end': {'down': 0, 'yardsToEndzone': 0}
        }
    ]
    
    mapper = FootballAudioMapper()
    
    print("Football Audio Mapper Test")
    print("=" * 60)
    print()
    
    for i, play in enumerate(example_plays, 1):
        config = mapper.map_play_to_audio(play)
        print(f"Play {i}: {play['text'][:50]}")
        print(f"  Yardage: {play['statYardage']} yards")
        print(f"  Audio: {config.frequency:.1f}Hz {config.wave_type} wave")
        print(f"  Duration: {config.duration:.2f}s, Volume: {config.volume:.2f}")
        print(f"  Envelope: attack={config.attack:.3f}s, decay={config.decay:.3f}s")
        print()
    
    # Test drive sequence
    example_drive = {
        'plays': example_plays,
        'result': {'text': 'Touchdown'}
    }
    
    player = FootballDrivePlayer()
    playback_data = player.prepare_drive_playback(example_drive)
    
    print("\nDrive Summary:")
    print("=" * 60)
    summary = playback_data['summary']
    print(f"Total plays: {summary['total_plays']}")
    print(f"Rushes: {summary['rushes']}, Passes: {summary['passes']}")
    print(f"Total yards: {summary['total_yards']}")
    print(f"Scoring drive: {summary['scoring']}")
    print(f"Result: {summary['result']}")
    print(f"Audio duration: {playback_data['total_duration']:.2f} seconds")
