## What's New in Version 0.9.4

### The Rank column no longer skips numbers

Sorted by rank, the Fantasy Cheatsheet jumped: 35, 36, then 69. Further down it skipped from 519 straight to 978. Across the whole board there were 1,539 missing numbers and 251 of these jumps.

Nothing was actually missing from the board. The column was showing ESPN's own published rank, and ESPN ranks a much larger pool than a fantasy draft board uses — roughly 1,750 defensive players, 51 punters, and 32 "Team QB" entries that only a few league formats use. Those occupy rank numbers, so once they are left out the remaining numbers have holes in them. The jump from 36 to 69 was exactly the 32 Team QB slots.

The Rank column now counts the board itself — 1, 2, 3, with nothing missing — in exactly the order ESPN ranks them. The number now answers the question you are actually asking it: how many players are ahead of this one.

ESPN's own rank is still there if you want it. It appears on the player details screen as **ESPN overall rank**, and in the CSV export as two extra columns, so you can still cross-reference against ESPN's site.

### Upgrading from 0.9.3

Scores will offer the update itself, or run `Scores-0.9.4-Setup.exe`.

---

**Platform:** Windows  
**Requires:** Windows 10 or later
