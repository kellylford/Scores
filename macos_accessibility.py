"""
macOS-specific accessibility enhancements for Sports Scores Application
Provides VoiceOver support and improved keyboard navigation on macOS
"""

import platform
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtGui import QFocusEvent

class MacOSAccessibilityManager:
    """Manages macOS-specific accessibility features"""
    
    def __init__(self, app: QApplication):
        self.app = app
        self.is_macos = platform.system() == "Darwin"
        if self.is_macos:
            self._setup_macos_accessibility()
    
    def _setup_macos_accessibility(self):
        """Configure macOS-specific accessibility features"""
        # Install global event filter for accessibility
        self.app.installEventFilter(MacOSAccessibilityEventFilter())
        
        # Set application properties for VoiceOver
        self.app.setProperty("QT_MAC_WANTS_LAYER", 1)
        
        # Enable focus follows mouse for better VoiceOver integration
        self.app.setAttribute(Qt.ApplicationAttribute.AA_MacDontSwapCtrlAndMeta, False)
    
    def enhance_widget_accessibility(self, widget: QWidget, role: str = None, 
                                   description: str = None):
        """Enhance a widget's accessibility for macOS"""
        if not self.is_macos:
            return
        
        # Set focus policy to ensure widget can receive focus
        if widget.focusPolicy() == Qt.FocusPolicy.NoFocus:
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Set accessibility role if provided
        if role:
            widget.setAccessibleName(role)
        
        # Set description if provided
        if description:
            widget.setAccessibleDescription(description)
        
        # Ensure widget is focusable by VoiceOver
        widget.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)


class MacOSAccessibilityEventFilter(QObject):
    """Event filter to enhance macOS accessibility"""
    
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Filter events to enhance accessibility"""
        if not isinstance(watched, QWidget):
            return False
        
        # Handle focus events to ensure VoiceOver tracking
        if event.type() == QEvent.Type.FocusIn:
            self._handle_focus_in(watched, event)
        elif event.type() == QEvent.Type.KeyPress:
            return self._handle_key_press(watched, event)
        
        return False
    
    def _handle_focus_in(self, widget: QWidget, event: QFocusEvent):
        """Handle focus in events for VoiceOver"""
        # Ensure the widget is properly announced by VoiceOver
        if hasattr(widget, 'accessibleName') and widget.accessibleName():
            # Force VoiceOver to re-read the element
            widget.update()
        
        # For tables, announce current position
        if hasattr(widget, 'currentRow') and hasattr(widget, 'currentColumn'):
            try:
                row = widget.currentRow()
                col = widget.currentColumn()
                if row >= 0 and col >= 0:
                    # Get cell content for announcement
                    item = widget.item(row, col)
                    if item:
                        content = item.text()
                        # Update accessible description with current position
                        widget.setAccessibleDescription(
                            f"Table cell row {row + 1}, column {col + 1}: {content}"
                        )
            except:
                pass
    
    def _handle_key_press(self, widget: QWidget, event) -> bool:
        """Handle key press events for improved navigation"""
        key = event.key()
        
        # Handle VoiceOver navigation keys
        if key == Qt.Key.Key_F5:  # VoiceOver element navigation
            return False  # Let VoiceOver handle it
        
        # Improve table navigation
        if hasattr(widget, 'currentRow') and hasattr(widget, 'currentColumn'):
            if key in [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right]:
                # Let the table handle arrow keys, but ensure accessibility update
                result = False  # Don't consume the event
                # Schedule accessibility update after the navigation
                QApplication.processEvents()
                self._handle_focus_in(widget, QFocusEvent(QEvent.Type.FocusIn))
                return result
        
        return False


def setup_macos_widget_accessibility(widget: QWidget, manager: MacOSAccessibilityManager = None):
    """Setup macOS accessibility for a specific widget"""
    if platform.system() != "Darwin":
        return
    
    # Ensure the widget can be focused
    if widget.focusPolicy() == Qt.FocusPolicy.NoFocus:
        widget.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    
    # Set proper widget attributes for VoiceOver
    widget.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
    widget.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
    
    # For list widgets and tables, ensure proper keyboard navigation
    if hasattr(widget, 'setTabKeyNavigation'):
        widget.setTabKeyNavigation(True)
    
    # Apply accessibility manager enhancements if provided
    if manager:
        manager.enhance_widget_accessibility(widget)


def announce_to_voiceover(text: str, widget: QWidget = None):
    """Announce text to VoiceOver (macOS only)"""
    if platform.system() != "Darwin":
        return
    
    try:
        # Try to use the native announcement system
        import subprocess
        subprocess.run(['say', text], check=False, capture_output=True)
    except:
        # Fallback: update widget accessibility description
        if widget:
            current_desc = widget.accessibleDescription()
            widget.setAccessibleDescription(f"{current_desc}. {text}")
            widget.update()
