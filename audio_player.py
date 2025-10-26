"""
Audio synthesis and playback for football play audio.
Uses winsound (Windows built-in) for audio playback and numpy for wave generation.
Supports stereo panning to represent field position (left endzone to right endzone).
"""

import winsound
import numpy as np
import wave
import tempfile
import os
from typing import List, Optional
from football_audio_mapper import PlayAudioConfig


class AudioPlayer:
    """Generates and plays audio from PlayAudioConfig parameters with stereo panning."""
    
    SAMPLE_RATE = 44100  # CD quality
    
    def __init__(self):
        self.temp_files = []
        self.stereo_enabled = True  # Enable stereo field position audio
    
    def generate_tone(self, config: PlayAudioConfig, field_position: Optional[int] = None) -> np.ndarray:
        """
        Generate audio samples for a single play based on config.
        
        Args:
            config: PlayAudioConfig with frequency, wave_type, duration, volume, attack, decay
            field_position: Yard line (0-100, where 0=left endzone, 50=center, 100=right endzone)
            
        Returns:
            numpy array of audio samples (stereo if field_position provided, mono otherwise)
        """
        num_samples = int(self.SAMPLE_RATE * config.duration)
        t = np.linspace(0, config.duration, num_samples, False)
        
        # Generate base waveform
        if config.wave_type == 'sine':
            wave_data = np.sin(2 * np.pi * config.frequency * t)
        elif config.wave_type == 'square':
            wave_data = np.sign(np.sin(2 * np.pi * config.frequency * t))
        elif config.wave_type == 'sawtooth':
            wave_data = 2 * (t * config.frequency - np.floor(t * config.frequency + 0.5))
        elif config.wave_type == 'triangle':
            wave_data = 2 * np.abs(2 * (t * config.frequency - np.floor(t * config.frequency + 0.5))) - 1
        else:
            # Default to sine
            wave_data = np.sin(2 * np.pi * config.frequency * t)
        
        # Apply volume
        wave_data = wave_data * config.volume
        
        # Apply attack/decay envelope
        envelope = np.ones(num_samples)
        
        # Attack (fade in)
        attack_samples = int(self.SAMPLE_RATE * config.attack)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay (fade out)
        decay_samples = int(self.SAMPLE_RATE * config.decay)
        if decay_samples > 0:
            envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)
        
        wave_data = wave_data * envelope
        
        # Apply stereo panning if field position provided
        if field_position is not None and self.stereo_enabled:
            left_channel, right_channel = self._apply_stereo_pan(wave_data, field_position)
            # Stack channels: shape (num_samples, 2)
            stereo_data = np.column_stack([left_channel, right_channel])
            return stereo_data
        
        return wave_data
    
    def _apply_stereo_pan(self, mono_data: np.ndarray, field_position: int) -> tuple:
        """
        Apply stereo panning based on field position.
        
        Args:
            mono_data: Mono audio samples
            field_position: Yard line (0-100)
                           0 = Left endzone (sound from left)
                           50 = Midfield (sound centered)
                           100 = Right endzone (sound from right)
        
        Returns:
            (left_channel, right_channel) tuple
        """
        # Normalize field position to -1.0 (left) to +1.0 (right)
        # 0 yards -> -1.0 (full left)
        # 50 yards -> 0.0 (center)
        # 100 yards -> +1.0 (full right)
        pan = (field_position - 50) / 50.0
        pan = np.clip(pan, -1.0, 1.0)
        
        # Calculate left/right volumes using equal power panning
        # This maintains constant perceived loudness across the stereo field
        angle = (pan + 1.0) * np.pi / 4  # Maps -1..1 to 0..pi/2
        left_volume = np.cos(angle)
        right_volume = np.sin(angle)
        
        left_channel = mono_data * left_volume
        right_channel = mono_data * right_volume
        
        return left_channel, right_channel
    
    def generate_silence(self, duration: float, stereo: bool = False) -> np.ndarray:
        """Generate silence for the specified duration."""
        num_samples = int(self.SAMPLE_RATE * duration)
        if stereo:
            return np.zeros((num_samples, 2))
        return np.zeros(num_samples)
    
    def play_audio_sequence(self, configs: List[PlayAudioConfig], silence_between: float = 0.1, 
                           field_positions: Optional[List[int]] = None):
        """
        Generate and play a sequence of audio configs (like a drive).
        
        Args:
            configs: List of PlayAudioConfig objects
            silence_between: Silence duration between plays (seconds)
            field_positions: List of yard line positions (0-100) for each play.
                           If provided, enables stereo panning.
        """
        if not configs:
            print("No audio to play!")
            return
        
        # Check if we have field positions
        if field_positions and len(field_positions) != len(configs):
            print(f"Warning: {len(configs)} configs but {len(field_positions)} positions. Disabling stereo.")
            field_positions = None
        
        # Determine if we're generating stereo
        is_stereo = field_positions is not None and self.stereo_enabled
        num_channels = 2 if is_stereo else 1
        
        # Generate all audio segments
        segments = []
        for i, config in enumerate(configs):
            field_pos = field_positions[i] if field_positions else None
            audio_data = self.generate_tone(config, field_position=field_pos)
            segments.append(audio_data)
            
            if silence_between > 0:
                silence = self.generate_silence(silence_between, stereo=is_stereo)
                segments.append(silence)
        
        # Remove trailing silence
        if silence_between > 0 and segments:
            segments.pop()
        
        # Concatenate all segments
        audio_data = np.concatenate(segments)
        
        # Normalize to prevent clipping
        if is_stereo:
            # Normalize each channel independently
            max_val = np.abs(audio_data).max()
            if max_val > 0:
                audio_data = audio_data / max_val
        else:
            max_val = np.abs(audio_data).max()
            if max_val > 0:
                audio_data = audio_data / max_val
        
        # Convert to 16-bit PCM
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Save to temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.temp_files.append(temp_file.name)
        
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.SAMPLE_RATE)
            wav_file.writeframes(audio_data.tobytes())
        
        # Play the audio
        stereo_msg = " (STEREO - listen for field position!)" if is_stereo else ""
        print(f"\nPlaying audio sequence ({len(configs)} plays){stereo_msg}...")
        try:
            winsound.PlaySound(temp_file.name, winsound.SND_FILENAME)
            print("Playback complete!")
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def play_single_play(self, config: PlayAudioConfig, field_position: Optional[int] = None):
        """Play audio for a single play."""
        field_positions = [field_position] if field_position is not None else None
        self.play_audio_sequence([config], silence_between=0, field_positions=field_positions)
    
    def cleanup(self):
        """Clean up temporary audio files."""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        self.temp_files = []
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()


