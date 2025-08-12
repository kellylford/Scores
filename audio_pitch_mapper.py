#!/usr/bin/env python3
"""
Audio Pitch Map System - Spatial Audio for Baseball Pitch Locations
===============================================================
Converts pitch coordinate data into spatial audio feedback for enhanced accessibility
"""

import math
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QAudioFormat, QAudioSink
from PyQt6.QtCore import QByteArray, QIODevice, QBuffer
import struct

class AudioPitchMapper(QObject):
    """Core audio mapping system for pitch coordinates"""
    
    # Signals for audio feedback
    audio_generated = pyqtSignal(str)  # Emitted when audio is generated
    audio_error = pyqtSignal(str)      # Emitted on audio errors
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sample_rate = 44100  # Standard sample rate
        self.duration = 0.5       # Audio duration in seconds
        self.volume = 0.3         # Default volume
        
        # Initialize audio system
        self.audio_output = None
        self.audio_sink = None
        self.setup_audio()
        
    def setup_audio(self):
        """Initialize the audio output system"""
        try:
            # Set up audio format
            self.audio_format = QAudioFormat()
            self.audio_format.setSampleRate(self.sample_rate)
            self.audio_format.setChannelCount(2)  # Stereo
            self.audio_format.setSampleFormat(QAudioFormat.SampleFormat.Float)
            
            # Create audio output
            self.audio_output = QAudioOutput()
            self.audio_output.setVolume(self.volume)
            
        except Exception as e:
            self.audio_error.emit(f"Audio setup failed: {str(e)}")
    
    def coordinate_to_audio_params(self, x, y, velocity=None, pitch_type=None, batter_hand=None):
        """Convert pitch coordinates to audio parameters
        
        Args:
            x (int): Horizontal coordinate (0-255, ESPN system)
            y (int): Vertical coordinate (0-255, ESPN system) 
            velocity (int): Pitch velocity in mph
            pitch_type (str): Type of pitch (fastball, slider, etc.)
            batter_hand (str): 'L' or 'R' for left/right handed batter
            
        Returns:
            dict: Audio parameters for spatial audio generation
        """
        
        # Coordinate ranges based on our validated system
        x_min, x_max = 0, 255
        y_min, y_max = 0, 255
        
        # Normalize coordinates to 0-1 range
        x_norm = max(0, min(1, (x - x_min) / (x_max - x_min)))
        y_norm = max(0, min(1, (y - y_min) / (y_max - y_min)))
        
        # === SPATIAL AUDIO MAPPING ===
        
        # 1. STEREO PANNING (Left/Right positioning)
        # Based on batter handedness - inside pitches go to batter's side
        if batter_hand == 'L':  # Left-handed batter
            # Lower X = outside (right audio), Higher X = inside (left audio)
            pan = x_norm  # 0 = right, 1 = left
        else:  # Right-handed batter (default)
            # Lower X = inside (left audio), Higher X = outside (right audio)  
            pan = 1 - x_norm  # 0 = left, 1 = right
            
        # 2. FREQUENCY MAPPING (High/Low positioning)
        # Higher Y = lower pitch (lower frequency)
        # Lower Y = higher pitch (higher frequency)
        base_freq = 440  # A4 note
        freq_range = 400  # +/- 200 Hz range
        frequency = base_freq + (freq_range * (0.5 - y_norm))
        
        # 3. VELOCITY MAPPING (Tempo/Attack)
        if velocity:
            # 60-105 mph typical range
            velocity_norm = max(0, min(1, (velocity - 60) / 45))
            attack_time = 0.1 - (velocity_norm * 0.08)  # Faster = sharper attack
            sustain_time = 0.2 + (velocity_norm * 0.1)   # Faster = longer sustain
        else:
            attack_time = 0.05
            sustain_time = 0.25
            
        # 4. PITCH TYPE SOUND CHARACTER
        waveform_type = self._get_waveform_for_pitch_type(pitch_type)
        
        return {
            'frequency': frequency,
            'pan': pan,  # 0.0 = left, 0.5 = center, 1.0 = right
            'attack_time': attack_time,
            'sustain_time': sustain_time,
            'waveform': waveform_type,
            'velocity': velocity,
            'coordinates': (x, y)
        }
    
    def _get_waveform_for_pitch_type(self, pitch_type):
        """Map pitch types to distinctive waveforms"""
        if not pitch_type:
            return 'sine'
            
        pitch_type_lower = pitch_type.lower()
        
        if 'fastball' in pitch_type_lower or 'four-seam' in pitch_type_lower:
            return 'sine'      # Clean, pure tone
        elif 'slider' in pitch_type_lower:
            return 'sawtooth'  # Sharp, cutting sound
        elif 'curve' in pitch_type_lower or 'curveball' in pitch_type_lower:
            return 'triangle'  # Softer, rounded sound
        elif 'change' in pitch_type_lower or 'changeup' in pitch_type_lower:
            return 'sine_soft' # Muted sine wave
        elif 'sinker' in pitch_type_lower:
            return 'square'    # Heavy, solid sound
        elif 'cutter' in pitch_type_lower:
            return 'sawtooth_soft'  # Sharp but controlled
        else:
            return 'sine'      # Default
    
    def generate_pitch_audio(self, x, y, velocity=None, pitch_type=None, batter_hand=None):
        """Generate audio for a pitch location
        
        Args:
            x, y: Pitch coordinates 
            velocity: Pitch velocity in mph
            pitch_type: Type of pitch
            batter_hand: Batter handedness ('L'/'R')
        """
        try:
            # Get audio parameters
            params = self.coordinate_to_audio_params(x, y, velocity, pitch_type, batter_hand)
            
            # Generate waveform
            audio_data = self._generate_waveform(params)
            
            # Play audio
            self._play_audio_data(audio_data)
            
            # Emit feedback signal
            location_desc = self._get_location_description(x, y, batter_hand)
            self.audio_generated.emit(f"Playing pitch audio: {location_desc}")
            
        except Exception as e:
            self.audio_error.emit(f"Audio generation failed: {str(e)}")
    
    def _generate_waveform(self, params):
        """Generate audio waveform based on parameters"""
        
        frequency = params['frequency']
        pan = params['pan']
        attack_time = params['attack_time'] 
        sustain_time = params['sustain_time']
        waveform_type = params['waveform']
        
        # Calculate sample counts
        total_samples = int(self.sample_rate * self.duration)
        attack_samples = int(self.sample_rate * attack_time)
        sustain_samples = int(self.sample_rate * sustain_time)
        release_samples = total_samples - attack_samples - sustain_samples
        
        # Generate base waveform
        t = np.linspace(0, self.duration, total_samples, False)
        
        if waveform_type == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        elif waveform_type == 'sine_soft':
            wave = 0.7 * np.sin(2 * np.pi * frequency * t)
        elif waveform_type == 'sawtooth':
            wave = 2 * (t * frequency % 1) - 1
        elif waveform_type == 'sawtooth_soft':
            wave = 0.8 * (2 * (t * frequency % 1) - 1)
        elif waveform_type == 'triangle':
            wave = 2 * np.abs(2 * (t * frequency % 1) - 1) - 1
        elif waveform_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        else:
            wave = np.sin(2 * np.pi * frequency * t)  # Default sine
        
        # Apply envelope (attack, sustain, release)
        envelope = np.ones(total_samples)
        
        # Attack phase (fade in)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Release phase (fade out)
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(1, 0, release_samples)
        
        # Apply envelope to waveform
        wave *= envelope
        
        # Create stereo audio with panning
        left_gain = math.cos(pan * math.pi / 2)   # Left channel gain
        right_gain = math.sin(pan * math.pi / 2)  # Right channel gain
        
        # Create stereo array (interleaved L,R samples)
        stereo_wave = np.zeros(total_samples * 2)
        stereo_wave[0::2] = wave * left_gain   # Left channel
        stereo_wave[1::2] = wave * right_gain  # Right channel
        
        # Apply master volume
        stereo_wave *= self.volume
        
        # Convert to bytes for audio output
        audio_bytes = (stereo_wave * 32767).astype(np.int16).tobytes()
        
        return audio_bytes
    
    def _play_audio_data(self, audio_data):
        """Play generated audio data"""
        try:
            # Create QByteArray from audio data
            byte_array = QByteArray(audio_data)
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.OpenModeFlag.ReadOnly)
            
            # Create audio sink if needed
            if not self.audio_sink:
                self.audio_sink = QAudioSink(self.audio_format)
            
            # Play audio
            self.audio_sink.start(buffer)
            
            # Schedule buffer cleanup
            QTimer.singleShot(int(self.duration * 1000 + 100), lambda: buffer.deleteLater())
            
        except Exception as e:
            self.audio_error.emit(f"Audio playback failed: {str(e)}")
    
    def _get_location_description(self, x, y, batter_hand):
        """Get text description of pitch location for feedback"""
        
        # Use our validated coordinate interpretation
        if batter_hand == 'L':  # Left-handed batter
            if x < 50:
                horizontal = "way outside"
            elif x < 100:
                horizontal = "outside"
            elif x < 155:
                horizontal = "over the plate"
            elif x < 205:
                horizontal = "inside"
            else:
                horizontal = "way inside"
        else:  # Right-handed batter
            if x < 50:
                horizontal = "way inside"
            elif x < 100:
                horizontal = "inside"
            elif x < 155:
                horizontal = "over the plate"
            elif x < 205:
                horizontal = "outside"
            else:
                horizontal = "way outside"
        
        # Vertical positioning
        if y < 80:
            vertical = "high"
        elif y < 150:
            vertical = "middle"
        elif y < 200:
            vertical = "low"
        else:
            vertical = "very low"
            
        return f"{vertical} and {horizontal}"
    
    def set_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.audio_output:
            self.audio_output.setVolume(self.volume)
    
    def test_audio_mapping(self):
        """Test the audio mapping with sample coordinates"""
        print("Testing Audio Pitch Mapping...")
        
        test_pitches = [
            (127, 115, 95, "Four-Seam Fastball", "R"),  # Center strike
            (28, 199, 94, "Sinker", "R"),               # Lindor HBP 
            (80, 60, 88, "Slider", "L"),                # High outside to lefty
            (200, 180, 82, "Curveball", "R"),           # Low inside to righty
        ]
        
        for x, y, velo, ptype, hand in test_pitches:
            print(f"\nPitch: {ptype} {velo}mph to {hand}HB at ({x},{y})")
            params = self.coordinate_to_audio_params(x, y, velo, ptype, hand)
            print(f"Audio: {params['frequency']:.1f}Hz, pan={params['pan']:.2f}, {params['waveform']}")
            
            # Generate audio
            self.generate_pitch_audio(x, y, velo, ptype, hand)

if __name__ == "__main__":
    # Test the audio system
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    mapper = AudioPitchMapper()
    mapper.test_audio_mapping()
    
    # Keep app running for audio playback
    QTimer.singleShot(5000, app.quit)  # Quit after 5 seconds
    app.exec()
