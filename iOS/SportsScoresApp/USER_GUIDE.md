# Sports Scores — iOS User Guide

This guide covers all features of the Sports Scores iOS app, including the audio and haptic features designed for blind and low-vision users.

---

## Getting Around

### Home Screen

The app opens on a list of sports. Tap any sport to open its scores and standings. The first row — **Live Scores** — shows current games across all sports at once.

Available sports:

- MLB Baseball
- NFL Football
- NBA Basketball
- NHL Hockey
- NCAA Football
- NCAA Men's Basketball
- NCAA Women's Basketball
- WNBA Basketball
- NCAA Men's Hockey
- NCAA Women's Hockey

The gear icon in the top-right corner opens **Settings**.

---

### Sport Screen

Each sport screen has four tabs across the top:

| Tab | Contents |
|-----|----------|
| **Scores** | Games for the selected date or week, grouped by status |
| **Standings** | Division or conference standings |
| **News** | Recent news and headlines |
| **Stats** | League statistical leaders |

Some sports add a **Polls** tab when rankings are available.

Tap any game row to open its detail view.

#### Date Navigation (Scores tab)

A date bar sits below the tab picker. Tap the left or right arrows to move one day at a time (or one week for football). Tap **Today** to jump back to the current date from wherever you are. Tap the date itself to open a calendar and jump to any specific day.

For **NFL and NCAA Football**, the bar shows a week number instead of a calendar date. Navigation moves by week.

#### Game Sections

Games on the Scores tab are grouped into three sections:

- **In Progress** — games currently being played
- **Upcoming** — games scheduled later today or this week
- **Completed** — games that have finished

Only sections with games are shown. If there are no games at all, a message tells you so.

#### Auto-Refresh

The clock icon in the top-right corner controls how often scores refresh automatically. Options: 1 minute, 2 minutes, 5 minutes, and manual. Pull down on the list to refresh immediately at any time.

---

### Game Detail Screen

Game detail has four tabs, swiped left and right:

| Tab | Contents |
|-----|----------|
| **Box Score** | Team-level stats (football) or full line score (baseball) |
| **Plays** or **Drives** | Play-by-play (basketball, hockey) or drive summaries (football) |
| **Info** | Game leaders, injuries, officials, venue, news |
| **More** | Win probability, season series — MLB only |

The game header at the top shows teams, score, and current status. For games in progress it includes period and clock.

#### Play-by-Play

For timed sports (basketball, hockey, NFL), plays are grouped by period and ordered within each period. Each play shows:

1. What happened (the play description)
2. When it happened (game clock)
3. Score at that moment

For baseball, plays are pitch-level. See the **Baseball Audio Features** section below.

---

## Settings

Open Settings from the gear icon on the home screen.

### Team Name Display

Controls how team names appear in scores and VoiceOver labels. Four options:

- **Abbreviation** — "BOS", "NYY" — shortest; good if you know team codes
- **City** — "Boston", "New York"
- **Nickname** — "Red Sox", "Yankees"
- **Full Name** — "Boston Red Sox", "New York Yankees" — most verbose; best for VoiceOver if you want no ambiguity

The setting applies everywhere in the app: game rows, play-by-play, accessibility labels.

---

## VoiceOver

The app is designed for VoiceOver from the start. Some specific behaviors to know:

- Game rows combine all their sub-elements into a single VoiceOver item. Reading order is: away team, away score, home team, home score, game status.
- Scores are grouped into labeled sections (In Progress, Upcoming, Completed) so you can jump between sections using the rotor's Headings or scroll by container.
- Play-by-play rows read as a single label in the order: what happened, clock, score.
- The date control in the toolbar supports swipe up/down to increment or decrement the date without opening the picker.

---

## Baseball Audio Features

MLB has two optional audio exploration tools, designed to give a spatial sense of the game through sound and touch. Both are fully usable with screen readers. Neither requires looking at the screen.

### Stadium Field Tour

