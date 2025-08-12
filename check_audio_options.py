#!/usr/bin/env python3
"""
Check Available Audio Libraries
===============================
"""

def check_audio_libraries():
    """Check what audio libraries are available"""
    libraries = [
        'pygame',
        'pydub', 
        'sounddevice',
        'pyaudio',
        'playsound',
        'wave',
        'ossaudiodev'
    ]
    
    print("Audio Library Availability Check:")
    print("=" * 40)
    
    available = []
    for lib in libraries:
        try:
            __import__(lib)
            print(f"✓ {lib}: Available")
            available.append(lib)
        except ImportError:
            print(f"✗ {lib}: Not installed")
    
    return available

def suggest_stereo_alternatives():
    """Suggest alternatives for stereo audio"""
    print("\n" + "=" * 40)
    print("Stereo Audio Alternatives:")
    print("=" * 40)
    
    print("1. **pygame**: Can generate stereo tones with left/right channel control")
    print("2. **wave + struct**: Generate WAV files with stereo data") 
    print("3. **Different frequencies**: Use very different frequencies for left/right")
    print("4. **Temporal patterns**: Use distinct timing patterns")
    print("5. **Volume modulation**: Use Windows volume control APIs")
    
    print("\nCurrent winsound limitations:")
    print("- Mono audio only")
    print("- No stereo balance")
    print("- No volume control")
    print("- Simple beep tones only")

if __name__ == "__main__":
    available = check_audio_libraries()
    suggest_stereo_alternatives()
    
    if 'pygame' in available:
        print("\n🎵 pygame is available - we could implement true stereo audio!")
    elif 'wave' in available:
        print("\n🎵 wave module is available - we could generate stereo WAV files!")
    else:
        print("\n🔇 Limited to winsound beeps - let's try more dramatic frequency differences")
