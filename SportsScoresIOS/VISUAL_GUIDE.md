# 📱 Sports Scores iOS - Visual Guide

## What Your App Looks Like

### 1. Sport Selection Screen
```
┌─────────────────────────────┐
│  Sports Scores         ⚙️   │
├─────────────────────────────┤
│                             │
│  Select a Sport             │
│                             │
│  ⚾️ MLB Baseball        >   │
│  🏈 NFL Football        >   │
│  🏀 NBA Basketball      >   │
│  🏒 NHL Hockey          >   │
│  🏈 NCAA Football       >   │
│  🏀 NCAA Men's Basketball>  │
│  🏀 NCAA Women's Basketball>│
│                             │
└─────────────────────────────┘
```

### 2. Scores View (Live Scores)
```
┌─────────────────────────────┐
│  < ⚾️ MLB Baseball      🔄  │
├─────────────────────────────┤
│  [Scores] [Standings]       │
├─────────────────────────────┤
│  ● Live - Top 3rd - 2:15   📺│
│  @ LAD (95-67)          3   │
│  vs SD (82-80)          5   │
│  Petco Park, San Diego, CA  │
├─────────────────────────────┤
│  Final                      │
│  @ NYY (102-60)         4   │
│  vs BOS (78-84)         2   │
│  Fenway Park, Boston, MA    │
├─────────────────────────────┤
│  Thu 8/29 7:05PM            │
│  @ CHC (83-79)          -   │
│  vs MIL (92-70)         -   │
│  American Family Field, WI  │
└─────────────────────────────┘
        Tap game for details >
```

### 3. Standings View - Table Mode
```
┌─────────────────────────────┐
│  < ⚾️ MLB Baseball      ↻   │
├─────────────────────────────┤
│  [Scores] [Standings]       │
├─────────────────────────────┤
│ [📊 Table][📋 Quick][📖 Full]│
├─────────────────────────────┤
│  NL West                    │
│                             │
│ Rk│Team│W │L │Win%│GB│Strk │
│ 1 │LAD │95│67│.586│- │W1  │
│ 2 │ARI │84│78│.519│11│L2  │
│ 3 │SD  │82│80│.506│13│W3  │
│ 4 │SF  │80│82│.494│15│L1  │
│ 5 │COL │59│103│.364│36│L5  │
├─────────────────────────────┤
│  AL Central                 │
│                             │
│ Rk│Team│W │L │Win%│GB│Strk │
│ 1 │MIN │82│80│.506│- │W2  │
│ 2 │CLE │76│86│.469│6 │L1  │
│ ...                         │
└─────────────────────────────┘
```

### 4. Standings View - Quick List Mode
```
┌─────────────────────────────┐
│  < ⚾️ MLB Baseball      ↻   │
├─────────────────────────────┤
│  [Scores] [Standings]       │
├─────────────────────────────┤
│ [📊 Table][📋 Quick][📖 Full]│
├─────────────────────────────┤
│  NL West                    │
│                             │
│  LAD, 95-67, .586, GB: -    │
│                             │
│  ARI, 84-78, .519, GB: 11   │
│                             │
│  SD, 82-80, .506, GB: 13    │
│                             │
│  SF, 80-82, .494, GB: 15    │
│                             │
│  COL, 59-103, .364, GB: 36  │
│                             │
├─────────────────────────────┤
│  AL Central                 │
│                             │
│  MIN, 82-80, .506, GB: -    │
│  ...                        │
└─────────────────────────────┘
```

### 5. Standings View - Full List Mode
```
┌─────────────────────────────┐
│  < ⚾️ MLB Baseball      ↻   │
├─────────────────────────────┤
│  [Scores] [Standings]       │
├─────────────────────────────┤
│ [📊 Table][📋 Quick][📖 Full]│
├─────────────────────────────┤
│  NL West                    │
│                             │
│  Los Angeles Dodgers        │
│  Rank:    1                 │
│  Wins:    95                │
│  Losses:  67                │
│  Win%:    .586              │
│  GB:      -                 │
│  Streak:  W1                │
│  Record:  95-67             │
├─────────────────────────────┤
│  Arizona Diamondbacks       │
│  Rank:    2                 │
│  Wins:    84                │
│  Losses:  78                │
│  Win%:    .519              │
│  GB:      11                │
│  ...                        │
└─────────────────────────────┘
```

