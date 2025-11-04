"""
Enhanced audio synthesis with professional sound design.
Adds harmonic layering, proper ADSR envelopes, and waveform blending
for richer, more musical tones that sound less "toy-like".
"""

import numpy as np
from typing import Optional
from audio_player import AudioPlayer
from football_audio_mapper import PlayAudioConfig


class EnhancedAudioPlayer(AudioPlayer):
    """
    Enhanced audio player with professional sound synthesis.
    
    Features:
    - Harmonic layering (fundamental + octave + fifth)
    - Proper ADSR envelopes (Attack, Decay, Sustain, Release)
    - Waveform blending for warmer tones
    - Sub-bass layer for impact plays
    - Filtered noise for texture
    """
    
    def __init__(self):
        super().__init__()
        self.harmonic_layering = True
        self.use_sub_bass = True
        self.blend_waveforms = True
    
    def generate_tone(self, config: PlayAudioConfig, field_position: Optional[int] = None,
                     end_field_position: Optional[int] = None) -> np.ndarray:
        """
        Generate enhanced audio with harmonics and better envelopes.
        
        Overrides parent to add:
        - Harmonic layering
        - Waveform blending
        - Sub-bass for scoring plays
        - Better ADSR envelope
        """
        num_samples = int(self.SAMPLE_RATE * config.duration)
        t = np.linspace(0, config.duration, num_samples, False)
        
        # Generate enhanced multi-layer waveform
        wave_data = self._generate_layered_waveform(t, config)
        
        # Apply proper ADSR envelope
        wave_data = self._apply_adsr_envelope(wave_data, config)
        
        # Apply stereo panning if field position provided
        if field_position is not None and self.stereo_enabled:
            if end_field_position is not None and end_field_position != field_position:
                # Animate from start to end position
                left_channel, right_channel = self._apply_animated_stereo_pan(
                    wave_data, field_position, end_field_position
                )
            else:
                # Static position
                left_channel, right_channel = self._apply_stereo_pan(wave_data, field_position)
            stereo_data = np.column_stack([left_channel, right_channel])
            return stereo_data
        
        return wave_data
    
    def _generate_layered_waveform(self, t: np.ndarray, config: PlayAudioConfig) -> np.ndarray:
        """
        Generate rich multi-layer waveform with harmonics.
        
        Layers:
        - Fundamental frequency (100% requested frequency)
        - Octave up (2x frequency, 30% volume) - adds brightness
        - Perfect fifth (1.5x frequency, 20% volume) - adds musicality
        - Sub-bass (0.5x frequency, 40% volume) - for scoring plays only
        """
        # Generate fundamental (primary tone)
        fundamental = self._generate_base_wave(t, config.frequency, config.wave_type, config.volume)
        
        if not self.harmonic_layering:
            return fundamental
        
        # Add harmonics for richness
        layers = [fundamental]
        
        # Octave up (adds brightness and presence)
        octave_up = self._generate_base_wave(
            t, config.frequency * 2.0, config.wave_type, config.volume * 0.3
        )
        layers.append(octave_up)
        
        # Perfect fifth (adds musicality and warmth)
        fifth = self._generate_base_wave(
            t, config.frequency * 1.5, config.wave_type, config.volume * 0.2
        )
        layers.append(fifth)
        
        # Sub-bass for scoring plays (adds weight and impact)
        if self.use_sub_bass and hasattr(config, 'play_type'):
            if config.play_type in ['touchdown', 'field_goal']:
                sub_bass = self._generate_base_wave(
                    t, config.frequency * 0.5, 'sine', config.volume * 0.4
                )
                layers.append(sub_bass)
        
        # Mix all layers
        mixed = np.sum(layers, axis=0)
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(mixed))
        if max_val > 1.0:
            mixed = mixed / max_val
        
        return mixed
    
    def _generate_base_wave(self, t: np.ndarray, frequency: float, 
                           wave_type: str, volume: float) -> np.ndarray:
        """
        Generate a single waveform with optional blending.
        
        For warmer tones, blends waveforms:
        - Square + Triangle blend for rush plays
        - Sine stays pure for pass plays
        - Sawtooth + Sine blend for scoring plays
        """
        if wave_type == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        
        elif wave_type == 'square':
            square = np.sign(np.sin(2 * np.pi * frequency * t))
            if self.blend_waveforms:
                # Blend square with triangle for warmth (50/50 mix)
                triangle = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
                wave = 0.5 * square + 0.5 * triangle
            else:
                wave = square
        
        elif wave_type == 'sawtooth':
            sawtooth = 2 * (t * frequency - np.floor(t * frequency + 0.5))
            if self.blend_waveforms:
                # Blend sawtooth with sine for smoothness (70/30 mix)
                sine = np.sin(2 * np.pi * frequency * t)
                wave = 0.7 * sawtooth + 0.3 * sine
            else:
                wave = sawtooth
        
        elif wave_type == 'triangle':
            wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        
        else:
            # Default to sine
            wave = np.sin(2 * np.pi * frequency * t)
        
        return wave * volume
    
    def _apply_adsr_envelope(self, wave_data: np.ndarray, config: PlayAudioConfig) -> np.ndarray:
        """
        Apply proper ADSR (Attack, Decay, Sustain, Release) envelope.
        
        ADSR creates more dynamic, instrument-like sounds:
        - Attack: Time to reach peak (fast = percussive, slow = smooth)
        - Decay: Time to fall to sustain level
        - Sustain: Level maintained during play (as percentage of peak)
        - Release: Fade out time at end
        
        Config uses:
        - config.attack: Attack time (s)
        - config.decay: Used as decay time (s)
        - Sustain: Fixed at 70% for musical sound
        - Release: 150ms for smooth fade
        """
        num_samples = len(wave_data)
        envelope = np.ones(num_samples)
        
        # Attack phase (0 → 1.0)
        attack_samples = int(self.SAMPLE_RATE * config.attack)
        attack_samples = min(attack_samples, num_samples // 4)  # Max 25% of duration
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay phase (1.0 → sustain_level)
        sustain_level = 0.7  # 70% of peak - sounds musical and natural
        decay_samples = int(self.SAMPLE_RATE * config.decay)
        decay_samples = min(decay_samples, num_samples // 4)  # Max 25% of duration
        decay_start = attack_samples
        decay_end = decay_start + decay_samples
        
        if decay_samples > 0 and decay_end < num_samples:
            envelope[decay_start:decay_end] = np.linspace(1.0, sustain_level, decay_samples)
        
        # Sustain phase (maintain sustain_level)
        # Release phase will override the end portion
        release_time = 0.15  # 150ms release for smooth fade
        release_samples = int(self.SAMPLE_RATE * release_time)
        release_samples = min(release_samples, num_samples // 3)  # Max 33% of duration
        
        if decay_end < num_samples - release_samples:
            envelope[decay_end:num_samples - release_samples] = sustain_level
        
        # Release phase (sustain_level → 0)
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)
        
        return wave_data * envelope
    
    def set_harmonic_layering(self, enabled: bool):
        """Enable/disable harmonic layering."""
        self.harmonic_layering = enabled
    
    def set_sub_bass(self, enabled: bool):
        """Enable/disable sub-bass layer for scoring plays."""
        self.use_sub_bass = enabled
    
    def set_waveform_blending(self, enabled: bool):
        """Enable/disable waveform blending for warmer tones."""
        self.blend_waveforms = enabled
