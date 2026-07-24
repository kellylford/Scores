# iOS TestFlight / App Store Release via GitHub Actions

The [`ios-release.yml`](ios-release.yml) workflow builds and uploads a Sports Scores
build to App Store Connect (TestFlight) from a GitHub-hosted macOS runner.

**Why this exists:** archiving on a Mac that's on a **beta macOS** (or a beta
Xcode/SDK) stamps the binary as "compiled with a beta product," and Apple rejects
those for the public App Store. GitHub's runners are always on released macOS +
released Xcode, so builds from here pass review. The workflow also aborts if the
runner ever comes up on a beta macOS seed, so a bad binary can never ship.

The app talks only to public ESPN / MLB APIs, so **no app-side API-key secrets are
required** — just the Apple signing/upload credentials below.

## One-time setup: repo secrets

Add these under **Settings → Secrets and variables → Actions → New repository secret**
on the **Scores** repo. (Secrets are per-repository, so even though these are the
same Apple credentials used by FastWeather, they must be added here too.)

| Secret | What it is | How to get it |
|--------|-----------|---------------|
| `ASC_KEY_ID` | App Store Connect API key ID | e.g. `38ANZ53D9L` — the key you already use for TestFlight uploads |
| `ASC_ISSUER_ID` | ASC API issuer ID | The issuer UUID from App Store Connect → Users and Access → Integrations → App Store Connect API |
| `ASC_KEY_P8_BASE64` | The `.p8` API key, base64-encoded | `base64 -i ~/Downloads/AuthKey_38ANZ53D9L.p8 \| pbcopy` |
| `DIST_CERT_P12_BASE64` | "Apple Distribution" cert **+ its private key**, base64-encoded | Export a `.p12` (below), then `base64 -i dist.p12 \| pbcopy` |
| `DIST_CERT_PASSWORD` | The password you set on that `.p12` | Whatever you typed during export |

### Exporting the distribution `.p12`

Easiest via **Keychain Access** (the private key can't be reliably exported from the CLI):

1. Open **Keychain Access** → **login** keychain → **My Certificates**.
2. Find **"Apple Distribution: Kelly Ford (P887QF74N8)"**. Expand it — it must have a
   private key underneath (the disclosure triangle). If it doesn't, that Mac can't
   export a usable cert; create a new distribution cert in Xcode first.
3. Right-click it → **Export "Apple Distribution…"** → **Personal Information Exchange (.p12)**.
4. Save as `dist.p12`, set a password → that password is `DIST_CERT_PASSWORD`.
5. `base64 -i dist.p12 | pbcopy` → paste as `DIST_CERT_P12_BASE64`.

Then delete `dist.p12` when you're done.

## Important: the workflow must live on the default branch to be runnable

GitHub only shows the **Run workflow** button for a `workflow_dispatch` workflow when
the file exists on the repo's **default branch** (`main`). The iOS app, however, lives
on the **`iOS`** branch. So both must be true for a run:

- the workflow file is present on **`main`** (so the button appears), **and**
- you dispatch it against the **`iOS`** branch (so it checks out and builds the iOS code).

This file is committed on `iOS`. To make it appear in the Actions UI, also land it on
`main` — either merge/cherry-pick just the `.github/workflows/` files onto `main`, or
merge `iOS` → `main` when you're ready. Until then you can still trigger it from the
CLI against the iOS branch:

```bash
gh workflow run ios-release.yml --ref iOS -f build_number=31
```

## Running it

1. **Actions** tab → **iOS TestFlight / App Store Release** → **Run workflow**.
2. Set the branch to **`iOS`**.
3. **Build number**: the next unused build for the current marketing version. The
   project is at version **0.8**, build **30**, so use **31** or higher.
4. **Marketing version**: leave blank to keep `0.8`.
5. Run. On success the build appears in App Store Connect / TestFlight (Processing for
   ~5–15 min), after which you can add it to a TestFlight group or submit it for App
   Store review. The `.ipa` is also saved as a run artifact.

## Notes

- **Signing is automatic:** the ASC API key lets `xcodebuild` create/download the App
  Store provisioning profile; the imported `.p12` provides the distribution identity.
- **This uploads to App Store Connect but does not auto-submit for review.** The build
  lands in TestFlight/Processing; releasing to testers or the App Store is a separate,
  manual step in App Store Connect.
- The workflow sets the build/marketing number for that run only — it does **not**
  commit the change back. Bump `CURRENT_PROJECT_VERSION` / `MARKETING_VERSION` in
  `iOS/SportsScoresApp/project.yml` (and regenerate) when you want the repo default to move.
- **App:** "Sports Scores Fast", bundle id `com.sportsscores.app`, team `P887QF74N8`.
- **Cost:** free for public repos; a private repo bills macOS runner minutes at 10×
  (a build is a few minutes, so cents per run).
