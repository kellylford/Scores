# TestFlight Submission Checklist

Items are grouped by who does the work and ordered by priority.
Hard blockers are marked **[BLOCKER]** — the build will not archive or will be rejected without them.
Everything else is strongly recommended before inviting outside testers.

---

## 1. App Icon — [BLOCKER]

**What's missing:** The `AppIcon.appiconset` folder contains only `Contents.json`. There is no actual image file. Xcode will produce a warning and App Store Connect will reject the binary.

**What's needed:**
- One PNG at exactly **1024 × 1024 pixels**, RGB, no alpha channel, no rounded corners (Apple applies the mask).
- Drop it into `SportsScoresApp/SportsScores/Assets.xcassets/AppIcon.appiconset/`.
- Update `Contents.json` to reference the filename. The minimal correct `Contents.json` for a modern Xcode project (single universal icon) is:

```json
{
  "images" : [
    {
      "filename" : "AppIcon-1024.png",
      "idiom" : "universal",
      "platform" : "ios",
      "size" : "1024x1024"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
```

**Design guidance:** The icon should communicate "sports scores" at a glance. A scoreboard, stadium, or simple bold typography on a strong color background works well and reproduces clearly at small sizes. You do not need multiple sizes — modern Xcode generates them from the 1024px master.

---

## 2. Privacy Manifest — [BLOCKER for external TestFlight / App Store]

**What's missing:** No `PrivacyInfo.xcprivacy` file exists anywhere in the project.

**Why it matters:** Since May 2024, Apple requires a privacy manifest for any app that accesses a "required reason API." This app uses `UserDefaults` directly (in `AppSettings.swift` and `ScoreMonitorService.swift`), which is on Apple's required-reason API list. Uploads to App Store Connect without this file produce a compliance warning and will eventually be hard-rejected.

**What to do:** Create `SportsScoresApp/SportsScores/PrivacyInfo.xcprivacy` with the following content and add it to the Xcode target:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>NSPrivacyAccessedAPITypes</key>
  <array>
    <dict>
      <!-- UserDefaults — used to store app preferences (team name setting,
           auto-refresh interval, monitored game IDs). No user-identifying
           data is stored. -->
      <key>NSPrivacyAccessedAPIType</key>
      <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
      <key>NSPrivacyAccessedAPITypeReasons</key>
      <array>
        <string>CA92.1</string>
      </array>
    </dict>
  </array>

  <!-- The app does not collect or transmit any data about users. -->
  <key>NSPrivacyCollectedDataTypes</key>
  <array/>

  <key>NSPrivacyTracking</key>
  <false/>
</dict>
</plist>
```

**In `project.yml`:** Add the file to the target's `sources` — it will be picked up automatically if it is inside the `SportsScores/` source directory.

---

## 3. Apple Developer Portal — App Record

These steps are done at [developer.apple.com](https://developer.apple.com) and [appstoreconnect.apple.com](https://appstoreconnect.apple.com).

### 3a. Register the Bundle ID
- Go to **Certificates, Identifiers & Profiles → Identifiers**.
- Register `com.sportsscores.app` as an explicit App ID.
- Enable the **Push Notifications** capability (the app requests notification authorization at launch).
- No other capabilities are needed (no iCloud, no App Groups, no Sign in with Apple).

### 3b. Create the App on App Store Connect
- Go to **My Apps → +** and create a new iOS app.
- Bundle ID: `com.sportsscores.app`
- Name: decide what you want the public-facing name to be. **"SportsScores"** is almost certainly taken on the App Store — search first. Options: "Scores for ESPN," "Sports Scores Live," something more distinctive.
- Primary language, category (Sports), and SKU (can be anything unique, e.g. `sportsscores-001`).

You do not need to fill out the full App Store listing for TestFlight — just enough to create the record and upload a build.

---

## 4. What to Test Notes (TestFlight)

App Store Connect asks for "What to Test" notes with every TestFlight build. Write something testers can actually use. Suggested starting text:

```
This is an early build of a sports scores app for MLB, NFL, NBA, NHL,
NCAA Football, NCAA Basketball, and WNBA.

