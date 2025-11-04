# Hybrid Audio System - Option D Implementation

## Overview
**Option D (Hybrid Approach)** from the AUDIO_ENHANCEMENT_OPTIONS.md has been implemented! This provides smart, context-aware audio feedback that combines:

1. **TTS Narration** - For detailed play-by-play information
2. **Musical Tones** - With stereo positioning for spatial awareness
3. **Key Moment Announcements** - Highlights touchdowns and big plays

## Features

### Three Audio Modes

#### 1. Single Play Mode
**Purpose**: Individual play narration with full details  
**Use Case**: Alt+P on a single play  
**What You Get**:
- TTS narration of yardage and play type
- Musical tone with stereo field positioning
- Clear, detailed information

**Example**:
```python
from hybrid_audio_player import HybridAudioPlayer

player = HybridAudioPlayer()

play = {
    'description': 'QB pass complete to WR for 15 yards',
    'yardage': 15,
    'type': 'pass',
    'yardsToEndzone': 65
}

player.play_single_play(play, with_narration=True)
# Speaks: "15 yard pass. QB pass complete to WR for 15 yards"
# Plays: Musical tone with stereo position at 35% (left-center)
```

#### 2. Sequence Mode
**Purpose**: Fast drive playback with key moment highlights  
**Use Case**: Alt+S for full drive sequence  
**What You Get**:
- Quick musical tones for all plays (with stereo positioning)
- Announces drive start
- Narrates key moments AFTER the sequence:
  - Touchdowns
  - Big plays (20+ yards)
  - Turnovers

**Example**:
```python
drive = [
    {'yardage': 4, 'type': 'rush', 'yardsToEndzone': 75},
    {'yardage': 22, 'type': 'pass', 'yardsToEndzone': 71},  # Big play!
    {'yardage': 10, 'type': 'rush', 'yardsToEndzone': 10, 'isScoringPlay': True}
]

player.play_drive_sequence(drive, mode='sequence')
# Speaks: "Playing drive with 3 plays"
# Plays: Quick musical tones (beep-beep-beep with stereo panning)
# Speaks: "Play 2: Big play! 22 yards!"
# Speaks: "Play 3: Touchdown!"
```

#### 3. Tutorial Mode
**Purpose**: Educational mode with detailed explanations  
**Use Case**: Learning how the audio system works  
**What You Get**:
- Full narration of each play
- Technical details (wave type, frequency)
- Explanation of stereo positioning
- Musical tone after each explanation

**Example**:
```python
tutorial_drive = [
    {'yardage': 8, 'type': 'pass', 'yardsToEndzone': 55}
]

player.play_drive_sequence(tutorial_drive, mode='tutorial')
# Speaks: "Playing 1 plays in tutorial mode"
# Speaks: "Play 1. This is a pass. Notice the sine wave pattern at 392 hertz. 
#          The stereo positioning represents the field location."
# Plays: Sine wave tone at 45% stereo position (near center)
```

## User Preferences

The hybrid audio player supports customizable preferences:

```python
player = HybridAudioPlayer()

# Get current preferences
prefs = player.get_preferences()
# Returns: {'narration_enabled': True, 'tones_enabled': True, 'sound_effects_enabled': False}

# Disable narration (tones only)
player.set_preference('narration_enabled', False)

# Disable tones (narration only)
player.set_preference('tones_enabled', False)

# Enable both (default)
player.set_preference('narration_enabled', True)
player.set_preference('tones_enabled', True)
```

## Play Data Format

The hybrid audio player accepts a simplified play format:

```python
play = {
    'description': str,        # Human-readable description
    'yardage': int,           # Yards gained/lost (negative for losses)
    'type': str,              # 'rush' or 'pass'
    'yardsToEndzone': int,    # Current field position (0-100)
    'down': int,              # Optional: current down
    'distance': int,          # Optional: yards to first down
    'isScoringPlay': bool     # Optional: is this a touchdown?
}
```

The player automatically converts this to ESPN API format internally.

## Integration with Main Application

To integrate with the existing Scores app:

### Option 1: Replace existing audio_player
```python
from hybrid_audio_player import HybridAudioPlayer

# In your main app
self.audio_player = HybridAudioPlayer()

# For single play (Alt+P)
play_data = {
    'description': play['text'],
    'yardage': play['statYardage'],
    'type': play['type']['text'].lower(),
    'yardsToEndzone': play['start']['yardsToEndzone']
}
self.audio_player.play_single_play(play_data, with_narration=True)

# For drive sequence (Alt+S)
drive_plays = [convert_play(p) for p in drive['plays']]
self.audio_player.play_drive_sequence(drive_plays, mode='sequence')
```

### Option 2: Add as alternative mode
```python
# Add to settings/preferences
self.audio_mode = 'hybrid'  # or 'basic' for original tone-only

if self.audio_mode == 'hybrid':
    self.hybrid_player.play_single_play(play_data)
else:
    self.basic_player.play_single_play(config)
```

## Technical Details

### Dependencies
- **pyttsx3**: Text-to-speech engine (offline, uses Windows SAPI)
- **numpy**: Audio wave generation
- **winsound**: Audio playback (Windows built-in)

### Audio Quality
- **TTS**: Uses system voices (SAPI on Windows)
- **Tones**: 44.1kHz sample rate, stereo output
- **Stereo Panning**: Equal power panning for constant loudness
- **Field Position**: 0-100 yard line mapped to stereo field

### Performance
- **TTS Speed**: ~150 words per minute (configurable)
- **Sequence Mode**: Fast playback with deferred key moment narration
- **Memory**: Minimal - generates audio on-the-fly

## Key Moment Detection

The system automatically detects and announces:

1. **Touchdowns**: Any play marked as `isScoringPlay` or with "touchdown" in description
2. **Big Plays**: 20+ yards gained
3. **Turnovers**: "fumble" or "interception" in description

You can customize detection in `_announce_key_moments()` method.

## Comparison to Original System

| Feature | Original (Tones Only) | Hybrid (Option D) |
|---------|----------------------|------------------|
| Individual plays | Musical tone only | Tone + TTS narration |
| Drive sequences | Rapid tones | Tones + key moment narration |
| Information density | Low (requires interpretation) | High (direct narration) |
| Speed | Very fast | Fast (sequence), slower (single) |
| Accessibility | Moderate | Excellent |
| Learning curve | High (must learn tone meanings) | Low (direct information) |
| User control | Wave type only | Mode + preferences |

## Future Enhancements

Ready to add (from AUDIO_ENHANCEMENT_OPTIONS.md):

### Phase 2: Sound Effects
- Touchdown horn
- Crowd cheer for big plays
- Whistle sounds
- Tackle sounds

### Phase 3: Enhanced Musical System
- FM synthesis for richer tones
- Chord progressions for emotional context
- Stadium reverb effects
- Team theme songs

## Testing

Run the included test suite:

```bash
# Test basic functionality
python hybrid_audio_player.py

# Test TTS engine
python test_tts.py

# Test with real drive data
python test_hybrid_with_sample_drives.py
```

## Troubleshooting

### TTS Not Speaking
1. Check system volume
2. Verify SAPI voices installed: `Control Panel > Speech > Text to Speech`
3. Try different voice: `engine.setProperty('voice', engine.getProperty('voices')[1].id)`

### Audio Not Playing
1. Check winsound is available (Windows only)
2. Verify numpy installed: `pip install numpy`
3. Check for audio file conflicts (clean up temp files)

### Performance Issues
1. Disable narration for faster playback: `player.set_preference('narration_enabled', False)`
2. Use sequence mode instead of tutorial mode
3. Reduce TTS rate: `engine.setProperty('rate', 200)` for faster speech

## Credits

Implements **Option D: Hybrid Approach** from AUDIO_ENHANCEMENT_OPTIONS.md, combining the best of:
- TTS narration (Option A)
- Musical tones (Option C)
- Context-aware intelligent switching

---

**Status**: ✅ Fully implemented and tested  
**Version**: 1.0  
**Date**: November 2025