def demo_audio():
    """Quick demo of audio playback with stereo field position."""
    from football_audio_mapper import FootballAudioMapper
    
    player = AudioPlayer()
    mapper = FootballAudioMapper()
    
    print("\n=== AUDIO PLAYBACK DEMO (with STEREO field position) ===\n")
    
    # Demo plays with field positions (simulating a drive)
    demo_plays = [
        {
            'text': 'J.Daniels rush up the middle for 3 yards',
            'statYardage': 3,
            'type': {'text': 'Rush'},
            'start': {'yardLine': 25}  # Starting at own 25
        },
        {
            'text': 'J.Daniels pass short right to T.McLaurin for 12 yards',
            'statYardage': 12,
            'type': {'text': 'Pass Reception'},
            'start': {'yardLine': 28}
        },
        {
            'text': 'J.Daniels pass deep left to Z.Ertz for 28 yards',
            'statYardage': 28,
            'type': {'text': 'Pass Reception'},
            'start': {'yardLine': 40}
        },
        {
            'text': 'B.Robinson Jr. rush left tackle for 7 yards TOUCHDOWN',
            'statYardage': 7,
            'type': {'text': 'Rush'},
            'scoringPlay': True,
            'scoreValue': 6,
            'start': {'yardLine': 68}
        }
    ]
    
    print("Playing a sample touchdown drive:\n")
    print("Listen with HEADPHONES to hear the team move down the field!")
    print("(Sound moves from left to right as they advance)\n")
    
    configs = []
    field_positions = []
    
    for i, play in enumerate(demo_plays, 1):
        config = mapper.map_play_to_audio(play)
        configs.append(config)
        
        # Extract field position
        field_pos = play.get('start', {}).get('yardLine', 50)
        field_positions.append(field_pos)
        
        print(f"{i}. Yard {field_pos:3d} | {play['statYardage']:+3d}yd | {play['text'][:60]}")
        print(f"   {config.frequency:.1f}Hz {config.wave_type} | {config.duration:.2f}s")
    
    print("\n" + "="*60)
    input("Press ENTER to play the audio sequence...")
    
    player.play_audio_sequence(configs, silence_between=0.15, field_positions=field_positions)
    
    player.cleanup()


if __name__ == '__main__':
    demo_audio()
