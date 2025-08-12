#!/usr/bin/env python3
"""
Simple Audio Pitch Map System - Windows Compatible with Stereo Option
======================================================================
Simple beep-based spatial audio for baseball pitch locations with optional true stereo
"""

import math
import platform
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

# Windows-specific audio
if platform.system() == "Windows":
    try:
        import winsound
        WINSOUND_AVAILABLE = True
    except ImportError:
        WINSOUND_AVAILABLE = False
else:
    WINSOUND_AVAILABLE = False

class SimpleAudioPitchMapper(QObject):
    """Simple audio mapping system with optional stereo support"""
    
    # Signals for audio feedback
    audio_generated = pyqtSignal(str)  # Emitted when audio is generated
    audio_error = pyqtSignal(str)      # Emitted on audio errors
    
    def __init__(self, parent=None, use_stereo=True):
        super().__init__(parent)
        self.enabled = WINSOUND_AVAILABLE
        self.use_stereo = use_stereo and self._check_stereo_support()
        
        # Initialize stereo mapper if available
        if self.use_stereo:
            try:
                from stereo_audio_mapper import StereoAudioPitchMapper
                # Use optimized L/R multiplier value from testing
                self.stereo_mapper = StereoAudioPitchMapper(parent, lr_multiplier=2.15)
                self.stereo_mapper.audio_generated.connect(self.audio_generated)
                self.stereo_mapper.audio_error.connect(self.audio_error)
            except ImportError:
                self.use_stereo = False
                self.stereo_mapper = None
        else:
            self.stereo_mapper = None
    
    def _check_stereo_support(self):
        """Check if stereo audio support is available"""
        try:
            import wave
            import struct
            import tempfile
            return True
        except ImportError:
            return False
        
    def generate_pitch_audio(self, x, y, velocity=None, pitch_type=None, batter_hand=None):
        """Generate audio for a pitch location - uses stereo if available, falls back to beeps
        
        Args:
            x, y: Pitch coordinates 
            velocity: Pitch velocity in mph
            pitch_type: Type of pitch
            batter_hand: Batter handedness ('L'/'R')
        """
        
        if not self.enabled:
            self.audio_error.emit("Audio system not available")
            return
        
        # Use stereo audio if available
        if self.use_stereo and self.stereo_mapper:
            try:
                self.stereo_mapper.generate_pitch_audio(x, y, velocity, pitch_type, batter_hand)
                return
            except Exception as e:
                # Fall back to simple beeps if stereo fails
                self.audio_error.emit(f"Stereo audio failed, using simple beeps: {str(e)}")
        
        # Fall back to simple beeps
        try:
            # Convert coordinates to audio parameters
            frequency, duration, balance, location_desc = self._coordinate_to_beep_params(
                x, y, velocity, pitch_type, batter_hand
            )
            
            # Play the beep with stereo balance simulation
            self._play_beep_with_balance(frequency, duration, balance)
            
            # Emit feedback
            balance_desc = self._get_balance_description(balance)
            self.audio_generated.emit(f"Audio: {location_desc} {balance_desc}")
            
        except Exception as e:
            self.audio_error.emit(f"Audio generation failed: {str(e)}")
    
    def _coordinate_to_beep_params(self, x, y, velocity=None, pitch_type=None, batter_hand=None):
        """Convert pitch coordinates to simple beep parameters with stereo balance"""
        
        # Coordinate ranges based on our validated system
        x_min, x_max = 0, 255
        y_min, y_max = 0, 255
        
        # Normalize coordinates to 0-1 range
        x_norm = max(0, min(1, (x - x_min) / (x_max - x_min)))
        y_norm = max(0, min(1, (y - y_min) / (y_max - y_min)))
        
        # === SIMPLE BEEP MAPPING ===
        
        # 1. FREQUENCY MAPPING (High/Low positioning)
        # Higher Y = lower pitch (lower frequency) 
        # Lower Y = higher pitch (higher frequency)
        base_freq = 800  # Base frequency
        freq_range = 600  # +/- 300 Hz range
        frequency = base_freq + (freq_range * (0.5 - y_norm))
        frequency = max(200, min(2000, int(frequency)))  # Clamp to audible range
        
        # 2. DURATION MAPPING (Velocity)
        if velocity:
            # 60-105 mph typical range - faster = shorter beep
            velocity_norm = max(0, min(1, (velocity - 60) / 45))
            duration = 200 + int(300 * (1 - velocity_norm))  # 200-500ms
        else:
            duration = 300  # Default duration
        
        # 3. STEREO BALANCE (Left/Right positioning)
        # x_norm: 0 = far left, 0.5 = center, 1 = far right
        balance = x_norm  # 0.0 = left speaker, 0.5 = center, 1.0 = right speaker
        
        # 4. LOCATION DESCRIPTION
        location_desc = self._get_location_description(x, y, batter_hand)
        
        return frequency, duration, balance, location_desc
    
    def _play_beep(self, frequency, duration):
        """Play a simple beep with the given frequency and duration (legacy method)"""
        self._play_beep_with_balance(frequency, duration, 0.5)  # Center balance

    def _play_beep_with_balance(self, frequency, duration, balance):
        """Play a beep with stereo balance simulation using multiple beeps"""
        if WINSOUND_AVAILABLE:
            try:
                # Since Windows winsound doesn't support true stereo,
                # we'll simulate left/right with distinct audio patterns
                
                if balance < 0.4:  # Left side - play two quick beeps (more aggressive threshold)
                    # Lower frequency for left
                    left_freq = max(200, min(2000, int(frequency - 100)))
                    winsound.Beep(left_freq, int(duration * 0.4))
                    # Very short pause
                    import time
                    time.sleep(0.05)
                    winsound.Beep(left_freq, int(duration * 0.4))
                    
                elif balance > 0.6:  # Right side - play one higher, longer beep (more aggressive threshold)
                    # Higher frequency for right
                    right_freq = max(200, min(2000, int(frequency + 100)))
                    winsound.Beep(right_freq, int(duration * 1.5))  # Even longer duration
                    
                else:  # Center - normal single beep
                    winsound.Beep(frequency, duration)
                    
            except Exception as e:
                self.audio_error.emit(f"Beep failed: {str(e)}")
        else:
            # Fallback - print what we would play
            if balance < 0.4:
                pattern = "LEFT (double beep)"
            elif balance > 0.6:
                pattern = "RIGHT (long beep)"
            else:
                pattern = "CENTER (single beep)"
            print(f"BEEP: {frequency}Hz for {duration}ms [{pattern}]")
    
    def _get_balance_description(self, balance):
        """Get description of stereo balance position with audio pattern info"""
        if balance < 0.4:
            return "(left - double beep)"
        elif balance > 0.6:
            return "(right - long beep)"
        else:
            return "(center - single beep)"
    
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
    
    def generate_strike_zone_audio(self, zone_position, batter_hand='R'):
        """Generate audio for specific strike zone positions
        
        Args:
            zone_position: String like "high_left", "center_center", "low_right"
            batter_hand: Batter handedness ('L'/'R')
        """
        
        # Use stereo audio if available
        if self.use_stereo and self.stereo_mapper:
            try:
                self.stereo_mapper.generate_strike_zone_audio(zone_position, batter_hand)
                return
            except Exception as e:
                self.audio_error.emit(f"Stereo strike zone audio failed: {str(e)}")
                # Fall through to simple beep version
        
        # Define the 9 strike zone positions using actual strike zone boundaries
        zone_coords = {
            'high_left': (100, 50),     # Actual left edge of strike zone
            'high_center': (127, 50),   # Dead center  
            'high_right': (155, 50),    # Actual right edge of strike zone
            'center_left': (100, 127),  # Actual left edge of strike zone
            'center_center': (127, 127), # Dead center
            'center_right': (155, 127), # Actual right edge of strike zone
            'low_left': (100, 200),     # Actual left edge of strike zone
            'low_center': (127, 200),   # Dead center
            'low_right': (155, 200)     # Actual right edge of strike zone
        }
        
        if zone_position not in zone_coords:
            self.audio_error.emit(f"Unknown zone position: {zone_position}")
            return
            
        x, y = zone_coords[zone_position]
        
        # Generate audio with standard velocity
        self.generate_pitch_audio(x, y, velocity=90, pitch_type="Strike Zone", batter_hand=batter_hand)
    
    def test_audio_mapping(self):
        """Test the audio mapping with sample coordinates"""
        print("Testing Simple Audio Pitch Mapping...")
        print(f"Audio available: {self.enabled}")
        
        if not self.enabled:
            print("Audio system not available - install winsound or run on Windows")
            return
        
        test_pitches = [
            (127, 115, 95, "Four-Seam Fastball", "R"),  # Center strike
            (28, 199, 94, "Sinker", "R"),               # Lindor HBP 
            (80, 60, 88, "Slider", "L"),                # High outside to lefty
            (200, 180, 82, "Curveball", "R"),           # Low inside to righty
        ]
        
        for x, y, velo, ptype, hand in test_pitches:
            print(f"\nPitch: {ptype} {velo}mph to {hand}HB at ({x},{y})")
            freq, duration, balance, desc = self._coordinate_to_beep_params(x, y, velo, ptype, hand)
            balance_desc = self._get_balance_description(balance)
            print(f"Audio: {freq}Hz for {duration}ms {balance_desc} - {desc}")
            
            # Generate audio
            self.generate_pitch_audio(x, y, velo, ptype, hand)
            
            # Small delay between beeps
            import time
            time.sleep(0.8)

if __name__ == "__main__":
    # Test the simple audio system
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    mapper = SimpleAudioPitchMapper()
    mapper.test_audio_mapping()
    
    # Keep app running briefly
    QTimer.singleShot(5000, app.quit)
    app.exec()
