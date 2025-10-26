## 🏈 Football Audio Experimentation - Quick Start Guide

### How to Run

Simply run:
```bash
python experiment_football_audio.py
```

### What You Can Do

#### 1. **Pick a Game**
   - Shows recent completed NFL games
   - Choose one to explore

#### 2. **Analyze Individual Drives**
   - View all 19 drives from the game
   - Pick any drive to see:
     - Play-by-play audio mapping
     - Frequency (Hz) for each play
     - Wave type (sine/square/sawtooth/triangle)
     - Duration
     - Visual frequency bars
   
   Example output:
   ```
   1. +16yd | 523.2Hz sine     | 0.45s
      ==========
      C.Wentz pass deep left to J.Jefferson for 16 yards
   
   2. +2yd  | 349.2Hz square   | 0.30s
      =======
      J.Mason left tackle for 2 yards
   ```

#### 3. **View Big Plays (Highlight Reel)**
   - Shows all plays 20+ yards
   - Includes touchdowns, big gains, turnovers
   - Customize minimum yardage threshold
   
   Example:
   ```
   1. [TD] +8yd  | 440Hz sawtooth  - Herbert TD pass!
   2.     +40yd | 880Hz sine      - Deep pass to Gadsden
   3.     -8yd  | 116Hz square    - Sack!
   ```

#### 4. **Compare Two Drives**
   - Pick any two drives
   - See side-by-side comparison:
     - Total plays, yards, result
     - Frequency range (min/max/average)
     - Audio duration
     - Scoring vs non-scoring
   
   Useful for comparing:
   - Touchdown drive vs punt
   - Efficient vs struggling offense
   - Long sustained drive vs quick score

#### 5. **Experiment with Audio Parameters**
   - Adjust base duration (faster/slower playback)
   - Adjust base volume
   - See how changes affect the audio mapping
   - Test different settings on same drive
   
   Try:
   - Duration: 0.2s (fast), 0.5s (slow), 0.8s (very slow)
   - Volume: 0.4 (quiet), 0.8 (loud)

### Understanding the Audio

**Frequencies (Pitch):**
- 880Hz: Touchdowns, huge plays (40+ yards)
- 659Hz: Big gains (20-39 yards)
- 523Hz: First down range (10-19 yards)
- 440Hz: Good gains (5-9 yards)
- 349Hz: Short gains (1-4 yards)
- 262Hz: No gain
- 196Hz and below: Losses, sacks

**Wave Types (Timbre):**
- **Sine (~)**: Passes - smooth, pure tone
- **Square (^)**: Rushes - percussive, aggressive
- **Triangle (v)**: Kicks - special teams
- **Sawtooth (/)**: Scores - bright, celebratory

**Duration:**
- Scoring plays: 3x longer (0.9s) - celebration!
- Big plays (20+): 2x longer (0.6s)
- Regular plays: 0.3s (base)

**Volume:**
- Max (1.0) for scores
- Boosted for 3rd/4th down (critical)
- Boosted in red zone (inside 20 yards)

### Example Session

```
1. Choose game: Vikings @ Chargers
2. Pick option 1 (View drives)
3. Select drive #2 (Chargers touchdown drive)
4. See the musical arc:
   - Starts low (short gains)
   - Builds with first downs (higher notes)
   - Climaxes with TD (880Hz celebration)
5. Try option 3 (Compare drives)
6. Compare drive #2 (TD) vs drive #1 (punt)
   - See how successful drive has higher avg frequency
   - TD drive has wider frequency range
```

### Tips for Experimentation

**Find Interesting Audio Patterns:**
- Long scoring drives = rich melodic progression
- 3-and-out = three low notes, quick and sad
- Big play TD = sudden high pitch spike
- Back-and-forth drive = wide frequency swings

**Compare Audio Characteristics:**
- Efficient offense = higher average frequencies
- Struggling offense = clustered low frequencies
- Explosive offense = large frequency spikes
- Ball control = many medium-frequency notes

**Adjust Parameters:**
- Faster playback (0.2s) = get through drives quickly
- Slower playback (0.5s+) = appreciate each play
- Higher base volume = emphasize all plays equally
- Lower base volume = let big plays stand out more

### What to Listen For

When you eventually add real audio synthesis:
- **Touchdown drives** will sound like ascending melodies
- **3-and-outs** will sound flat and disappointing
- **Big plays** will create dramatic pitch jumps
- **Efficient drives** will have smooth progressions
- **Struggling drives** will sound dissonant and choppy

### Next Steps

The system generates all the audio parameters. To actually *hear* sounds:
1. Integrate with audio synthesis library (like `pydub` or `winsound`)
2. Add UI controls for play/pause
3. Create real-time mode for live games
4. Export drives as audio files

But for now, you can see exactly what frequencies, wave types, and durations each play would generate - perfect for experimentation!
