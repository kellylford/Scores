# Scores v0.65.0 Release Notes

## 🎯 Accessibility Enhancement Release

This release focuses on improving clarity and accessibility by spelling out sport names and gender designations throughout the application interface.

### ✨ What's New

#### Enhanced League Name Display
**Better Clarity for All Users** - League abbreviations now display with full, descriptive names:

- **NCAA Women's Hockey** (formerly NCAAWH)
- **NCAA Women's Basketball** (formerly NCAAWB)
- **NCAA Men's Hockey** (formerly NCAAH)
- **NCAA Men's Basketball** (formerly NCAAM)
- **NCAA Football** (formerly NCAAF)

This enhancement affects:
- **Main League Selection Screen**: Clear sport names when choosing which sport to view
- **Live Scores Section Headers**: Organized game listings with descriptive headers
- **Window Titles**: Full sport names in title bar for better context awareness
- **In-App Labels**: All sport references now use complete, unambiguous names

### 🔍 Why This Matters

#### Accessibility Benefits
- **Screen Reader Friendly**: Full names are immediately understandable without needing to know abbreviations
- **New User Experience**: No learning curve for understanding sport abbreviations
- **Gender Clarity**: Explicit designation of men's and women's sports removes ambiguity
- **Context Awareness**: Window titles and headers now provide complete information at a glance

#### Real-World Impact
Before this release, users saw:
```
--- NCAAWH ---
Michigan vs Wisconsin
```

Now they see:
```
--- NCAA Women's Hockey ---
Michigan vs Wisconsin
```

This makes the interface:
- More welcoming to new users
- Easier to navigate with assistive technologies
- Clearer when multitasking or quickly checking scores
- More professional and polished

### 🎨 Technical Details

All changes maintain backward compatibility:
- Internal API calls still use efficient abbreviation codes
- No performance impact from longer display names
- Consistent formatting across all interface elements
- Comprehensive coverage of main screen, dialogs, and window titles

### 🚀 Getting Started

**For New Users:**
1. Download and launch Scores v0.65.0
2. Notice the clear, descriptive sport names on the main selection screen
3. Choose your sport and enjoy organized, well-labeled game listings

**For Existing Users:**
No action needed - you'll immediately see the clearer sport names throughout the application.

### 📋 Full Change List

#### Changed
- Main league selection list now displays full sport names with gender designation
- Live scores section headers use complete league names
- Window titles show full sport names in breadcrumb navigation
- Score view headers display formatted league names
- Game detail dialogs include full sport names in titles

### 🎯 What's Next

We continue to focus on accessibility and user experience improvements. Future releases will bring more enhancements to make Scores the most accessible sports application available.

---

**Version**: 0.65.0  
**Release Date**: December 14, 2025  
**Build**: Stable Release
