## What's New in Version 0.9.8

### Live Scores is fast, and no longer freezes

On a busy Saturday, Live Scores – All Sports could stop responding and never recover. Windows marked it "Not Responding" until you closed it.

Live Scores now works the way the iPhone app does. It asks ESPN for each league's scoreboard for today, all at once, and reads the latest play straight from it. Before, it also downloaded the full details of every live game, one game at a time. It now loads in about 5 seconds instead of more than a minute, and the window stays usable while it does:

- **Refreshes don't pile up.** A refresh waits until the previous one has finished.
- **Keeps your place.** Your position in the list stays where it was when the scores refresh.

### Golf in Live Scores

Golf tournaments used to show up as "Unknown at Unknown". They now have their own section at the top of Live Scores, like the iPhone app, for example:

> PGA Tour: Bank of Utah Championship, Round 3 - In Progress. Leaders: T1. Kevin Streelman, -19; T1. Austin Smotherman, -19; 3. Doug Ghim, -18

Press Enter on a tournament to open its leaderboard.

Golf scores are also correct now for golfers partway through a round. ESPN's total leaves out the round being played, so a golfer at -11 could show as -3. Scores now adds up the rounds itself, both in Live Scores and on the leaderboard.

### Scores grouped by game status

A league's scores list used to show games in the order ESPN sends them, which is by kickoff time. On a college football Saturday that mixed finished games, games in progress and evening kickoffs together.

Games are now grouped the same way the iPhone app groups them:

- **In Progress**, including suspended games
- **Upcoming**, soonest first
- **Completed**
- **Postponed / Cancelled**

Each group starts with a header that gives its count, such as "Upcoming, 42 games". The arrow keys stop on the headers and the screen reader reads them, and pressing Enter on a header does nothing.

### Other screens that froze while loading

- **League scores:** opening a league, changing week or date, and going back from a game used to freeze the window while it downloaded. The list now opens right away on "Loading scores...", and the games replace it when they arrive.
- **Statistics:** the dialog opens at once and fills in when the statistics arrive, instead of freezing the window for several seconds before it appeared.

### Fewer crashes, no endless waits

- **Fewer crashes:** a few screens could close the app outright if you left them, or opened them again, while they were still loading. These were Standings, the Wild Card tabs, the fantasy cheatsheet and your favorite team cards on Home.
- **No endless waits:** every ESPN request now gives up after 15 seconds, so one slow response can no longer hang the app.

### Upgrading from 0.9.7

Scores will offer the update itself, or run `Scores-0.9.8-Setup.exe`.

---

**Platform:** Windows
**Requires:** Windows 10 or later