### 6. Game Details - Box Score
```
┌─────────────────────────────┐
│  < Game Details             │
├─────────────────────────────┤
│         Final               │
│                             │
│    LAD              SD      │
│     3               5       │
│  (95-67)         (82-80)    │
│                             │
├─────────────────────────────┤
│ [Box Score][Plays][Leaders] │
├─────────────────────────────┤
│  Los Angeles Dodgers        │
│                             │
│  Hits:           8          │
│  Runs:           3          │
│  Errors:         1          │
│  Batting Avg:    .267       │
│  ...                        │
├─────────────────────────────┤
│  San Diego Padres           │
│                             │
│  Hits:           12         │
│  Runs:           5          │
│  Errors:         0          │
│  Batting Avg:    .308       │
│  ...                        │
└─────────────────────────────┘
```

### 7. Game Details - Plays
```
┌─────────────────────────────┐
│  < Game Details             │
├─────────────────────────────┤
│         Final               │
│    LAD 3  @  SD 5          │
├─────────────────────────────┤
│ [Box Score][Plays][Leaders] │
├─────────────────────────────┤
│  Bot 9th                    │
│  Tatis Jr. singles to right │
│  Single                     │
├─────────────────────────────┤
│  Bot 9th                    │
│  Machado grounds out to 2nd │
│  Groundout                  │
├─────────────────────────────┤
│  Top 9th                    │
│  Betts strikes out swinging │
│  Strikeout                  │
├─────────────────────────────┤
│  Top 9th                    │
│  Freeman flies out to center│
│  Flyout                     │
│  ...                        │
└─────────────────────────────┘
```

### 8. Game Details - Leaders
```
┌─────────────────────────────┐
│  < Game Details             │
├─────────────────────────────┤
│         Final               │
│    LAD 3  @  SD 5          │
├─────────────────────────────┤
│ [Box Score][Plays][Leaders] │
├─────────────────────────────┤
│  Batting Leaders            │
│                             │
│  Mookie Betts        2-4    │
│  Fernando Tatis Jr.  3-4    │
│                             │
├─────────────────────────────┤
│  Pitching Leaders           │
│                             │
│  Clayton Kershaw    6 IP    │
│  Joe Musgrove       7 IP    │
│                             │
├─────────────────────────────┤
│  RBI Leaders                │
│                             │
│  Freddie Freeman    2 RBI   │
│  Manny Machado      3 RBI   │
│  ...                        │
└─────────────────────────────┘
```

## Gestures & Interactions

### Navigation
- **Tap** sport → See scores
- **Tap** game → See details
- **Swipe left/right** → Switch between Scores/Standings tabs
- **Pull down** → Refresh data
- **Tap <** → Go back

### View Mode Switching
- **Tap segment** → Direct selection
- **Tap ↻ button** → Cycle through modes
- **Smooth animation** → Seamless transitions

### Accessibility
- **VoiceOver** → Full screen reader support
- **Dynamic Type** → Respects text size preferences
- **Voice Control** → Hands-free navigation
- **Semantic labels** → Context-aware descriptions

## Color Scheme

The app uses iOS system colors for:
- **Primary**: Blue (tappable items, accents)
- **Secondary**: Gray (labels, subtitles)
- **Background**: White/Black (auto light/dark mode)
- **Live indicators**: Red (live games)
- **Success**: Green (completed actions)
- **Warning**: Orange (errors, alerts)

**Dark Mode**: Automatically adapts to system preference!

## Responsive Design

Works perfectly on:
- 📱 iPhone (all sizes)
- 📱 iPhone Pro/Max (larger screens)
- 📱 iPhone SE (smaller screens)
- 📱 Portrait orientation
- 📱 Landscape orientation

Tables scroll horizontally on small screens to show all columns!

## What Users Will Love

✅ **Fast**: Native performance, instant responses  
✅ **Smooth**: Animations and transitions  
✅ **Accessible**: Three view modes for different needs  
✅ **Intuitive**: Standard iOS patterns  
✅ **Reliable**: Error handling and retry options  
✅ **Fresh**: Pull to refresh on all screens  
✅ **Clean**: Modern, uncluttered design  
✅ **Smart**: Auto light/dark mode  

---

This is what your Sports Scores app will look like on iPhone! 
Clean, modern, and professional. 🎉
