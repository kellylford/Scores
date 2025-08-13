# **Schedule Loading Performance & Focus Improvements**

**Date**: August 12, 2025  
**Status**: 🔄 **IN PROGRESS** - Implementation interrupted by file corruption  

---

## **🎯 Issues Identified**

### **Performance Problems**
1. **Slow schedule loading** - Each team's schedule requires a fresh API call (1-3 seconds)
2. **Repeated API calls** - No caching for team schedules
3. **Blocking UI** - Synchronous loading freezes the interface

### **Focus/UX Problems**
1. **Poor focus management** - Focus defaults to "Back" button instead of schedule list
2. **No today highlighting** - User can't quickly find today's games
3. **Manual navigation** - User must scroll to find current/upcoming games

---

## **🚀 Planned Solutions**

### **1. Background Threading for Schedules**
```python
class ScheduleLoader(QThread):
    """Background thread for loading team schedule data"""
    schedule_loaded = pyqtSignal(str, object)  # team_id, schedule_data
    loading_failed = pyqtSignal(str, str)      # team_id, error_message
```

**Benefits:**
- **Non-blocking UI** during schedule loading
- **Parallel loading** while user browses other teams
- **Immediate cache population** for instant subsequent access

### **2. Schedule Caching System**
```python
self.cached_schedules = {}  # {team_id: schedule_data}
```

**Features:**
- **Per-team caching** - Each team's schedule cached independently
- **Smart loading** - Check cache before API calls
- **Memory efficient** - Only cache accessed schedules

### **3. Smart Focus on Today's Date**
```python
def set_schedule_focus_to_today(self, schedule_list):
    """Focus on today's game or next upcoming game"""
```

**Logic:**
1. **Today's game** - Focus and highlight if exists
2. **Next upcoming game** - Focus on closest future game
3. **Visual highlighting** - Bold text + light yellow background for today
4. **Auto-scroll** - Ensure focused item is visible

---

## **📈 Expected Performance Gains**

### **Schedule Loading Speed**
- **First access**: 1-3 seconds (API call + cache)
- **Subsequent access**: < 100ms (cached data)
- **Background loading**: User can browse while data loads

### **User Experience**
- **Immediate focus** on relevant games (today/upcoming)
- **Visual highlighting** of today's games
- **No UI freezing** during data loading
- **Intuitive navigation** to current games

---

## **🔧 Implementation Details**

### **Background Loading Workflow**
1. **Dialog opens** → Start background standings loading
2. **Team selected** → Start background schedule loading for that team
3. **Schedule view** → Use cached data if available, show loading if not
4. **Background complete** → Update UI with loaded data

### **Caching Strategy**
- **Scope**: Per-dialog instance (clears when dialog closes)
- **Storage**: In-memory dictionary `{team_id: schedule_data}`
- **Freshness**: Appropriate for single browsing session
- **Memory**: Minimal impact (schedules ~5-10KB each)

### **Focus Management**
```python
# Priority order for schedule focus:
1. Today's exact game → Focus + highlight
2. Next upcoming game → Focus + scroll to
3. First item → Default fallback
```

---

## **🎨 Visual Enhancements**

### **Today's Game Highlighting**
- **Bold text** for today's games
- **Light yellow background** (#FFFFE8) for visibility
- **Auto-scroll** to ensure visibility

### **Loading Indicators**
- **"Loading schedule..."** for initial load
- **"Loading schedule... (background loading)"** when background thread active
- **Immediate UI response** with loading feedback

---

## **🧪 Testing Plan**

### **Performance Testing**
1. **First team access** - Measure initial load time
2. **Second team access** - Verify background caching works
3. **Return to first team** - Confirm instant access from cache
4. **Multiple rapid selections** - Test background loading queue

### **Focus Testing**
1. **Team with today's game** - Verify focus and highlighting
2. **Team with no today game** - Verify focus on next upcoming
3. **Team with past games only** - Verify focus on first item
4. **Navigation flow** - Teams → Schedule → Focus works properly

---

## **⚠️ Implementation Status**

### **Completed Elements**
✅ **Background threading classes** (`ScheduleLoader`)  
✅ **Caching architecture** (`cached_schedules` dictionary)  
✅ **Background loading methods** (`start_schedule_background_loading`)  
✅ **Schedule population logic** (`populate_schedule_list`)  
✅ **Smart focus logic** (`set_schedule_focus_to_today`)  

### **In Progress**
🔄 **File restoration** - syntax errors from manual edits  
🔄 **Integration testing** - ensure all components work together  
🔄 **Focus timing** - proper QTimer delays for UI updates  

### **Pending**
❌ **Complete testing** - verify performance improvements  
❌ **Documentation** - update comments and docstrings  
❌ **Edge case handling** - error states and fallbacks  

---

## **🔥 Current Issue: File Corruption**

**Problem**: The `scores.py` file contains "Made changes." markers causing syntax errors.

**Recovery Options**:
1. **Restore from backup** if available
2. **Clean manual edit** to remove corruption markers
3. **Selective restoration** of working sections

**Next Steps**:
1. Fix file syntax errors
2. Verify all imports are correct
3. Test background loading functionality
4. Validate focus improvements

---

## **💡 Additional Optimization Ideas**

### **Preemptive Loading**
- **Load popular teams** in background when dialog opens
- **Smart predictions** based on division browsing patterns

### **Persistent Caching**
- **File-based cache** with timestamp validation
- **Cross-session persistence** for frequently accessed teams

### **Progressive Enhancement**
- **Skeleton UI** while loading
- **Progressive disclosure** of game details as they load

---

**Current Priority**: 🚨 **Fix file corruption and restore functionality**  
**Next Priority**: ✅ **Complete performance testing and validation**  
**Target Outcome**: 90%+ faster schedule access + smart focus on today's games
