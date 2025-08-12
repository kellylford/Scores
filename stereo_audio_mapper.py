#!/usr/bin/env python3
"""
Stereo Audio Pitch Mapper - True Stereo Implementation
======================================================
Uses wave module to generate stereo WAV files for true left/right audio
"""

import math
import wave
import struct
import tempfile
import os
import platform
from PyQt6.QtCore import QObject, pyqtSignal

# Windows audio playback
if platform.system() == "Windows":
    try:
        import winsound
        WINSOUND_AVAILABLE = True
    except ImportError:
        WINSOUND_AVAILABLE = False
else:
    WINSOUND_AVAILABLE = False

class StereoAudioPitchMapper(QObject):
    """True stereo audio mapping system using WAV file generation"""
    
    # Signals for audio feedback
    audio_generated = pyqtSignal(str)
    audio_error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = True  # WAV generation always available
        self.temp_files = []  # Track temp files for cleanup
        
    def generate_pitch_audio(self, x, y, velocity=None, pitch_type=None, batter_hand=None):
        """Generate true stereo audio for a pitch location"""
        
        try:
            # Convert coordinates to audio parameters
            frequency, duration, balance, location_desc = self._coordinate_to_audio_params(
                x, y, velocity, pitch_type, batter_hand
            )
            
            # Generate and play stereo audio
            self._play_stereo_beep(frequency, duration, balance)
            
            # Emit feedback
            balance_desc = self._get_balance_description(balance)
            self.audio_generated.emit(f"Stereo Audio: {location_desc} {balance_desc}")
            
        except Exception as e:
            self.audio_error.emit(f"Stereo audio generation failed: {str(e)}")
    
    def _coordinate_to_audio_params(self, x, y, velocity=None, pitch_type=None, batter_hand=None):
        """Convert pitch coordinates to audio parameters"""
        
        # Coordinate ranges
        x_min, x_max = 0, 255
        y_min, y_max = 0, 255
        
        # Normalize coordinates
        x_norm = max(0, min(1, (x - x_min) / (x_max - x_min)))
        y_norm = max(0, min(1, (y - y_min) / (y_max - y_min)))
        
        # Frequency mapping (high/low)
        base_freq = 800
        freq_range = 600
        frequency = base_freq + (freq_range * (0.5 - y_norm))
        frequency = max(200, min(2000, int(frequency)))
        
        # Duration mapping (velocity)
        if velocity:
            velocity_norm = max(0, min(1, (velocity - 60) / 45))
            duration = 0.3 + (0.4 * (1 - velocity_norm))  # 0.3-0.7 seconds
        else:
            duration = 0.5  # Default duration
        
        # Stereo balance (left/right)
        balance = x_norm  # 0.0 = full left, 0.5 = center, 1.0 = full right
        
        # Location description
        location_desc = self._get_location_description(x, y, batter_hand)
        
        return frequency, duration, balance, location_desc
    
    def _play_stereo_beep(self, frequency, duration, balance):
        """Generate and play a stereo WAV file with proper left/right balance"""
        
        try:
            # Audio parameters
            sample_rate = 44100
            samples = int(sample_rate * duration)
            
            # Calculate left and right volumes based on balance
            # balance: 0.0 = full left, 0.5 = center, 1.0 = full right
            left_volume = math.cos(balance * math.pi / 2)    # 1.0 at balance=0, 0.0 at balance=1
            right_volume = math.sin(balance * math.pi / 2)   # 0.0 at balance=0, 1.0 at balance=1
            
            # Generate stereo audio data
            audio_data = []
            for i in range(samples):
                # Generate sine wave
                t = i / sample_rate
                sample_value = math.sin(2 * math.pi * frequency * t)
                
                # Apply envelope (fade in/out to avoid clicks)
                envelope = 1.0
                if i < sample_rate * 0.05:  # 50ms fade in
                    envelope = i / (sample_rate * 0.05)
                elif i > samples - sample_rate * 0.05:  # 50ms fade out
                    envelope = (samples - i) / (sample_rate * 0.05)
                
                sample_value *= envelope
                
                # Apply stereo balance and convert to 16-bit integers
                left_sample = int(sample_value * left_volume * 32767)
                right_sample = int(sample_value * right_volume * 32767)
                
                # Pack as 16-bit signed integers (little endian)
                audio_data.append(struct.pack('<hh', left_sample, right_sample))
            
            # Create temporary WAV file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            self.temp_files.append(temp_file.name)
            
            # Write WAV file
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(2)      # Stereo
                wav_file.setsampwidth(2)      # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b''.join(audio_data))
            
            temp_file.close()
            
            # Play the WAV file
            if WINSOUND_AVAILABLE:
                winsound.PlaySound(temp_file.name, winsound.SND_FILENAME)
            else:
                print(f"Would play stereo WAV: {temp_file.name}")
                print(f"  Frequency: {frequency}Hz, Duration: {duration}s")
                print(f"  Balance: {balance:.2f} (L:{left_volume:.2f}, R:{right_volume:.2f})")
            
        except Exception as e:
            raise Exception(f"Stereo audio generation failed: {str(e)}")
    
    def _get_balance_description(self, balance):
        """Get description of stereo balance"""
        if balance < 0.2:
            return "(far left)"
        elif balance < 0.4:
            return "(left)"
        elif balance < 0.6:
            return "(center)"
        elif balance < 0.8:
            return "(right)"
        else:
            return "(far right)"
    
    def _get_location_description(self, x, y, batter_hand):
        """Get text description of pitch location"""
        
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
    
    def generate_strike_zone_audio(self, zone_position, batter_hand='R'):
        """Generate audio for specific strike zone positions"""
        
        # Define the 9 strike zone positions with wider X range for better stereo separation
        zone_coords = {
            'high_left': (50, 50),      # Further left for clear left audio
            'high_center': (127, 50),   # Dead center
            'high_right': (205, 50),    # Further right for clear right audio
            'center_left': (50, 127),   # Further left for clear left audio
            'center_center': (127, 127), # Dead center
            'center_right': (205, 127), # Further right for clear right audio
            'low_left': (50, 200),      # Further left for clear left audio
            'low_center': (127, 200),   # Dead center
            'low_right': (205, 200)     # Further right for clear right audio
        }
        
        if zone_position not in zone_coords:
            self.audio_error.emit(f"Unknown zone position: {zone_position}")
            return
            
        x, y = zone_coords[zone_position]
        self.generate_pitch_audio(x, y, velocity=90, pitch_type="Strike Zone", batter_hand=batter_hand)
    
    def cleanup(self):
        """Clean up temporary WAV files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass
        self.temp_files.clear()
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()

if __name__ == "__main__":
    # Test the stereo audio system
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    import sys
    import time
    
    app = QApplication(sys.argv)
    
    mapper = StereoAudioPitchMapper()
    
    print("Testing True Stereo Audio System")
    print("=" * 40)
    print("Make sure you have stereo headphones or speakers!")
    print()
    
    # Test left-center-right
    test_positions = [
        (50, 127, "Far Left"),
        (127, 127, "Center"), 
        (200, 127, "Far Right")
    ]
    
    for x, y, desc in test_positions:
        print(f"Playing: {desc}")
        mapper.generate_pitch_audio(x, y, velocity=90, pitch_type="Test", batter_hand='R')
        time.sleep(1.5)
    
    print("\nTesting complete!")
    print("You should have heard clear left-center-right positioning")
    
    # Cleanup and exit
    QTimer.singleShot(2000, app.quit)
    app.exec()
    
    mapper.cleanup()