**Where to find it:** Tap the **Stadium Tour** button (the walking figure icon) in the top-left corner of the MLB scores screen. You do not need to have a game open. You can also access it from a game's Info tab by tapping the venue name.

**What it does:** Displays a scale drawing of a real MLB stadium. You drag your finger around the field and hear a sound that changes based on what type of ground you're touching.

**The three terrain sounds:**

| Surface | Sound character |
|---------|----------------|
| **Fair territory** (grass) | Soft, smooth swish — all high frequencies removed, like wind through grass |
| **Warning track** (cinder/gravel) | Coarser, with a slight crunch — a 6-sample filtered noise with slow amplitude modulation |
| **Foul territory** (hard surface) | Rough, full-spectrum scrape — barely filtered white noise |

The sound is **continuous** while your finger is down — no gaps or stutters. Stereo panning moves with your finger: left field sounds left, right field sounds right, center field is centered.

When you lift your finger, VoiceOver announces the zone name (e.g., "Left field warning track, 330 feet from home"). A haptic pulse also fires when you cross a zone boundary during a drag.

**Navigating by stadium:**

A picker at the top lets you choose from all 30 MLB parks. Each park uses real wall distances: left field line, left-center, center, right-center, right field line. Notable features (like the Green Monster or Tal's Hill) are listed in an expandable section at the bottom.

**VoiceOver usage:** The canvas is a direct touch area — VoiceOver passes your touches directly to the app instead of intercepting them. To enter the canvas with VoiceOver on: swipe to focus the field element, then drag freely. Lift your finger to hear the location announced.

---

### Pitch Zone Explorer

**Where to find it:** Open a game detail for any MLB game that has play-by-play data. In the **Plays** tab, tap **Explore Zone** next to the Strike Zone Map button.

**What it does:** Displays the pitch coordinate data for each at-bat as a sound map. Each dot on the canvas represents one pitch. Drag your finger across it and you hear tones that encode where each pitch was thrown.

**How the audio encodes location:**

- **Pitch height** → musical note on an A-minor pentatonic scale. High in the zone = higher note. Low in the zone = lower note. Notes are always harmonious with each other.
- **Horizontal position** → stereo pan. Inside (toward batter) = panned toward that side. Outside = other side.
- **Pitch velocity** (when available) → note duration. 105 mph fastball = short crisp note. 80 mph changeup = longer, more sustained note.

The waveform is harmonic-rich (fundamental + 2nd and 3rd partials), giving it a vibraphone-like quality rather than a synthetic beep.

**Two ways to navigate:**

1. **Drag to explore** — drag your finger around the zone. Audio plays the coordinates under your finger as you move. When you lift, VoiceOver announces a full pitch summary: pitch number, type, velocity, location, result, and count.

2. **Flick up/down to step pitch by pitch** — with the canvas focused in VoiceOver, flick up or down to move to the next or previous pitch. Audio plays for each pitch. The current value (e.g., "Pitch 3 of 7: Four-seam FB") updates in VoiceOver's value field.

The adjustable action works the same whether you discovered a pitch by dragging or came to it fresh via flicking — both methods land on the same pitch and play the same audio.

**At-bat navigation:**

Below the zone canvas is an at-bat navigation bar. Use the arrows to move between at-bats, or use the **All at-bats** toggle to see all pitches from the whole game overlaid at once.

A batter hand badge (Left-handed / Right-handed) is shown so you know which side of the plate the intended location (inside/outside) is relative to.

---

## Data Notes

All data comes from ESPN's public API and refreshes in real time. A few things to know:

- **MLB Spring Training** runs February–March. During that window, the app defaults to spring training games. Regular season starts in late March.
- **NBA and WNBA** season years follow the second year of the season (2025–26 season shows as 2026).
- **NCAA Hockey** data from ESPN is sometimes incomplete — box scores or play-by-play may be missing for some games.
- Game times are shown in your device's local time zone.
