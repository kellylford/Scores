# Screen Reader Text Truncation Issue & Fix

## Issue Description

Screen readers were reading truncated text with ellipses ("...") from QListWidget items in the live scores view and other list-based views.

### Example of Problem
Visual display and screen reader both announced:
```
Jacksonville Jaguars 15 at Tennessee Titans 3 | (Shotgun) T.Pollard right guard to TEN 31 for 3 yards (D.Str...
```

Instead of the full text:
```
Jacksonville Jaguars 15 at Tennessee Titans 3 | (Shotgun) T.Pollard right guard to TEN 31 for 3 yards (D.Strong).
10:56 Q2 | 1st & 10 | TEN: 1 play (10:56 - 2nd)
```

## Root Cause

Qt's QListWidget truncates long text with ellipses ("...") when the text exceeds the widget's visible width. By default, screen readers read from the `DisplayRole` which contains the same truncated text that's visually displayed.

## Solution Implemented

Added full untruncated text to each QListWidgetItem using:
- `setToolTip(full_text)` - Screen readers can access tooltip text
- `setWhatsThis(full_text)` - Additional accessibility property some screen readers use

### Code Pattern Applied

```python
item = QListWidgetItem(display_text)
item.setData(Qt.ItemDataRole.UserRole, game_data)
# Set full text for screen readers via tooltip and WhatsThis to prevent ellipsis truncation
item.setToolTip(display_text)
item.setWhatsThis(display_text)
list_widget.addItem(item)
```

### What Didn't Work

1. **Custom QStyledItemDelegate with ElideNone** - While this approach is correct for QTableWidget, QListWidget doesn't fully respect the delegate's size hints for horizontal width
2. **setWordWrap(True)** - Word wrapping doesn't prevent ellipsis truncation; Qt still truncates at the widget boundary
3. **Horizontal scrollbar alone** - Requires Qt to know the true width of items, which it doesn't calculate by default
4. **AccessibleTextRole/AccessibleDescriptionRole** - Caused double-reading: screen readers announced both DisplayRole and AccessibleTextRole

## Files Modified

- `scores.py`:
  - `LiveScoresView.load_live_scores()` - All game items (live, upcoming, completed)
  - `LeagueView.load_scores()` - All score items (weekly and daily)

## Result

- Visual display: May still show truncated text with "..." when window is narrow
- Screen readers: Can access full untruncated text via tooltip/WhatsThis properties
- No double-reading issues
- No performance impact

## Future Considerations

If visual truncation needs to be fixed (not just screen reader accessibility):
1. Consider using QListView with custom delegate and proper size hint width calculation
2. Or use multi-line text with word wrapping in fixed-width cells
3. Or redesign UI to use expandable items or detail panes

For now, the tooltip/WhatsThis approach is the standard accessibility pattern and meets WCAG requirements without impacting visual design.

## Related Code Locations

- Custom delegate attempts: Removed from final implementation
- Import cleanup: Removed unused QStyledItemDelegate, QStyle, QSize, QFontMetrics
- Similar patterns could be applied to other list widgets if needed (details_list, news_list, etc.)
