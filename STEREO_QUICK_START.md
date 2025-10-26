## 🎯 Quick Start: Stereo Field Position

### Setup (5 seconds)
1. Put on headphones
2. Run: `python audio_player.py`
3. Press ENTER when prompted

### What You'll Hear

**The Demo Drive:**
```
         LEFT SPEAKER          CENTER          RIGHT SPEAKER
        (Own Endzone)        (Midfield)      (Opponent Endzone)
              |                  |                    |
Play 1 (Yd 25): *               |                    |   ← Low pitch, left
Play 2 (Yd 28):  *              |                    |   ← Rising pitch, left
Play 3 (Yd 40):      *          |                    |   ← Higher, moving center
Play 4 (Yd 68): TOUCHDOWN!      |              *     |   ← High pitch, right!
```

**You hear the team literally move from left to right through your headphones!**

### Try Real Games

```bash
python experiment_football_audio.py
```

1. Choose Option 1 (View drives)
2. Pick drive #2 or any scoring drive
3. Type 'y' to play audio
4. **Close your eyes and listen**

The sound will travel across your stereo field as the offense advances!

### The Magic

- **Pitch (frequency)** = How many yards gained
- **Position (stereo)** = WHERE on the field
- **Duration** = Importance of play

Three dimensions of information in pure sound!

### Best Example

Find a long touchdown drive (10+ plays, 75+ yards):
- Starts far left (their 20 yard line)
- Gradually moves right with each first down
- Reaches center at midfield
- Continues right into red zone
- Ends far right with touchdown celebration

**It sounds like a wave moving across your head.** 🌊🎧

That's the offense marching down the field!
