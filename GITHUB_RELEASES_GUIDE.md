# GitHub Releases Guide - Sports Scores Application

## 🎯 **Release Created: v1.0.0**

I've created a Git tag `v1.0.0` and pushed it to GitHub. Now you can create the official release!

## 📋 **How to Create the Release on GitHub**

### **Step 1: Go to GitHub Releases**
1. Go to: https://github.com/kellylford/Scores
2. Click **"Releases"** (on the right side of the repository page)
3. Click **"Create a new release"**

### **Step 2: Select Your Tag**
- **Tag version:** Select `v1.0.0` (should appear in dropdown)
- **Release title:** `Sports Scores v1.0.0 - Initial Release`

### **Step 3: Write Release Notes**
```markdown
# Sports Scores v1.0.0 - Initial Release

A desktop application for browsing live sports scores with professional accessibility features.

## ✨ **Key Features**
- **Live Sports Data** - MLB, NFL, NBA, NHL and more via ESPN API
- **Export Game Logs** - Professional HTML format for baseball and football
- **Full Accessibility** - Complete keyboard navigation and screen reader support
- **Detailed Game Views** - Play-by-play (baseball) and drive-by-drive (football)
- **News Integration** - Direct links to ESPN articles
- **No Installation** - Standalone Windows executable

## 🎮 **Quick Start**
1. Download `SportsScores.exe` below
2. Run the executable (no installation needed)
3. Navigate with keyboard: Arrow keys, Enter to select, Alt+B to go back
4. Try exporting a game log from baseball plays or football drives!

## 📚 **Documentation**
- See [User Guide](https://github.com/kellylford/Scores/blob/main/USER_GUIDE.md) for complete instructions
- Check [Quick Reference](https://github.com/kellylford/Scores/blob/main/QUICK_REFERENCE.md) for keyboard shortcuts

## 🔧 **System Requirements**
- Windows 10/11 (64-bit)
- Internet connection for live data
- No Python installation required

## 🐛 **Known Issues**
- Table navigation could be improved (virtual cursor mode)
- Export currently limited to MLB and NFL games
- Some API data may be incomplete depending on ESPN availability

---
**File Size:** ~38MB (includes all GUI libraries and dependencies)
```

### **Step 4: Upload Your Executable**
- **Drag and drop** your `C:/Users/kelly/GitHub/Scores/dist/SportsScores.exe` file
- Or click **"Attach binaries"** and select the file
- GitHub will show upload progress

### **Step 5: Additional Files (Optional)**
You could also attach:
- `USER_GUIDE.md` (as a PDF or just reference the GitHub link)
- `QUICK_REFERENCE.md` 
- Any example HTML export files

### **Step 6: Publish**
- Check **"Set as the latest release"**
- Click **"Publish release"**

## 🎉 **What Happens After Publishing**

### **Users Will See:**
- Professional download page at: `https://github.com/kellylford/Scores/releases`
- Clear download button for `SportsScores.exe`
- Release notes explaining features
- Version history as you add more releases

### **Benefits:**
- **Professional appearance** - looks like commercial software
- **Download statistics** - see how many people download
- **Version management** - easy to release updates
- **Clean repository** - executable not cluttering your code

### **For Future Releases:**
1. Make code changes and commit
2. Create new tag: `git tag -a v1.1.0 -m "Version 1.1.0 - Bug fixes"`
3. Push tag: `git push origin v1.1.0`
4. Create new release on GitHub with updated executable

## 🔗 **Direct Links After Publishing**
- **Releases page:** https://github.com/kellylford/Scores/releases
- **Direct download:** https://github.com/kellylford/Scores/releases/download/v1.0.0/SportsScores.exe
- **Latest release:** https://github.com/kellylford/Scores/releases/latest

---

**Your tag `v1.0.0` is ready! Go to GitHub to complete the release creation.**
