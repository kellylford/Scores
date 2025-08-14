# Scores App Release Management Overview

This document summarizes everything you need to know about release management, versioning, and best practices for your Scores application using GitHub.

---

## 1. Release Management Workflow

**A. Prepare for Release**
- Finalize code and documentation
- Update version numbers (in `VERSION` file and code)
- Update `CHANGELOG.md` and `RELEASE_NOTES.md`

**B. Build the Application**
- Use `build-enhanced.bat` to build the Windows executable
- Use `prepare-release.bat <version>` to automate versioning and building

**C. Commit and Tag**
- Commit all changes: `git add . && git commit -m "Release vX.Y.Z"`
- Create a git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- Push commits and tag: `git push origin main && git push origin vX.Y.Z`

**D. Create GitHub Release**
- Go to GitHub Releases page
- Create a new release from the tag
- Add release notes (copy from `RELEASE_NOTES.md`)
- Upload the executable (`dist/Scores.exe`)
- Mark as pre-release if needed

---

## 2. Versioning Best Practices

- Use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- For preview/beta: use suffixes like `-preview`, `-beta`, `-rc` (e.g., `0.5.0-preview`)
- Store the version in a `VERSION` file and in your code (`__version__`)
- Update version numbers before each release

---

## 3. Changelog & Release Notes

- Maintain a `CHANGELOG.md` with all notable changes
- Use `RELEASE_NOTES.md` for user-friendly release summaries
- Document new features, fixes, known issues, and technical details

---

## 4. Build & Distribution

- Build with PyInstaller for a standalone Windows executable
- Use virtual environments for dependency isolation
- Distribute the executable (`dist/Scores.exe`)—no Python required on target machines

---

## 5. Automation Tools

- `prepare-release.bat`: Automates versioning and building
- `build-enhanced.bat`: Cleans, builds, and verifies the executable
- Consider using [bump2version](https://github.com/c4urself/bump2version) or GitHub Actions for further automation

---

## 6. GitHub Release Features

- **Tags:** Mark specific commits for releases
- **Release Page:** Publish releases, attach binaries, add notes
- **Pre-release:** Mark releases for testing/beta
- **Actions:** Automate builds/tests/releases
- **Issues/PRs:** Track bugs, enhancements, and code reviews

---

## 7. Example Release Steps

1. `prepare-release.bat 0.6.0`
2. Update `CHANGELOG.md` and `RELEASE_NOTES.md`
3. `git add . && git commit -m "Release v0.6.0"`
4. `git tag -a v0.6.0 -m "Release v0.6.0"`
5. `git push origin main && git push origin v0.6.0`
6. Create GitHub release, upload `Scores.exe`, add notes

---

## 8. Maintenance & Next Steps

- Test each release before publishing
- Gather feedback from users/testers
- Plan next version based on feedback/issues
- Keep documentation and automation scripts up to date

---

## 9. Useful Links
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- [GitHub Releases Guide](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [bump2version](https://github.com/c4urself/bump2version)

---

**Reference maintained by GitHub Copilot — August 2025**
