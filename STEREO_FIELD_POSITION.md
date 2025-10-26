## 🎧 Stereo Field Position - Audio Innovation!

### The Feature

**You can now HEAR where the team is on the field!**

When you play drive audio, the sound moves through your headphones:
- **Left speaker** = Their own endzone (0 yard line)
- **Center** = Midfield (50 yard line)  
- **Right speaker** = Opponent's endzone (100 yard line)

As the offense moves down the field, the sound literally travels from left to right!

### Why This Is Cool

**Traditional View:** Look at numbers, read yard lines, track progress mentally

**Stereo Audio View:** HEAR the team advance - your ears tell the story!

### What You'll Experience

#### Touchdown Drive
```
Play 1: Yard 25 → Sound comes from left (their territory)
Play 2: Yard 35 → Sound moves toward center
Play 3: Yard 50 → Sound is centered (midfield!)
Play 4: Yard 75 → Sound in right speaker (red zone!)
Play 5: TD!    → High pitch, far right (celebration!)
```

You literally hear them march down the field. It's like watching a stereo soundstage!

#### 3-and-Out
```
Play 1: Yard 20 → Left speaker
Play 2: Yard 22 → Still left (barely moved)
Play 3: Yard 18 → Even more left (went backwards!)
```

The sound stays stuck in the left channel - you hear the struggle!

#### Big Play Touchdown
```
Play 1: Yard 30 → Left speaker
Play 2: Yard 80 → JUMPS to right speaker (50 yard bomb!)
```

Dramatic stereo movement = explosive play!

### How to Use

1. **Get headphones or stereo speakers** (essential!)

2. **Run the demo:**
   ```bash
   python audio_player.py
   ```
   Listen to the sample drive move from left to right

3. **Try real games:**
   ```bash
   python experiment_football_audio.py
   ```
   - Pick Option 1 (View drives)
   - Select any drive
   - Type 'y' when asked to play audio
   - **Listen with headphones!**

### Field Position Mapping

```
   0 yds                    50 yds                   100 yds
[Own Endzone] ←--------→ [Midfield] ←--------→ [Opponent Endzone]
 Full Left                 Center                    Full Right
 |----|----|----|----|----|----|----|----|----|----|
 0   10   20   30   40   50   60   70   80   90  100
```

**Equal Power Panning:** Sound stays at constant volume as it moves across the stereo field, just like a real sound source moving past you.

### Best Drives to Try

1. **Long Touchdown Drive** (10+ plays)
   - Starts in left channel
   - Gradually moves right
   - Ends in right channel celebration
   - Like watching a wave move across stereo field

2. **Back-and-Forth Drive**
   - Sound bounces left-right-left-right
   - Indicates gaining/losing yards
   - Stereo movement shows struggle

3. **Quick Score** (3-4 plays)
   - Rapid movement left to right
   - Dramatic stereo shift
   - Explosive offense

4. **Failed Drive** (3-and-out)
   - Sound stays in left channel
   - Maybe moves slightly right then back
   - Tells story of stalled offense

### Technical Details

**Stereo Panning Algorithm:**
- Uses equal power panning (constant perceived loudness)
- Pan angle calculated from field position
- Left volume = cos(angle)
- Right volume = sin(angle)

**Field Position Extraction:**
- From ESPN API: `play['start']['yardLine']`
- Normalized to 0-100 scale
- 0 = Own goal line (left)
- 50 = Midfield (center)
- 100 = Opponent goal line (right)

**Audio Channels:**
- Mono: Single channel (no stereo info)
- Stereo: Two channels (left + right position)
- 16-bit PCM WAV format
- 44.1kHz sample rate (CD quality)

### What Makes This Unique

**Most audio representations:**
- Time on X-axis
- Frequency/pitch on Y-axis
- Static stereo field

**This implementation:**
- Time flows forward (as always)
- Frequency = yards gained (pitch)
- **Stereo position = field location (spatial)**

You're hearing the game in 3 dimensions:
1. **Time** - When things happen
2. **Pitch** - How successful (yards)
3. **Space** - Where on the field

### Troubleshooting

**Can't hear stereo movement:**
- ✓ Use headphones (not phone speaker)
- ✓ Check Windows balance is centered (not all left/right)
- ✓ Try the demo first (`python audio_player.py`)
- ✓ Listen carefully - it's subtle but clear

**Sound seems to "jump":**
- Normal! Football is discrete plays, not continuous
- Big yardage = big stereo jump
- Loss = movement backwards (right to left)

**All sounds in center:**
- Drive might be all around midfield
- Try a touchdown drive from deep territory
- Look for "Yard 25" → "Yard 75" progression

### Advanced: Disable Stereo

If you prefer mono (single channel):

```python
# In audio_player.py
player = AudioPlayer()
player.stereo_enabled = False  # Disables stereo panning
```

All audio will be centered (mono) but still playable.

### The Experience

**Put on headphones. Play a touchdown drive.**

You'll hear:
- Low pitch in your left ear (own territory)
- Rising pitch moving toward center (gaining yards)
- Medium pitch in center (midfield battle)  
- High pitch in right ear (red zone!)
- Celebration tone far right (TOUCHDOWN!)

It's not just hearing the stats - it's experiencing the journey down the field.

**The offense literally marches through your headphones. 🎧🏈**
