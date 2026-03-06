# Live Accessibility Label Debugging (iOS)

This guide explains how to enable debug logging for live-game VoiceOver labels.

## What this logs

When enabled, the app prints the final accessibility strings used by live score rows in:

- `ScoresView` game rows
- `LiveScoresView` compact game rows

This is useful for catching issues like trailing placeholder clocks (for example `0:00`) before TV info.

## Prerequisites

- Build configuration must be `Debug`
- Run from Xcode (so you can see console output)

## Enable logging

1. Open the iOS project in Xcode:
   - `iOS/SportsScoresApp/SportsScores.xcodeproj`
2. Go to `Product` -> `Scheme` -> `Edit Scheme...`
3. Select `Run` in the left sidebar.
4. Open the `Arguments` tab.
5. Under `Arguments Passed On Launch`, add:
   - `-A11YDebugLiveLabels`
6. Run the app.
7. Open pages with live games (`Live Scores` and sport score pages).
8. Watch Xcode console output.

## Expected log format

You will see lines like:

```text
[A11Y][ScoresView][MLB][401697123] Phillies 4, at Pirates 3, Top 9th, on MLB.TV
[A11Y][LiveScoresView][401697123] Phillies 4, at Pirates 3, Top 9th, on MLB.TV
```

## Turn logging off

- Remove `-A11YDebugLiveLabels` from scheme arguments, or uncheck it.

## Notes

- Logging is guarded by `#if DEBUG`, so it does not run in Release builds.
- Only live rows are logged.
- Source hooks:
  - `iOS/SportsScoresApp/SportsScores/Views/ScoresView.swift`
  - `iOS/SportsScoresApp/SportsScores/Views/LiveScoresView.swift`
