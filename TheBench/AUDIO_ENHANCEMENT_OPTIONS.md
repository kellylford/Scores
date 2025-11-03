# Audio Enhancement Options for Scores App

## Current State
The app currently uses simple tone synthesis for audio feedback:
- **Baseball**: Strike zone mapping with pitch-based frequencies (high/low/middle zones)
- **Football**: Drive progression with stereo positioning and yardage-based pitch
- **Wave types**: Square (rush), Sine (pass), Sawtooth (scoring)
- **Limitations**: Functional but not engaging; sounds like computer beeps rather than sports

## Enhancement Options

### Option A: Speech Synthesis (Text-to-Speech) 🗣️

#### Implementation
```python
# Using pyttsx3 (offline, cross-platform, no dependencies)
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed
engine.setProperty('volume', 0.9)

# Football examples
engine.say("3rd and 7 from the 30 yard line")
engine.say("12 yard completion")
engine.say("Touchdown Wisconsin!")

# Baseball examples
engine.say("Strike on the outside corner")
engine.say("Ball high and inside")
engine.say("Home run to left field!")
engine.runAndWait()
```

#### Pros
- **Most informative**: Users hear exactly what happened
- **Accessibility gold**: Perfect for screen reader users
- **No learning curve**: Immediate understanding
- **Works offline**: pyttsx3 uses system TTS
- **Highly customizable**: Speed, pitch, voice selection

#### Cons
- **Slower**: Takes time to speak full sentences
- **Could be verbose**: Might be annoying for rapid play sequences
- **Voice quality**: System TTS can sound robotic

#### Best For
- Individual play narration (Alt+P)
- Key moments (touchdowns, home runs, strikeouts)
- Tutorial mode explanations
- Users who prefer detailed verbal feedback

---

### Option B: Sound Effects Library 🔊

#### Implementation
```python
# Pre-recorded stadium sounds
import pygame

sounds = {
    # Football
    'whistle': 'sounds/referee_whistle.wav',
    'crowd_cheer_loud': 'sounds/crowd_big_cheer.wav',
    'crowd_cheer_medium': 'sounds/crowd_cheer.wav',
    'crowd_groan': 'sounds/crowd_aww.wav',
    'tackle': 'sounds/football_hit.wav',
    'touchdown_horn': 'sounds/touchdown_horn.wav',
    'field_goal': 'sounds/field_goal_good.wav',
    
    # Baseball
    'bat_crack': 'sounds/bat_hit.wav',
    'crowd_ooh': 'sounds/crowd_reaction.wav',
    'umpire_strike': 'sounds/strike_call.wav',
    'organ_charge': 'sounds/charge.wav',
    'home_run_call': 'sounds/home_run.wav'
}

# Layer multiple sounds
def play_touchdown():
    sounds['touchdown_horn'].play()
    pygame.time.delay(500)
    sounds['crowd_cheer_loud'].play()
```

#### Pros
- **Realistic**: Actual stadium atmosphere
- **Emotionally engaging**: Crowd reactions add excitement
- **Quick**: Instant audio feedback
- **Recognizable**: Everyone knows what a whistle/horn means
- **Layerable**: Can combine sounds for richer experience

#### Cons
- **File management**: Need to bundle/download sound files
- **Copyright**: Must use royalty-free sounds
- **Storage**: Adds to app size
- **Limited information**: Doesn't convey specific details

#### Best For
- Background atmosphere during drive sequences
- Punctuation for key moments
- Emotional engagement
- Quick feedback without narration

---

### Option C: Musical/Harmonic System 🎵

#### Implementation
```python
# FM synthesis for richer tones
from scipy import signal
import numpy as np

def create_musical_tone(play_type, yardage, field_position):
    """Generate musical tones instead of beeps"""
    
    # Chord progressions based on outcome
    if yardage >= 20:  # Big play
        # Major 7th chord (excitement)
        notes = [261.63, 329.63, 392.00, 493.88]  # C-E-G-B
    elif yardage >= 10:  # Good gain
        # Major triad (positive)
        notes = [261.63, 329.63, 392.00]  # C-E-G
    elif yardage >= 0:  # Small gain
        # Single note (neutral)
        notes = [261.63]
    else:  # Loss
        # Minor chord (negative)
        notes = [261.63, 311.13, 392.00]  # C-Eb-G
    
    # Add reverb for stadium feel
    # Stereo panning for field position
    # Tempo based on play speed
```

