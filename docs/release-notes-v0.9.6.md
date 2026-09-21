## What's New in Version 0.9.6

### The NHL, NBA and college seasons roll over on their own

Open an NHL team's schedule in September 2026 and it showed the 2025-26 season — the one that finished in June. The same was true for the NBA and for college basketball and hockey, and the Season list in a team's Schedule tab stopped at 2025-26, so there was no way to reach the current season at all.

ESPN numbers a winter season by the year it *ends* in: the 2026-27 NHL season is season 2027. That number was written into the code rather than worked out from the date, so it stayed on whatever season was current when the release was built.

The app now works the season out per sport:

- **NHL, NBA, college basketball and college hockey** use the year the season ends in, and turn over in July — once the previous season is finished and the new schedule has been published.
- **NFL and college football** stay on the previous season through January and February, so a schedule opened during the playoffs is still the season being played.
- **MLB** continues to follow the calendar year.

The Season list follows, so it now opens on **2026-27 Season** and lists earlier seasons under the two years they span. NBA standings track the current season too, instead of the one frozen into the request. And if you look during the gap between one season ending and the next schedule being published, the schedule falls back to the season that just finished rather than showing nothing.

### Upgrading from 0.9.5

Scores will offer the update itself, or run `Scores-0.9.6-Setup.exe`.

---

**Platform:** Windows  
**Requires:** Windows 10 or later
