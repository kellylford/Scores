## What's New in Version 0.9.9.1

A Windows-only update. The iPhone app stays at 0.9.9.

### Follow live games from a sport's own scores

Live games in a sport's scores list now show the current play, the same as Live Scores does. Before, the In Progress section showed only the score and clock.

- **Football:** the last play, then the clock, which team has the ball, and down and distance.
- **Baseball:** runners on base, the count and outs, who's batting, and the last play.
- **Other sports:** the latest play after the score.

The plays come from the scores already being downloaded, with no extra request per game.

### Fixes

- **NFL and college football scores were running behind.** In a football week's scores list, live games could be minutes out of date, sometimes by a whole score, because ESPN's week-by-week scores lag its daily ones. Live games now come from the daily scores, including late games still going after midnight.
- **F5 keeps your place.** Refreshing a sport's scores list now lands back on the game you were on instead of jumping to the top, so you can keep following a game with F5.
- **Football clock read twice.** In Live Scores, a live football game read its clock twice, as in "8:30 Q4 ... (8:30 - 4th)". It's now read once.
- **Scores read backwards in Live Scores.** Some games read the home score first after an away-first name. "Colts at Commanders - 13-30" meant the Colts had won 30-13. Scores now follow the team order.
- **Status read twice.** Live games with no play to show no longer read their status twice.

### Upgrading

Scores will offer the update itself, or run `Scores-0.9.9.1-Setup.exe`.

---