Please focus on:
• Scores tab — do games load? Does date navigation work?
• Standings tab — do all six sports load correctly?
• Game detail (tap any game) — box score, plays, info tab
• VoiceOver — the standings table should read row and column
  headers automatically; box score rows should each read as one item

Known issues / not yet implemented:
• [fill in before distributing]
```

---

## 5. Notification Permission — Cosmetic Issue

The app requests notification authorization immediately on first launch (`onAppear` in `SportsScoresApp.swift`). iOS will show the system permission prompt before the user has done anything in the app.

Apple's Human Interface Guidelines and App Review guidelines both say you should explain *why* before asking. This will not block TestFlight but will be flagged in App Review if you ever submit to the App Store.

**Recommended fix before wider distribution:** Move the authorization request to the moment a user first taps "Monitor this game" in `ScoreMonitorService.toggle(game:)` rather than on app launch.

---

## 6. App Version / Build Number

Currently set in `project.yml`:
```
CURRENT_PROJECT_VERSION: 1      # build number — increment for every upload
MARKETING_VERSION: 1.0          # version shown to users
```

**For TestFlight:** These are fine as-is for the first upload. You must increment `CURRENT_PROJECT_VERSION` (the build number) every time you upload a new build, even for TestFlight. The marketing version can stay at 1.0 through testing.

---

## 7. ESPN API — Policy Awareness

The app calls `site.api.espn.com` directly. This is an unofficial, undocumented API — it is the same endpoint used by ESPN's own apps and website, but it is not a documented public API with terms of service for third parties.

**For internal TestFlight (your own devices / invited team members):** No issue.

**For external TestFlight (public link / uninvited testers):** Builds go through a basic App Review before Apple allows you to distribute them externally. A reviewer browsing the app will not necessarily notice the API source, but if there is ever a rights complaint from ESPN, Apple could pull the app.

**Practical guidance:** Internal TestFlight is safe indefinitely. For external distribution or App Store submission, you should either obtain a license / attribution agreement with ESPN or note the risk and proceed. Many apps operate this way; it is a business risk, not a technical one.

---

## 8. Mac Catalyst — Consider Disabling for TestFlight

`project.yml` has `SUPPORTS_MACCATALYST: YES`. This means your archive will build for Mac as well, and App Store Connect will make it available on the Mac App Store via iPhone/iPad apps. This is convenient eventually but adds untested surface area for a first TestFlight. If the Mac version has not been tested at all, consider disabling it temporarily:

```yaml
SUPPORTS_MACCATALYST: NO
```

You can re-enable it once you are happy with the iOS version.

---

## 9. Build and Archive Checklist (day of submission)

1. **Increment build number** in `project.yml` (`CURRENT_PROJECT_VERSION`).
2. Regenerate the Xcode project if using XcodeGen: `xcodegen generate`.
3. In Xcode: select **Any iOS Device (arm64)** as the destination (not a simulator).
4. Product → **Archive**.
5. In the Organizer window, select the archive → **Distribute App** → **App Store Connect** → **Upload**.
6. On App Store Connect under your app → **TestFlight** → select the build once it finishes processing (usually 5–15 minutes).
7. Add testers: internal (anyone in your developer account) can be added immediately. External testers require the brief App Review first.

---

## Summary

| # | Item | Blocks archive? | Blocks TestFlight upload? |
|---|------|----------------|--------------------------|
| 1 | App icon (actual PNG) | Yes | Yes |
| 2 | PrivacyInfo.xcprivacy | No | Will warn; eventually hard-reject |
| 3 | Bundle ID + App Store Connect record | No | Yes — nowhere to upload to |
| 4 | What to Test notes | No | No (can add after upload) |
| 5 | Notification permission timing | No | No |
| 6 | Build number increment | No | Only matters on 2nd+ upload |
| 7 | ESPN API awareness | No | No (internal TestFlight) |
| 8 | Disable Mac Catalyst (optional) | No | No |

**Minimum required to get a build into TestFlight:**
1 → 2 → 3, then archive and upload.