#### Advanced: MIDI Generation
```python
from mido import MidiFile, MidiTrack, Message

# Create theme songs for teams
# Victory melodies for touchdowns
# Ascending scales for drives
# Descending patterns for turnovers
```

#### Pros
- **Pleasant**: Musical instead of harsh beeps
- **Expressive**: Chords convey emotion/outcome
- **Spatial**: Still supports stereo positioning
- **Creative**: Could have team themes, victory jingles
- **No files needed**: Generated in real-time

#### Cons
- **Abstract**: Still requires learning what sounds mean
- **Less informative**: Doesn't tell you specific yardage
- **Complexity**: Harder to tune/balance
- **Subjective**: Musical taste varies

#### Best For
- Background score during drive playback
- Emotional tone without narration
- Users who like musical feedback
- "Video game" style experience

---

### Option D: Hybrid Approach (Recommended) ⭐

#### Smart Context-Aware Audio
```python
def play_audio_for_context(play_data, mode='sequence'):
    """Combine multiple audio types intelligently"""
    
    if mode == 'single':
        # Alt+P on individual play: Use TTS for details
        speak(f"{play_data['yardage']} yard {play_data['type']}")
        
    elif mode == 'sequence':
        # Alt+S for full drive: Use musical tones + sound effects
        for play in drive:
            # Quick musical tone with stereo positioning
            play_musical_tone(play)
            
            # Sound effects for key moments
            if play.is_touchdown:
                play_sound('touchdown_horn')
                speak("Touchdown!")
            elif play.is_big_play:
                play_sound('crowd_cheer')
    
    elif mode == 'tutorial':
        # Learning mode: Detailed narration
        speak(f"This is a {play_type}. Notice the {wave_type} wave pattern...")
```

#### Implementation Strategy
1. **Individual plays (Alt+P)**: TTS narration with details
2. **Drive sequences (Alt+S)**: Musical tones with spatial positioning + sound effects at key moments
3. **Tutorial mode**: Full TTS explanations
4. **Settings**: Let users choose preferred audio mode

#### Pros
- **Best of all worlds**: Informative when needed, quick when desired
- **Context-appropriate**: Different feedback for different uses
- **Flexible**: Users can customize preference
- **Scalable**: Easy to add more audio types

#### Cons
- **More complex**: Multiple audio systems to maintain
- **Larger**: Combines storage needs

---

## Specific Recommendations for Your App

### Phase 1: Quick Win - Add TTS (Easy)
```python
# Add pyttsx3 to requirements.txt
pip install pyttsx3

# Minimal code change - just wrap existing audio calls
def play_with_narration(text, also_play_tone=True):
    if user_preferences.get('narration_enabled', True):
        speak(text)
    if also_play_tone and user_preferences.get('tones_enabled', True):
        # Keep existing tone generation
        play_current_tone()
```

**Effort**: 1-2 hours  
**Impact**: Huge for accessibility  
**Risk**: Low (pyttsx3 is stable)

### Phase 2: Sound Effects for Key Moments (Medium)
```python
# Bundle a few key sounds
sounds = {
    'touchdown': 'touchdown.wav',  # ~50KB
    'field_goal': 'field_goal.wav', # ~30KB  
    'home_run': 'home_run.wav',    # ~40KB
}

# Play at climactic moments only
if scoring_play:
    play_sound(play_type)
    speak(f"Touchdown {team_name}!")
```

**Effort**: 3-4 hours (finding sounds, integration)  
**Impact**: Medium (adds excitement)  
**Risk**: Low (optional feature)

### Phase 3: Enhanced Musical System (Advanced)
- FM synthesis instead of basic waves
- Chord progressions for emotional context
- Stadium reverb effects
- Tempo variation based on game pace

**Effort**: 8-10 hours  
**Impact**: Medium (subjective improvement)  
**Risk**: Medium (complexity)

---

## Dependencies & Resources

### Text-to-Speech
```bash
# Offline, cross-platform (RECOMMENDED)
pip install pyttsx3

# Online, higher quality voices (optional)
pip install gTTS
pip install playsound
```

### Sound Effects
- **Source**: freesound.org (Creative Commons)
- **Library**: soundbible.com (royalty-free)
- **Size**: Keep under 5MB total for basic set

