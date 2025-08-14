#!/usr/bin/env python3
"""
Sports Scores Application - Main Entry Point
A comprehensive sports analysis application supporting MLB and NFL
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from scores import SportsScoresApp
    
    app = QApplication(sys.argv)
    window = SportsScoresApp()
    sys.exit(app.exec())
