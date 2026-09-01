## What's New in Version 0.9.5

### College football was showing a fraction of the games

On Saturday 29 August, 48 Division I college football games were played. Scores showed 8 of them.

ESPN serves the two halves of Division I separately, and Scores was only ever asking for the Football Bowl Subdivision. That is a small share of an opening weekend, which is largely FCS — so the games were not late or missing from ESPN, they were never requested.

Scores now asks for all of Division I by default: roughly 200 games a week instead of about 100. If you only follow FBS, **Settings → College football games shown** switches back to **FBS only**.

A team's own schedule always uses the widest coverage, so looking up an FCS team now works — previously it returned nothing at all.

### College basketball had the same problem, and worse

A Saturday in January was showing 21 of 145 men's Division I games, and 4 of 122 women's. Both now show the full slate. There is no setting for this one — college basketball has no equivalent split below Division I, so there is nothing to choose between.

College basketball team schedules were also nearly empty, stopping about a fortnight into the season. They now load in full.

### MLB wild card standings

The standings window could only show divisions, so the playoff race — the thing most people are actually tracking in September — was not visible anywhere.

Two new tabs sit beside the six division tabs: **AL Wild Card** and **NL Wild Card**. Each shows its league's three division leaders first, then the twelve-team wild card race in order.

The three teams currently holding a wild card spot are marked in a **Status** column — "Wild card 1", "Wild card 2", "Wild card 3" — and division leaders read "AL East leader" and so on. Teams outside the spots read "Not in a playoff spot". The playoff cut line is a value you can read and hear, rather than a line drawn across the table, so it works the same way in all three view modes and with a screen reader.

The tabs load the first time you open one, so the divisions you usually want are not held up waiting for them.

### Upgrading from 0.9.4

Scores will offer the update itself, or run `Scores-0.9.5-Setup.exe`.

---

**Platform:** Windows  
**Requires:** Windows 10 or later
