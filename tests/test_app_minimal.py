"""
Minimal test to open the Football Audio Tutorial
Run this and press Enter on "Football Audio Tutorial" to test
"""

import sys
from PyQt6.QtWidgets import QApplication
from scores import SportsScoresApp

print("Starting minimal test...")
print("=" * 60)

app = QApplication(sys.argv)
window = SportsScoresApp()

print("\nApp created. Now opening Audio Tutorial menu...")
window.open_audio_tutorial()

print("\nYou should now see the Audio Tutorial menu.")
print("Press Enter on '🏈 Football Audio Tutorial' and watch the console...")
print("=" * 60)

window.show()
sys.exit(app.exec())
