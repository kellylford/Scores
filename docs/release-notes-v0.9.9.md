## What's New in Version 0.9.9

### Live Scores no longer freezes

On a busy Saturday, Live Scores – All Sports could stop responding and never recover. Windows marked it "Not Responding" until you closed it.

To show the latest play, Live Scores downloaded each live game's full details one at a time, and all of that work happened in the part of the app that draws the window. With 50 games in progress that took over a minute. The automatic refresh then started again as soon as it finished, so the window never got a turn.

Live Scores now downloads in the background, and the window stays usable while it does:

- **Faster:** it downloads several games at once, so a full load takes about 20 seconds instead of more than a minute and a half.
- **No pile-up:** a refresh waits until the previous one has finished.
- **Keeps your place:** your position in the list stays where it was when the scores refresh.

### Other screens that froze while loading

- **League scores:** opening a league, changing week or date, and going back from a game used to freeze the window while it downloaded. The list now opens right away on "Loading scores...", and the games replace it when they arrive.
- **Statistics:** team statistics download one team at a time, and the window used to freeze for all of it before the dialog appeared. The dialog now opens at once and fills in when the statistics arrive.

### Fewer crashes, no endless waits

- **Fewer crashes:** a few screens could close the app outright if you left them, or opened them again, while they were still loading. These were Standings, the Wild Card tabs, the fantasy cheatsheet and your favorite team cards on Home.
- **No endless waits:** every ESPN request now gives up after 15 seconds, so one slow response can no longer hang the app.

### Upgrading from 0.9.8

Scores will offer the update itself, or run `Scores-0.9.9-Setup.exe`.

---

**Platform:** Windows  
**Requires:** Windows 10 or later
