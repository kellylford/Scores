# iOS Spatial / Touch Exploration Plan

Five accessibility-first features that give VoiceOver users a tactile + audio
way to "see" baseball and football data.  The goal is continuous, real-time
sonification as the user drags a finger — not a static screen-reader
description.

**Data source:** all coordinates come from the live ESPN API.
Baseball pitches use a 0–255 integer grid (`pitchCoordinate.{x,y}`).
NFL play positions use yard-line integers (0–100).

---

## Feature 1 — Pitch Zone Explorer ✅ SHIPPED (v0.56)

**What it is:** Full-screen drag canvas showing where pitches were thrown for a
single at-bat (or the whole game).  Audio pitch rises as you move up in the
zone; stereo pan shifts left/right.  Touching a pitch dot triggers a haptic and
adds it to an "Explored" list you can replay.

**Files:**
- `SportsScoresApp/SportsScores/Views/PitchZoneExplorerView.swift` — main view
- `SportsScoresApp/SportsScores/Services/PitchAudioEngine.swift` — `playCoordinate(espnX:espnY:velocity:)` method

**Entry point:** "Explore Zone" button on the Plays tab of any MLB game that has
pitch coordinate data.  Appears beside the existing "Strike Zone Map" button.

**Accessibility highlights:**
- `.accessibilityDirectTouch()` so VoiceOver doesn't block the drag
- `.accessibilityAdjustableAction` on both the canvas and the at-bat nav bar
  let users step through pitches and at-bats without lifting their finger
- Strike zone boundary crossing → medium haptic + announcement ("Strike zone" /
  "Ball")
- Landing on a pitch dot → light haptic + pitch added to explored list
- "Explored pitches" expandable list, each item tapable to replay audio

**Known gaps / future ideas:**
- Currently draws strike zone at fixed ESPN proportions; could extend to show the
  called-strike zone inferred from actual pitch outcomes for the game
- No two-finger pan to scroll through at-bats (rely on nav bar for now)
- Could add pitch type audio cue (different waveform per pitch type)

---

## Feature 2 — Spray Chart / Field Impact Explorer 🔲 NOT STARTED

**What it is:** After a ball is put in play, ESPN sometimes returns hit
coordinates (`hitCoordinate.{x,y}`).  A canvas showing where batted balls
landed with audio + haptic would let VoiceOver users "read" a spray chart.

**Data availability:** `hitCoordinate` is present on `in-play-*` pitch result
plays when available;  confirmed in API spot-checks but not 100% consistent.

**Planned entry point:** Second tab or toggle inside `PitchZoneExplorerView`.

**Key design questions:**
- Use the same 0–255 grid as pitch coordinates? (likely yes — same canvas)
- Infield vs outfield distinction via color + haptic intensity
- Show only current batter vs full game spray

---

## Feature 3 — At-Bat Timeline Scrubber 🔲 NOT STARTED

**What it is:** A horizontal scrubber that plays the count progression of an
at-bat.  Swipe right → move through pitches; each stop plays audio and announces
"Pitch 3: 94 mph four-seam, 2-1 count, middle-in."

**Planned entry point:** Accessible action inside `PitchZoneExplorerView` or in
the existing `MLBPlaysView` at-bat rows.

**Why useful:** Lets a VoiceOver user "replay" an at-bat without homing in on
the canvas; purely sequential rather than spatial.

---

## Feature 4 — NFL Drive Strip Explorer 🔲 NOT STARTED

**What it is:** A horizontal strip (yard 0–100) showing each play in an NFL
drive.  Audio pitch rises as you move downfield; haptic on scoring plays.

**Data source:** `plays[].yardsToEndzone` or `plays[].start.yardLine` — already
decoded in `GenericPlaysView`.

**Planned entry point:** New button in the Drives tab of NFL game details.

**Key design questions:**
- One strip per drive vs. all drives on one long canvas?
- Down-and-distance vs. just yardage for the audio gap?
- Whether to use `PitchAudioEngine` or a simpler single-tone approach

---

## Feature 5 — Baseball Field Grand Tour ✅ SHIPPED (v0.56)

**What it is:** An interactive to-scale schematic of any MLB stadium that the
user can drag around to learn distances, explore zones (warning track, bases,
mound, foul territory, outfield), and hear audio that maps to distance and
direction.

**Files:**
- `SportsScoresApp/SportsScores/Models/StadiumGeometry.swift` — all 30 MLB parks
  with accurate LF/LC/CF/RC/RF distances, wall heights, roof type, notable
  features; wall arc interpolation; zone detection
- `SportsScoresApp/SportsScores/Views/BaseballFieldTourView.swift` — field canvas + audio
- `SportsScoresApp/SportsScores/Services/PitchAudioEngine.swift` — `playFieldCoordinate(fieldX:fieldY:maxHalfWidth:maxDepth:)` method

**Entry point:** Small walk icon beside the venue name in the game header of any
MLB game.  Stadium is preselected to match the venue; user can switch to any of
the 30 parks via a picker.

**Stadiums included (all 30 MLB parks):**
AL East: BAL (Camden Yards), BOS (Fenway — 37 ft Green Monster), NYY, TB
(Tropicana Field, dome), TOR (Rogers Centre, dome).
AL Central: CWS, CLE, DET (420 ft CF), KC, MIN.
AL West: HOU (crawl space corner 436 ft CF), LAA, OAK, SEA, TEX.
NL East: ATL, MIA, NYM, PHI, WSH.
NL Central: CHC (Wrigley — ivy-covered walls), CIN, MIL, PIT, STL.
NL West: ARI, COL (mile-high altitude), LAD, SD, SF (309 ft RF / McCovey Cove).

**Notable features surfaced in the UI:**
Each stadium has a `notableFeatures` list that appears in an expandable section
below the canvas (e.g. "37-foot Green Monster in left field", "ivy-covered
outfield walls", "hill in center field").

**Known gaps / future ideas:**
- Wall heights aren't drawn to scale in the canvas (only listed in notable features)
- No crowd noise or reverb difference between open vs dome stadiums yet
- Could animate a "ball path" for a specific play

---

## Infrastructure built for these features

| Component | File | Notes |
|---|---|---|
| `PitchAudioEngine.playCoordinate` | `Services/PitchAudioEngine.swift` | Short drag-mode tone, 0.18 s |
| `PitchAudioEngine.playFieldCoordinate` | `Services/PitchAudioEngine.swift` | Maps real-world feet to frequency + pan |
| `StadiumGeometry` model | `Models/StadiumGeometry.swift` | 30 parks, Equatable + Hashable |
| `StadiumGeometry.detectZone` | `Models/StadiumGeometry.swift` | Named zone + distance |
| `StadiumGeometry.wallArcPoints` | `Models/StadiumGeometry.swift` | 19-point arc for canvas drawing |

---

## Remaining work (priority order)

1. **Feature 2 — Spray Chart** — verify `hitCoordinate` availability, build view
2. **Feature 3 — At-Bat Scrubber** — pure accessibility feature, no canvas needed
3. **Feature 4 — NFL Drive Strip** — football companion to features 1–2
4. **Feature 5 refinements** — wall height 3D hint, dome ambient audio

---

*Last updated: March 2, 2026*
