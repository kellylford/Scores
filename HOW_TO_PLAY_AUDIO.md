## 🔊 How to Play Football Audio

### Quick Start

#### 1. **Test Audio Works**
Run the demo to hear a sample touchdown drive:
```bash
python audio_player.py
```
Press ENTER when prompted. You'll hear 4 plays ascending in pitch, ending with a touchdown celebration!

#### 2. **Experiment with Real Games**
```bash
python experiment_football_audio.py
```

### Playing Audio in the Experimentation Tool

When you analyze drives or big plays, you'll now see prompts like:
```
Play this drive audio? (y/n):
```

Type `y` and press ENTER to hear the audio!

### What You'll Hear

**Example: Touchdown Drive**
1. Short run (3 yards) → Low square wave (349Hz) - 0.3s
2. Pass for first down (12 yards) → Medium sine wave (523Hz) - 0.45s  
3. Deep pass (28 yards) → High sine wave (659Hz) - 0.6s
4. **TOUCHDOWN!** (7 yards) → Celebration sawtooth (880Hz) - 0.9s

The audio tells the story:
- **Pitch rises** as plays gain more yards
- **Longer notes** for big plays and touchdowns
- **Different timbres** for rushes (percussive) vs passes (smooth)
- **Dramatic finale** for scoring plays

### Audio Characteristics

**Frequencies:**
- 🎵 880Hz = Touchdowns, huge plays (bright, high)
- 🎵 659Hz = Big gains 20-39 yards
- 🎵 523Hz = First down range 10-19 yards
- 🎵 440Hz = Good gains 5-9 yards
- 🎵 349Hz = Short gains 1-4 yards
- 🎵 262Hz = No gain
- 🎵 196Hz and below = Losses (low, ominous)

**Waveforms:**
- **Square wave** (rushes) → Percussive, punchy
- **Sine wave** (passes) → Smooth, pure tone
- **Sawtooth** (scores) → Bright, celebratory
- **Triangle** (kicks) → Special teams

**Duration:**
- Regular plays: 0.3 seconds
- Big plays (20+ yards): 0.6 seconds (2x)
- Touchdowns: 0.9 seconds (3x) - celebration!

### What to Listen For

**Successful Drive:**
- Starts low (short gains)
- Gradually climbs (first downs)
- Peaks high (touchdown)
- Sounds like an ascending melody

**3-and-Out:**
- Three low notes
- Quick and sad
- No upward progression

**Big Play Touchdown:**
- Sudden high pitch spike
- Dramatic jump from low to high
- Exciting audio contrast

**Struggling Drive:**
- Clustered low frequencies
- Dissonant, choppy
- No clear progression

### Menu Options with Audio

**Option 1: View Drives**
- Pick any drive
- See the audio breakdown
- **Play it!** Hear the whole drive sequence

**Option 2: Big Plays**
- See all 20+ yard plays
- **Play them all!** Hear the highlight reel

**Option 4: Experiment**
- Adjust base_duration (faster/slower)
- Adjust base_volume (quieter/louder)
- Hear the same drive with different settings

### Tips for Best Audio Experience

1. **Start with a scoring drive** - Most dramatic arc
2. **Compare TD drive vs 3-and-out** - Stark contrast
3. **Play the highlight reel** - All the excitement
4. **Try different durations**:
   - 0.2s = Fast recap
   - 0.5s = Slower, appreciate each play
   
### Troubleshooting

**No sound?**
- Check Windows volume settings
- Make sure audio isn't muted
- Test with `python audio_player.py` demo first

**Audio sounds weird?**
- Normal! These are synthetic tones, not music
- Higher pitch = better play
- Longer note = more important play

**Want to stop playback?**
- Wait for sequence to finish (usually 5-15 seconds)
- Or press Ctrl+C to exit program

### Next Steps

Once you've experimented:
- Try different games (Option 5)
- Find the longest scoring drive
- Compare offensive vs defensive games
- See how blowouts vs close games sound different

The audio makes patterns instantly recognizable that would take minutes to analyze in stats!
