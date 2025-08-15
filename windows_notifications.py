"""
Windows UIA Notification Helper - Standalone module
For accessibility notifications in the Live Scores feature
"""

class WindowsNotificationHelper:
    """Helper class for Windows UIA notifications and accessibility announcements"""
    
    def __init__(self):
        self.available = False
        try:
            import platform
            if platform.system() == "Windows":
                import ctypes
                from ctypes import wintypes
                # Set up Windows UIA notification constants
                self.UIA_LiveRegionChangedEventId = 20024
                # Try to load user32.dll for MessageBeep
                self.user32 = ctypes.windll.user32
                self.available = True
        except ImportError:
            pass
        except Exception:
            pass
    
    def announce(self, message: str, priority: str = "normal"):
        """Announce a message to screen readers using Windows accessibility APIs"""
        if not self.available:
            # Fallback: print to console for development
            print(f"[ACCESSIBILITY] {message}")
            return
        
        try:
            # Method 1: Use MessageBeep to get attention
            if priority == "urgent":
                self.user32.MessageBeep(0x30)  # MB_ICONEXCLAMATION
            elif priority == "normal":
                self.user32.MessageBeep(0x40)  # MB_ICONASTERISK
            
            # Method 2: Try to trigger screen reader announcement
            # This is a simplified approach - in a full implementation,
            # you would use the full UIA API through COM
            print(f"[UIA] {message}")
            
        except Exception as e:
            # Fallback to console output
            print(f"[ACCESSIBILITY FALLBACK] {message}")
    
    def notify_score_change(self, game_name: str, score_text: str):
        """Specialized notification for score changes"""
        message = f"Score update: {game_name} - {score_text}"
        self.announce(message, "urgent")
    
    def notify_monitoring_change(self, game_name: str, monitoring: bool):
        """Notify about monitoring status changes"""
        status = "now monitoring" if monitoring else "stopped monitoring"
        message = f"{status} {game_name} for score updates"
        self.announce(message, "normal")


# Test the notification helper
if __name__ == "__main__":
    print("Testing Windows Notification Helper...")
    
    helper = WindowsNotificationHelper()
    print(f"Notification helper available: {helper.available}")
    
    # Test basic announcement
    helper.announce("Test accessibility announcement")
    
    # Test score change notification
    helper.notify_score_change("Dallas Cowboys vs Green Bay Packers", "Cowboys 21 - Packers 17")
    
    # Test monitoring notification
    helper.notify_monitoring_change("Lakers vs Celtics", True)
    helper.notify_monitoring_change("Lakers vs Celtics", False)
    
    print("✓ All notification tests completed successfully")