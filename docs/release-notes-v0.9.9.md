## What's New in Version 0.9.9

This is the first release that ships the Windows app and the iPhone app together, at the same version number.

### Windows: no more freezes while screens load

0.9.8 fixed the worst freezes, in Live Scores and league scores. This release moves the rest of the downloads into the background, so the window stays usable while they load:

- **Game details:** opening a game, Refresh, and F5 inside a game's details. The game opens right away on "Loading game details..." and fills in within a second or so.
- **Polls, Teams and Venues:** the row you pressed Enter on reads "(loading...)" until the dialog opens. Venues used to freeze the window for up to 20 seconds.
- **Bowls & Playoffs:** opens at once and fills in.
- **Pitch sounds:** the keyboard keeps working while a pitch or a whole pitch sequence plays.

### Windows: other fixes

- **Updating while an installer is already open:** if the installer from an earlier attempt is still open, often hidden behind other windows, Scores now tells you to switch to it with Alt+Tab. It used to fail with "Permission denied".
- **Changing season or World Cup phase quickly:** the TeamHub schedule and the World Cup bracket no longer show results for a season or phase you just left.
- **Game Wrap Up** now works for every sport. It was fetching a college football game whatever the sport.

### iPhone: golf

- **Correct totals mid-round:** golf leaderboards and the golf row in Live Scores now count the round being played. ESPN's total leaves it out, so a golfer at -11 could show as -3.
- **Ties:** golfers on the same score now share a position, shown as T1.

### Upgrading

On Windows, Scores will offer the update itself, or run `Scores-0.9.9-Setup.exe`. On iPhone, update through TestFlight.

---

**Platforms:** Windows 10 or later; iPhone through TestFlight
