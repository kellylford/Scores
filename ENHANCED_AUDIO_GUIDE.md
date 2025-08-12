# Enhanced Spatial Audio Features - User Guide

## Overview
The spatial audio pitch mapping system has been enhanced with several new features for better accessibility and usability.

## New Features

### 1. Context Menu Improvements
- **Context menu now works on both pitches AND player names/at-bats**
- **Right-click or Shift+F10** on any item in the game details tree
- Menu options are now context-aware:
  - **Play Pitch Audio**: Only available for actual pitches
  - **Play Pitch Sequence**: Available for pitches and at-bat items
  - **Explore Strike Zone**: Always available

### 2. Strike Zone Exploration
- **New submenu: "Explore Strike Zone"**
- **9 positions available**: High/Center/Low × Left/Center/Right
- Each position plays audio as if a pitch were thrown to that exact location
- Helps users learn the audio mapping for different strike zone areas
- Uses current batter context when available

### 3. Enhanced Stereo Audio
- **Left/right positioning now includes audio balance cues**
- Pitches to the left side have slightly lower frequency
- Pitches to the right side have slightly higher frequency  
- Center pitches use normal frequency
- Audio feedback includes position descriptions like "(left)", "(center)", "(right)"

### 4. Faster Pitch Sequences
- **Reduced delay between pitches in sequences**
- Changed from 1.2 seconds to 0.8 seconds between pitches
- Provides quicker playback for full at-bat sequences

## Usage Guide

### Context Menu Access
1. Navigate to any game with pitch-by-pitch details
2. **Right-click** on any item (pitch or batter name)
3. **OR press Shift+F10** on a selected item
4. Choose from available options based on context

### Keyboard Shortcuts
- **Alt+P**: Play current pitch audio (only works on pitches)
- **Alt+S**: Play pitch sequence (works on pitches and at-bat items)
- **Shift+F10**: Show context menu

### Strike Zone Exploration
1. Open context menu on any item
2. Select "Explore Strike Zone" submenu
3. Choose any of the 9 positions:
   - High Left, High Center, High Right
   - Center Left, Center Center, Center Right  
   - Low Left, Low Center, Low Right
4. Press Enter or click to hear that zone's audio

### Audio Mapping
- **Pitch Height**: Higher pitches = higher frequency beeps
- **Pitch Speed**: Faster pitches = longer duration beeps
- **Pitch Location**: Left/right position affects frequency slightly
- **Audio Balance**: Future enhancement for true stereo panning

## Technical Details

### Strike Zone Coordinates
The 9 exploration zones use these coordinates for optimal stereo separation:
- **High**: Y = 50 (top of zone)
- **Center**: Y = 127 (middle of zone)
- **Low**: Y = 200 (bottom of zone)
- **Left**: X = 50 (far left for clear left audio)
- **Center**: X = 127 (middle)
- **Right**: X = 205 (far right for clear right audio)

### Audio Parameters
- **Frequency Range**: 200Hz - 2000Hz
- **Duration Range**: 200ms - 500ms (based on velocity)
- **Sequence Timing**: 800ms between pitches
- **Balance Effect**: ±50Hz frequency adjustment for positioning

## Accessibility Features
- All menu items have proper accessibility names
- Status tips provide clear descriptions
- Audio feedback confirms actions
- Multiple access methods (mouse, keyboard, button)
- Works with screen readers

## Future Enhancements
- True stereo panning when audio system supports it
- Different sound profiles for different pitch types
- Customizable timing and frequency ranges
- Volume control based on strike zone accuracy
