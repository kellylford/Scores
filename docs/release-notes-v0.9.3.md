## What's New in Version 0.9.3

### The Fantasy Cheatsheet was missing most of the player pool

The draft board carried about 370 players. It now carries 1,026.

The board was capped at ESPN's overall draft rank, on the assumption that a worse rank meant a less relevant player. That assumption was wrong. ESPN ranks Ricky Pearsall 1507th and Tyreek Hill 1899th; both are rostered in real leagues, and neither appeared on the board at all.

There is no cutoff any more. The board now includes every player ESPN publishes a fantasy rank for, minus the ones ESPN flags as inactive — retirees it still ranks, all of them owned in 0.0% of leagues. Rookie filters cover 84 rookies rather than 34, and **Export to CSV** writes 1,026 rows.

The board is deliberately deeper than any league will draft, so late-round fliers and waiver targets are on it. The position and team filters, the search box, and sorting by rank keep it manageable.

### Average draft position is honest now

ESPN does not leave ADP empty for players nobody drafts — it hands out a placeholder just past the end of a real draft, about 170 this season. 826 of the 1,026 players carry it.

That placeholder was being displayed as though it were a real draft position. Worse, ESPN jitters it in the third decimal, so sorting by ADP put hundreds of rows in an order driven by digits too small to display — a deep camp body could sit above a genuine starter with both rows reading "170.0".

Players with no real ADP now show **N/A** and sort to the bottom in rank order. The 200 players who genuinely have one are unaffected.

### Also in this release

- The team filter has a **Free Agents** entry. That is 212 players, Tyreek Hill and Keenan Allen among them, previously reachable only by accident.
- The position, team, sort and scoring controls no longer redraw the board on every keypress while you arrow through them.
- Closing the cheatsheet now releases it, so opening it repeatedly during a draft does not grow memory.

### Upgrading from 0.9.2

Scores will offer the update itself, or run `Scores-0.9.3-Setup.exe`.

---

**Platform:** Windows  
**Requires:** Windows 10 or later
