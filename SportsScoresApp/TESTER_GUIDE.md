# Sports Scores — TestFlight Tester Guide

Sports scores app covering 10 leagues: MLB, NFL, NBA, NHL, NCAA Football/Basketball (men's/women's), WNBA, NCAA Hockey. Live data from ESPN's API.

## Navigation Basics

App opens on a sports list. **Live Scores** shows all active games. Tap any sport for scores, standings, news, stats, and polls.

**Scores tab**: Use arrows to move through dates (or weeks for football). Tap **Today** to return to current date. Tap the date for a calendar picker. Clock icon sets auto-refresh (30s/1m/2m/Manual). Pull down to refresh manually.

Games group as: In Progress, Upcoming, Completed. Tap any game for detail view.

**Game detail** (swipe between tabs): Box Score, Plays/Drives, Info (leaders/injuries/venue), More (MLB only—win probability/season series).

**Score monitoring**: Swipe left on any game row, tap **Monitor**. Get notifications when the score changes.

**Settings**: Gear icon. Change team name display (Abbreviation/City/Nickname/Full).

## Testing Checklist

- Navigate dates/weeks, try calendar picker
- Open games in different states (upcoming/live/completed), check all tabs load
- Verify standings, news, stats populate correctly
- Tap team names to open schedules
- Set 30-second auto-refresh during live games
- Monitor a game and verify notifications fire on score changes

## MLB Exploration Features

Two features explore game data through sound and touch. Use headphones for full spatial effect.

### Stadium Tour

Tap **Stadium Tour** (walking figure icon) on MLB scores screen, or tap venue name in game Info tab.

**Drag your finger** around a scale drawing of a real stadium. Continuous sound changes with terrain:
- **Fair territory** — soft, smooth (grass)
- **Warning track** — coarser, crunchy (gravel)  
- **Foul territory** — rough, full-spectrum (hard surface)

Sound pans spatially: left field sounds left, right field sounds right. Lifting your finger announces zone name and distance. Haptic pulse fires at zone boundaries.

Picker at top switches between all 30 MLB parks with real wall distances.

**Test**: Drag from home plate to left field. Listen for grass → warning track → foul territory transitions. Compare different stadiums (Fenway's Green Monster vs. others).

### Pitch Zone Explorer

Open MLB game with play-by-play. In **Plays** tab, tap **Explore Zone** next to Strike Zone Map.

**Drag your finger** across pitch locations. Tones encode:
- **Height** → musical note (high pitch = high note, low = low note)
- **Horizontal** → stereo pan (inside = batter's side, outside = opposite)
- **Velocity** → duration (fastball = short, changeup = longer)

Pentatonic scale keeps notes harmonious. Lifting announces: pitch number, type, velocity, location, result, count.

**Alternative**: Flick up/down to step through pitches sequentially.

Arrows navigate between at-bats. **All at-bats** toggle overlays entire game.

**Test**: Explore multiple at-bats. Distinguish high fastballs from low curves by sound. Try "All at-bats" view. Compare power vs. finesse pitchers.

## Known Quirks

- **Spring training** (Feb–Mar): seasontype 1. Regular season starts late March.
- **NBA/WNBA**: season years use year+1 (2025-26 = 2026).
- **NCAA Hockey**: data sometimes incomplete.

## Feedback

Note bugs, confusion, or slowness. For exploration features: Does spatial audio work? Can you distinguish pitch locations and stadium zones by sound? Send feedback through TestFlight.