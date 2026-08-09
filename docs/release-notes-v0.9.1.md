## What's New in Version 0.9.1

### Fantasy Football Cheatsheet

Open **NFL** and choose **Fantasy Cheatsheet** for a draft board covering every draftable player plus all 32 team defenses and kickers — around 370 rows in all, with ESPN's consensus rank, average draft position, auction value, and projected season points.

It is a starting point for your draft rather than a live draft assistant, and it is built to be worked entirely from the keyboard:

- **Search** by player name or team abbreviation.
- **Position** narrows the board to one position, or to FLEX (RB, WR and TE together).
- **Team** shows a single NFL team.
- **Sort by** rank, ADP, auction value, projected points, or name.
- **Scoring** switches between Standard, Half-PPR and PPR. Projected points change with it, instantly — nothing is downloaded again. ESPN publishes separate rankings for Standard and PPR only, so Half-PPR uses the PPR rankings.
- **Space** marks the selected player drafted or available. Tick **Hide drafted players** and they drop off the board as your draft goes by. Your marks are saved and are still there next time you open Scores.
- **Enter** opens full details for a player, including projected points in all three scoring formats.
- **Reload from ESPN** downloads the board again after a big injury or trade, keeping your drafted marks.

The board works in all three table view modes — Table, Quick List and Full List — so Alt+V, Alt+T, Alt+Q and Alt+F behave exactly as they do everywhere else in Scores.

Kickers and team defenses show **N/A** for projected points. ESPN's published projections for those two positions are not usable, so Scores shows no number rather than a wrong one; their rank, ADP and auction value are accurate.

Drafted marks are remembered per season, so last year's draft will not pre-cross-off this year's board.

### NFL Preseason

The NFL screen now shows preseason games. It never did before — open it in August and you would get the regular-season opener several weeks away, labelled simply "Week: 1", with no way to reach the games actually being played that week.

Weeks are now named the way ESPN names them, so you get **Hall of Fame Weekend**, **Preseason Week 1**, **Wild Card** and **Super Bowl** rather than a bare number that means something different depending on the time of year. **Previous Week** and **Next Week** (Alt+P and Alt+N) run straight through the whole season, rolling from the last preseason week into Week 1 of the regular season and on into the playoffs.

One related fix: a week's games were being fetched with a date range one day too long, which pulled the *following* week's Thursday game into the week you were looking at. That affected the regular season as well.

### Upgrading from 0.9.0

Scores will offer the update itself, or run `Scores-0.9.1-Setup.exe`.

---

**Platform:** Windows  
**Requires:** Windows 10 or later