### Music/MIDI
```bash
pip install mido
pip install python-rtmidi  # For playback
```

### Advanced Synthesis
```bash
pip install scipy  # Already have
pip install pedalboard  # Spotify's audio effects (optional)
```

---

## User Settings (Future)

```python
AUDIO_PREFERENCES = {
    'mode': 'hybrid',  # 'tones', 'speech', 'hybrid'
    'narration_enabled': True,
    'sound_effects_enabled': True,
    'musical_tones_enabled': True,
    'speech_rate': 150,  # words per minute
    'effect_volume': 0.8,
    'narrate_all_plays': False,  # Only key moments
    'spatial_audio': True  # Stereo positioning
}
```

---

## Implementation Priority

### Must Have (Phase 1)
- ✅ Keep existing tone system (works for spatial positioning)
- 🆕 Add pyttsx3 TTS for individual plays (Alt+P)
- 🆕 Settings to toggle narration on/off

### Should Have (Phase 2)
- 🆕 Sound effects for touchdowns, home runs, key moments
- 🆕 Crowd noise that scales with importance
- 🆕 Tutorial narration improvements

### Nice to Have (Phase 3)
- Enhanced musical tones (FM synthesis, chords)
- Stadium reverb effects
- Team-specific audio themes
- MIDI victory melodies

---

## Code Examples

### Example 1: Enhanced Football Audio with TTS
```python
def _play_single_play_audio_enhanced(self, play):
    """Play audio for a single play with narration option"""
    
    yardage = play.get('statYardage', 0)
    play_type = play.get('type', {}).get('text', '')
    play_text = play.get('text', '')
    
    # Option 1: Narrate the play
    if self.settings.get('narration_enabled'):
        narration = f"{abs(yardage)} yard {play_type}"
        if yardage < 0:
            narration = f"Loss of {narration}"
        self.tts_engine.say(narration)
        self.tts_engine.runAndWait()
    
    # Option 2: Play musical tone (existing system)
    if self.settings.get('tones_enabled'):
        audio_sequence = self.football_audio_mapper.map_drive_to_audio_sequence(
            {"plays": [play]}
        )
        self.football_audio_player.play_audio_sequence(audio_sequence)
    
    # Option 3: Sound effect for scoring plays
    if play.get('scoringPlay') and self.settings.get('effects_enabled'):
        self.play_sound_effect('touchdown')
```

### Example 2: Enhanced Baseball Audio
```python
def _play_pitch_audio_enhanced(self, pitch_data):
    """Play pitch with multiple audio options"""
    
    location = pitch_data.get('zone', 'Unknown')
    pitch_type = pitch_data.get('type', 'Unknown')
    result = pitch_data.get('result', 'Unknown')
    
    # Quick tone for spatial awareness (existing)
    if self.settings.get('tones_enabled'):
        self._play_pitch_tone(pitch_data)
    
    # TTS for detail (new)
    if self.settings.get('narration_enabled'):
        narration = f"{result}. {pitch_type} in zone {location}"
        self.tts_engine.say(narration)
        self.tts_engine.runAndWait()
    
    # Sound effect for strikes/balls (new)
    if self.settings.get('effects_enabled'):
        if result == 'Strike':
            self.play_sound_effect('umpire_strike')
        elif result == 'Ball':
            self.play_sound_effect('crowd_ooh')
```

---

## Testing Plan

1. **TTS Testing**
   - Test all speech synthesis with screen readers
   - Verify rate/volume settings
   - Check performance (doesn't block UI)

2. **Sound Effect Testing**
   - Verify all files load correctly
   - Test volume mixing
   - Check file sizes

3. **User Testing**
   - Get feedback on narration vs tones
   - Test with actual users who are blind/low vision
   - A/B test different audio modes

---

## Conclusion

**Recommended Approach**: Start with **Phase 1 (TTS for individual plays)** because:
1. Easy to implement (pyttsx3 is simple)
2. Huge accessibility win
3. Low risk (optional feature)
4. Can be toggled in settings
5. Doesn't remove existing functionality

**Next Steps**:
1. Add pyttsx3 dependency
2. Create TTS wrapper class
3. Add to individual play audio (Alt+P)
4. Add settings toggle
5. Test with users
6. Then consider sound effects for Phase 2

The current tone system is actually good for spatial awareness and quick feedback during sequences. Adding TTS for detailed feedback on individual plays gives users the best of both worlds.
