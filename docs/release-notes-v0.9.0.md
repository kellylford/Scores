## What's New in Version 0.9.0

This release is about how Scores is delivered rather than what it does. There is now a real installer, the app keeps itself up to date, and every download is code-signed.

### Installer

`Scores-0.9.0-Setup.exe` is the recommended download. It installs for your user account only, so it never asks for administrator rights, and it adds a Start Menu shortcut (a desktop shortcut is offered as an option).

The portable `Scores.exe` is still published for anyone who prefers it.

### Automatic Updates

Scores now checks for a newer release when it starts and offers to download and install it for you. There is also a **Check for Updates** entry at the bottom of the home page if you would rather check yourself.

The startup check is silent unless an update is waiting, so it never interrupts launch — and it can be turned off entirely in Settings under *Automatically check for updates at startup*.

### Code Signing

The installer and the portable executable are both Authenticode-signed. Windows SmartScreen no longer warns that the publisher is unknown when you download or run Scores.

### Upgrading from 0.8.0

Run `Scores-0.9.0-Setup.exe`. If you have been using the portable `Scores.exe`, the installer will move you to the installed copy in `%LocalAppData%\Programs\Scores` — you can delete the old file afterward. Close Scores before installing; if you forget, Setup will ask you to.

Once you are on 0.9.0, future updates can be installed from inside the app.

---

**Platform:** Windows  
**Requires:** Windows 10 or later
