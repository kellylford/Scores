# Accessible Table Explorer - Usage Guide

## Overview
The Accessible Table Explorer is a comprehensive test application designed to evaluate different PyQt6 table approaches for screen reader accessibility. This tool addresses the specific need to find optimal table navigation behavior for sports score applications.

## Problem Statement
The main issue being addressed:
- When navigating down a column in tables, screen readers should announce the row header (e.g., player name) + column header + cell value
- Current behavior only announces row numbers, which is not ideal
- Need to test different Qt6 table controls and accessibility settings

## Application Features

### Table Types Tested
1. **Standard QTableWidget** - Basic Qt table with enhanced accessibility
2. **Custom AccessibleTable** - Our enhanced table implementation
3. **HTML in QWebEngineView** - Full HTML table with semantic markup
4. **HTML in QTextBrowser** - Simplified HTML table for screen reader compatibility

### Control Panel Features
- **Navigation Mode**: Choose how cell navigation is announced
  - Row + Column + Value
  - Column + Value only
  - Row + Value only  
  - Value only
  - Full context (Row header + Column header + Value)

- **Row Numbers**: Toggle inclusion of row numbers in announcements
- **Tooltips**: Enable/disable tooltips for screen reader text
- **Accessible Roles**: Set explicit accessible roles for better screen reader support
- **Tab Behavior**: Configure how Tab key works within tables

### Testing Features
- Real-time accessibility setting adjustments
- Navigation testing with sample sports data
- Results logging for documentation
- Focus management testing

## Usage Instructions

### Running the Application
```bash
cd TheBench
python accessible_table_explorer.py
```

### Testing Procedure
1. **Select a table type** using the tabs at the top
2. **Adjust accessibility settings** using the control panel
3. **Test navigation**:
   - Use arrow keys to move between cells
   - Use Tab to enter/exit tables
   - Use "Test Navigation" button for automated testing
4. **Monitor results** in the results panel
5. **Document findings** for each configuration

### Sample Data
The application uses baseball player statistics as test data:
- Player names (serve as row headers)
- Position, At Bats, Hits, RBI, Batting Average
- Mimics real sports score table structure

## Key Testing Scenarios

### Scenario 1: Column Navigation
**Goal**: When moving down the "Hits" column, should announce:
- "TJ Friedl, Hits, 1" (not just "Row 1, 1")
- "Jonathan India, Hits, 2" (not just "Row 2, 2")

**Test**: Use down arrow in the Hits column and verify announcements

### Scenario 2: Row Navigation  
**Goal**: When moving across a row, should announce:
- "TJ Friedl, Position, CF"
- "TJ Friedl, At Bats, 4"
- "TJ Friedl, Hits, 1"

**Test**: Use right arrow across TJ Friedl's row

### Scenario 3: Tab Navigation
**Goal**: Tab should move user into/out of table, not between cells
**Test**: Use Tab key to enter table, arrow keys to navigate, Tab to exit

## Expected Findings

Based on preliminary research, we expect:

1. **QWebEngineView**: Beautiful but limited screen reader integration
2. **QTableWidget**: Good with proper accessibility setup, but may need custom row header handling
3. **Custom AccessibleTable**: Best control over accessibility behavior
4. **QTextBrowser**: Limited table navigation but good screen reader compatibility

## Documentation Process

For each table type and configuration:
1. Note navigation behavior
2. Record screen reader announcements
3. Test keyboard navigation patterns
4. Document pros/cons
5. Rate overall accessibility (1-10)

## Integration Recommendations

Results from this testing will inform:
- Which table control to use in the main sports app
- How to configure accessibility settings
- Custom navigation behavior implementation
- Screen reader optimization strategies

## Files Generated

- `accessible_table_explorer.py` - Main test application
- `ACCESSIBILITY_TEST_FINDINGS.md` - Results documentation
- Screenshots of each table type in action
- Detailed navigation behavior analysis

This systematic testing approach ensures we find the optimal accessible table solution for the sports scores application.