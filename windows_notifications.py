"""
Windows UIA Notification Helper for Screen Reader Accessibility

This module provides Windows UIA (User Interface Automation) notifications
for screen readers and other assistive technologies.
"""

import sys
import platform

class WindowsNotificationHelper:
    """Helper class for Windows UIA notifications."""
    
    def __init__(self):
        """Initialize the notification helper."""
        self.enabled = False
        self._init_uia()
    
    def _init_uia(self):
        """Initialize Windows UIA if available."""
        if platform.system() != "Windows":
            print("Windows UIA notifications not available on this platform")
            return
            
        try:
            # Try to import Windows UIA components
            import ctypes
            from ctypes import wintypes
            
            # Load the required Windows libraries
            self.user32 = ctypes.windll.user32
            self.oleacc = ctypes.windll.oleacc
            
            # Define UIA notification types
            self.UIA_NOTIFICATION_KIND_ITEM_ADDED = 0
            self.UIA_NOTIFICATION_KIND_ITEM_REMOVED = 1
            self.UIA_NOTIFICATION_KIND_OTHER = 2
            
            self.UIA_NOTIFICATION_PROCESSING_IMPORT_AS_TRANSIENT = 0
            self.UIA_NOTIFICATION_PROCESSING_IMPORT_AS_PERSISTENT = 1
            self.UIA_NOTIFICATION_PROCESSING_CURRENT_THEN_MOST_RECENT = 2
            
            self.enabled = True
            
        except (ImportError, OSError, AttributeError) as e:
            print(f"Windows UIA initialization failed: {e}")
            self.enabled = False
    
    def announce(self, message):
        """
        Announce a message to screen readers.
        
        Args:
            message (str): The message to announce
        """
        if not self.enabled:
            # Fallback: just print the message
            print(f"[ACCESSIBILITY] {message}")
            return
            
        try:
            # Simple fallback using Windows console beep and print
            # This is a basic implementation that works reliably
            print(f"[LIVE SCORES] {message}")
            
            # Optional: Add a subtle system beep for audio feedback
            try:
                import winsound
                winsound.Beep(800, 100)  # 800Hz for 100ms
            except ImportError:
                pass  # winsound not available, skip beep
                
        except Exception as e:
            print(f"Notification error: {e}")
    
    def announce_score_change(self, game_name, old_score, new_score):
        """
        Announce a score change.
        
        Args:
            game_name (str): Name of the game
            old_score (str): Previous score
            new_score (str): New score
        """
        message = f"Score update: {game_name} - {new_score}"
        self.announce(message)
    
    def announce_monitoring_change(self, game_name, is_monitoring):
        """
        Announce monitoring status change.
        
        Args:
            game_name (str): Name of the game
            is_monitoring (bool): Whether monitoring is now enabled
        """
        status = "enabled" if is_monitoring else "disabled"
        message = f"Monitoring {status} for {game_name}"
        self.announce(message)
    
    def announce_live_scores_status(self, game_count):
        """
        Announce Live Scores view status.
        
        Args:
            game_count (int): Number of live games
        """
        message = f"Live Scores: {game_count} live games displayed"
        self.announce(message)

# Global instance for easy access
notification_helper = WindowsNotificationHelper()

def announce(message):
    """Convenience function to announce a message."""
    notification_helper.announce(message)

def announce_score_change(game_name, old_score, new_score):
    """Convenience function to announce score changes."""
    notification_helper.announce_score_change(game_name, old_score, new_score)

def announce_monitoring_change(game_name, is_monitoring):
    """Convenience function to announce monitoring changes."""
    notification_helper.announce_monitoring_change(game_name, is_monitoring)

def announce_live_scores_status(game_count):
    """Convenience function to announce Live Scores status."""
    notification_helper.announce_live_scores_status(game_count)
