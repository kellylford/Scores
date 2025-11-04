"""
Advanced Audio Synthesis Module
Adds FM synthesis, noise generation, and other advanced techniques
to the basic waveform generator.
"""

import numpy as np
from typing import Optional


class AdvancedSynthesis:
    """Advanced synthesis techniques beyond basic waveforms."""
    
    SAMPLE_RATE = 44100
    
    @staticmethod
    def generate_fm_synthesis(carrier_freq: float, modulator_freq: float, 
                            modulation_index: float, duration: float,
                            sample_rate: int = 44100) -> np.ndarray:
        """
        Generate FM (Frequency Modulation) synthesis.
        
        Args:
            carrier_freq: Main frequency (Hz)
            modulator_freq: Modulating frequency (Hz) - often a ratio of carrier
            modulation_index: Depth of modulation (0-10+ typical)
            duration: Length in seconds
            sample_rate: Audio sample rate
            
        Returns:
            Audio samples
            
        Example ratios for different sounds:
        - Bell: carrier=1, modulator=1.4, index=5
        - Electric Piano: carrier=1, modulator=14, index=3
        - Brass: carrier=1, modulator=1, index=5
        - Organ: carrier=1, modulator=0.5, index=2
        """
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        
        # Modulator affects carrier frequency
        modulator = np.sin(2 * np.pi * modulator_freq * t)
        carrier = np.sin(2 * np.pi * carrier_freq * t + modulation_index * modulator)
        
        return carrier
    
    @staticmethod
    def generate_white_noise(duration: float, sample_rate: int = 44100) -> np.ndarray:
        """
        Generate white noise (all frequencies equal).
        Good for: hi-hats, cymbals, breath sounds, static
        """
        num_samples = int(sample_rate * duration)
        return np.random.uniform(-1.0, 1.0, num_samples)
    
    @staticmethod
    def generate_pink_noise(duration: float, sample_rate: int = 44100) -> np.ndarray:
        """
        Generate pink noise (1/f noise - more low-end than white).
        Good for: ocean, wind, rain, natural ambiences
        """
        num_samples = int(sample_rate * duration)
        
        # Simple pink noise using rolling average
        white = np.random.uniform(-1.0, 1.0, num_samples)
        
        # Apply 1/f filter by averaging
        pink = np.zeros(num_samples)
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        
        for i in range(3, num_samples):
            pink[i] = (b[0] * white[i] + b[1] * white[i-1] + 
                      b[2] * white[i-2] + b[3] * white[i-3] -
                      a[1] * pink[i-1] - a[2] * pink[i-2] - a[3] * pink[i-3])
        
        # Normalize
        max_val = np.max(np.abs(pink))
        if max_val > 0:
            pink = pink / max_val
        
        return pink
    
    @staticmethod
    def generate_brown_noise(duration: float, sample_rate: int = 44100) -> np.ndarray:
        """
        Generate brown noise (even more low-end, rumble).
        Good for: thunder, rumble, explosions, deep ambience
        """
        num_samples = int(sample_rate * duration)
        
        # Brown noise is the integration of white noise
        white = np.random.uniform(-1.0, 1.0, num_samples)
        brown = np.cumsum(white)
        
        # Normalize
        max_val = np.max(np.abs(brown))
        if max_val > 0:
            brown = brown / max_val
        
        return brown
    
    @staticmethod
    def apply_bandpass_filter(audio: np.ndarray, low_freq: float, high_freq: float,
                             sample_rate: int = 44100) -> np.ndarray:
        """
        Simple bandpass filter using FFT.
        Keeps frequencies between low_freq and high_freq.
        
        Args:
            audio: Input audio samples
            low_freq: Low cutoff frequency (Hz)
            high_freq: High cutoff frequency (Hz)
            sample_rate: Audio sample rate
            
        Returns:
            Filtered audio
        """
        # FFT
        fft = np.fft.rfft(audio)
        frequencies = np.fft.rfftfreq(len(audio), 1.0/sample_rate)
        
        # Create mask: keep only frequencies in band
        mask = (frequencies >= low_freq) & (frequencies <= high_freq)
        fft[~mask] = 0
        
        # Inverse FFT
        filtered = np.fft.irfft(fft, len(audio))
        
        return filtered
    
    @staticmethod
    def apply_highpass_filter(audio: np.ndarray, cutoff_freq: float,
                             sample_rate: int = 44100) -> np.ndarray:
        """Remove frequencies below cutoff."""
        fft = np.fft.rfft(audio)
        frequencies = np.fft.rfftfreq(len(audio), 1.0/sample_rate)
        
        mask = frequencies >= cutoff_freq
        fft[~mask] = 0
        
        filtered = np.fft.irfft(fft, len(audio))
        return filtered
    
    @staticmethod
    def apply_lowpass_filter(audio: np.ndarray, cutoff_freq: float,
                            sample_rate: int = 44100) -> np.ndarray:
        """Remove frequencies above cutoff."""
        fft = np.fft.rfft(audio)
        frequencies = np.fft.rfftfreq(len(audio), 1.0/sample_rate)
        
        mask = frequencies <= cutoff_freq
        fft[~mask] = 0
        
        filtered = np.fft.irfft(fft, len(audio))
        return filtered
    
    @staticmethod
    def ring_modulation(carrier: np.ndarray, modulator: np.ndarray) -> np.ndarray:
        """
        Ring modulation - multiply two signals together.
        Creates metallic, robotic, dissonant sounds.
        
        Args:
            carrier: First audio signal
            modulator: Second audio signal (should be same length)
            
        Returns:
            Ring modulated audio
        """
        # Make sure same length
        min_len = min(len(carrier), len(modulator))
        result = carrier[:min_len] * modulator[:min_len]
        return result
    
    @staticmethod
    def apply_lfo(audio: np.ndarray, lfo_freq: float, depth: float,
                 lfo_type: str = 'sine', sample_rate: int = 44100) -> np.ndarray:
        """
        Apply Low Frequency Oscillator for vibrato/tremolo effects.
        
        Args:
            audio: Input audio
            lfo_freq: LFO frequency (0.5-10 Hz typical)
            depth: Modulation depth (0.0-1.0)
            lfo_type: 'sine', 'triangle', 'square'
            sample_rate: Audio sample rate
            
        Returns:
            Modulated audio (tremolo effect)
        """
        num_samples = len(audio)
        t = np.linspace(0, num_samples / sample_rate, num_samples, False)
        
        # Generate LFO
        if lfo_type == 'sine':
            lfo = np.sin(2 * np.pi * lfo_freq * t)
        elif lfo_type == 'triangle':
            lfo = 2 * np.abs(2 * (t * lfo_freq - np.floor(t * lfo_freq + 0.5))) - 1
        elif lfo_type == 'square':
            lfo = np.sign(np.sin(2 * np.pi * lfo_freq * t))
        else:
            lfo = np.sin(2 * np.pi * lfo_freq * t)
        
        # Apply tremolo (amplitude modulation)
        # Scale LFO from [-1, 1] to [1-depth, 1+depth]
        lfo_scaled = 1 + (lfo * depth)
        
        return audio * lfo_scaled
    
    @staticmethod
    def apply_simple_echo(audio: np.ndarray, delay_time: float, feedback: float,
                         sample_rate: int = 44100) -> np.ndarray:
        """
        Simple echo/delay effect.
        
        Args:
            audio: Input audio
            delay_time: Delay time in seconds
            feedback: Feedback amount (0.0-0.9, higher = more repeats)
            sample_rate: Audio sample rate
            
        Returns:
            Audio with echo
        """
        delay_samples = int(delay_time * sample_rate)
        output = np.copy(audio)
        
        # Add delayed signal with feedback
        for i in range(delay_samples, len(audio)):
            output[i] += output[i - delay_samples] * feedback
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(output))
        if max_val > 1.0:
            output = output / max_val
        
        return output
    
    @staticmethod
    def pwm_oscillator(frequency: float, duration: float, duty_cycle: float,
                      sample_rate: int = 44100) -> np.ndarray:
        """
        Pulse Width Modulation oscillator.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            duty_cycle: Pulse width (0.0-1.0), 0.5 = square wave
            sample_rate: Audio sample rate
            
        Returns:
            PWM waveform
        """
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        
        # Generate phase
        phase = (t * frequency) % 1.0
        
        # Compare phase to duty cycle
        pwm = np.where(phase < duty_cycle, 1.0, -1.0)
        
        return pwm
    
    @staticmethod
    def karplus_strong(frequency: float, duration: float, 
                      sample_rate: int = 44100) -> np.ndarray:
        """
        Karplus-Strong string synthesis (plucked string physical model).
        
        Args:
            frequency: Fundamental frequency
            duration: Duration in seconds
            sample_rate: Audio sample rate
            
        Returns:
            Plucked string sound
        """
        num_samples = int(sample_rate * duration)
        
        # Delay line length based on frequency
        delay_length = int(sample_rate / frequency)
        
        # Initialize delay line with noise burst (pluck)
        delay_line = np.random.uniform(-1.0, 1.0, delay_length)
        
        # Generate output by feeding delay line through itself
        output = np.zeros(num_samples)
        
        for i in range(num_samples):
            # Output current sample
            output[i] = delay_line[0]
            
            # Average current and next sample (low-pass filter)
            average = (delay_line[0] + delay_line[1]) * 0.5 * 0.996  # 0.996 = damping
            
            # Rotate delay line and feed back averaged sample
            delay_line = np.roll(delay_line, -1)
            delay_line[-1] = average
        
        return output
