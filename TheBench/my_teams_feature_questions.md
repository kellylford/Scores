# My Teams Feature - Clarifying Questions

Before creating the full specification and work item for the "My Teams" feature, please provide clarification on the following points:

## 1. Team Selection Scope
Should all sports leagues currently supported by the app be included in the configuration tabs (NFL, NBA, MLB, NCAAF, etc.), or do you want to limit it to specific leagues initially?

**Your Answer:**
Answer: Limit to NFL, MLB and NCAAF for now.

## 2. Live Game Display
For live games in the My Teams view, should it show the same level of detail as the Live Scores view (quarter/inning, time remaining, etc.) or just the basic score?

**Your Answer:**
Same as live game view

## 3. Past/Future Navigation
For the past/future toggle:
- Should "past" show just the most recent game, or allow browsing through multiple past games?
- Should "future" show just the next game, or the entire upcoming schedule?

**Your Answer:**
Just past one item from either past or future because this is going to toggle the full list.

## 4. Configuration Access
Besides the automatic invocation when no favorites exist, should there be another way to access the team configuration (like a menu item or button in the My Teams view)?

**Your Answer:**
Yes, in addition to the save option, have a configure button.

## 5. Team Identification
Should the favorites be stored by team ID, team name, or both? This affects how the system handles potential team name changes or relocations.

**Your Answer:**
Use your judgement from what you know but I'd suspect team ID.

## 6. Empty States
What should be displayed in the My Teams view if:
- A favorited team has no recent games?
- A favorited team has no upcoming games?
- All favorited teams are in their off-season?

**Your Answer:**
For now we can show no games available so it would be soemthing like Milwaukee browers - no games available.

## 7. Performance Considerations
Should there be a limit on the number of teams that can be favorited, or should it support unlimited favorites?

**Your Answer:**
Cap this at 20 for now.

## 8. Integration
Should the My Teams feature integrate with any existing notifications or alerts in the app?

**Your Answer:**
No, not that I can think of here.

---

## Follow-up Clarification Questions

Based on your answers above, I need a few more clarifications:

### 9. Past/Future Toggle Clarification
You mentioned "Just past one item from either past or future because this is going to toggle the full list." Could you clarify what you mean by "toggle the full list"? Do you mean:
- Show the most recent game for each team when in "past" mode, and the next game for each team when in "future" mode?
- OR something else?

**Your Answer:**
I mean just what you said. The reality is that most times, a team will not be playing live so a user (me) will want to know what's going on with that team. Either their most recent game or what's coming next.

### 10. Configuration Dialog Save vs Configure
You mentioned both a "save option" and a "configure button". Should the configuration dialog have:
- A "Save" button that saves changes and closes the dialog?
- A "Configure" button in the My Teams view that opens the configuration dialog?
- OR both buttons within the configuration dialog itself?

**Your Answer:**
The configure dialog should have the save button. It would be on all tabs. The my teams view would have the configure button to trigger the conciguration experinece where you would save.

### 11. Empty State Display
For the "no games available" scenario, should this be:
- Listed alongside teams that do have games (mixed list)?
- Shown in a separate section?
- Should these teams without games be hidden entirely with just a count/message?

**Your Answer:**
A separate section sounds best for now.

### 12. JSON File Location
You specified the JSON file should be in "the same directory as the scores executable." For development/testing purposes, should it also work when running from the Python source (storing relative to the main.py file)?

**Your Answer:**
Yes.
---

**Instructions:** Please edit this file with your answers and let me know when you're done so I can continue creating the full specification and work item.
