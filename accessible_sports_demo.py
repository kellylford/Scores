#!/usr/bin/env python3
"""
Proof of concept: Sports Scores app using VoiceOver-friendly buttons instead of lists
"""

import sys
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                           QWidget, QPushButton, QLabel, QScrollArea, QFrame,
                           QGridLayout, QTextEdit)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class AccessibleSportsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accessible Sports Scores")
        self.setGeometry(100, 100, 700, 800)
        
        # Window accessibility
        self.setAccessibleName("Sports Scores Application")
        self.setAccessibleDescription("Accessible sports scores using button navigation")
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Sports Scores - VoiceOver Accessible")
        title.setAccessibleName("Application Title")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 15px; text-align: center;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Status area
        self.status = QLabel("Select a sport to view scores")
        self.status.setAccessibleName("Current Status")
        self.status.setStyleSheet("padding: 10px; background: #e8f4f8; border: 1px solid #ccc;")
        main_layout.addWidget(self.status)
        
        # Sports selection (using buttons instead of list)
        sports_frame = QFrame()
        sports_frame.setFrameStyle(QFrame.Shape.Box)
        sports_frame.setStyleSheet("border: 2px solid #ccc; margin: 10px; padding: 10px;")
        sports_layout = QVBoxLayout(sports_frame)
        
        sports_label = QLabel("Select Sport:")
        sports_label.setAccessibleName("Sports Selection Section")
        sports_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        sports_layout.addWidget(sports_label)
        
        # Create sport selection buttons
        sports_button_layout = QGridLayout()
        sports = [
            ("⚾ MLB", "Major League Baseball"),
            ("🏈 NFL", "National Football League"), 
            ("🏀 NBA", "National Basketball Association"),
            ("🏒 NHL", "National Hockey League")
        ]
        
        for i, (display, full_name) in enumerate(sports):
            btn = QPushButton(display)
            btn.setAccessibleName(f"{full_name} Scores")
            btn.setAccessibleDescription(f"View {full_name} games and scores")
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setMinimumHeight(50)
            btn.setStyleSheet("font-size: 14px; padding: 10px;")
            
            btn.clicked.connect(lambda checked, sport=full_name: self.show_sport_games(sport))
            
            row = i // 2
            col = i % 2
            sports_button_layout.addWidget(btn, row, col)
        
        sports_layout.addLayout(sports_button_layout)
        main_layout.addWidget(sports_frame)
        
        # Games display area (using buttons for each game)
        self.games_frame = QFrame()
        self.games_frame.setFrameStyle(QFrame.Shape.Box)
        self.games_frame.setStyleSheet("border: 2px solid #ccc; margin: 10px; padding: 10px;")
        self.games_layout = QVBoxLayout(self.games_frame)
        
        games_title = QLabel("Games:")
        games_title.setAccessibleName("Games Section")
        games_title.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        self.games_layout.addWidget(games_title)
        
        # Scroll area for games
        self.games_scroll = QScrollArea()
        self.games_scroll.setWidgetResizable(True)
        self.games_scroll.setAccessibleName("Games List")
        self.games_scroll.setAccessibleDescription("Scrollable list of games - use Tab to navigate between games")
        
        self.games_container = QWidget()
        self.games_container_layout = QVBoxLayout(self.games_container)
        self.games_scroll.setWidget(self.games_container)
        
        self.games_layout.addWidget(self.games_scroll)
        main_layout.addWidget(self.games_frame)
        
        # Initially show sample MLB games
        self.show_sport_games("Major League Baseball")
    
    def show_sport_games(self, sport):
        """Display games for selected sport using buttons"""
        self.status.setText(f"Showing {sport} games")
        self.status.setAccessibleDescription(f"Currently displaying {sport} games")
        
        # Clear existing games
        for i in reversed(range(self.games_container_layout.count())):
            child = self.games_container_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Sample game data (in real app, this would come from ESPN API)
        sample_games = self.get_sample_games(sport)
        
        # Create button for each game
        for i, game in enumerate(sample_games):
            game_btn = QPushButton(game['display'])
            game_btn.setAccessibleName(f"Game {i+1}: {game['accessible_name']}")
            game_btn.setAccessibleDescription(game['description'])
            game_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            game_btn.setMinimumHeight(60)
            game_btn.setStyleSheet("""
                QPushButton {
                    text-align: left; 
                    padding: 10px; 
                    margin: 2px;
                    font-size: 12px;
                    border: 1px solid #888;
                    background: white;
                }
                QPushButton:hover {
                    background: #f0f0f0;
                }
                QPushButton:focus {
                    border: 2px solid #0078d4;
                    background: #e8f4f8;
                }
            """)
            
            game_btn.clicked.connect(lambda checked, g=game: self.show_game_details(g))
            self.games_container_layout.addWidget(game_btn)
        
        # Add a spacer at the end
        self.games_container_layout.addStretch()
        
        print(f"Loaded {len(sample_games)} {sport} games")
    
    def get_sample_games(self, sport):
        """Get sample game data (replace with real ESPN API data)"""
        if "Baseball" in sport:
            return [
                {
                    'display': 'Yankees 7 - Red Sox 4\nFinal - Yankee Stadium',
                    'accessible_name': 'Yankees 7, Red Sox 4, Final game at Yankee Stadium',
                    'description': 'Completed baseball game: New York Yankees beat Boston Red Sox 7 to 4'
                },
                {
                    'display': 'Dodgers 3 - Giants 2\nBottom 8th - Oracle Park',
                    'accessible_name': 'Dodgers 3, Giants 2, Bottom 8th inning at Oracle Park',
                    'description': 'Live baseball game: Los Angeles Dodgers leading San Francisco Giants 3 to 2'
                },
                {
                    'display': 'Cubs 1 - Cardinals 5\nTop 6th - Busch Stadium',
                    'accessible_name': 'Cubs 1, Cardinals 5, Top 6th inning at Busch Stadium',
                    'description': 'Live baseball game: St. Louis Cardinals leading Chicago Cubs 5 to 1'
                }
            ]
        elif "Football" in sport:
            return [
                {
                    'display': 'Chiefs 21 - Bills 17\n2nd Quarter 8:45 - Arrowhead',
                    'accessible_name': 'Chiefs 21, Bills 17, 2nd Quarter 8:45 remaining at Arrowhead Stadium',
                    'description': 'Live football game: Kansas City Chiefs leading Buffalo Bills 21 to 17'
                },
                {
                    'display': 'Cowboys 14 - Eagles 10\nFinal - AT&T Stadium',
                    'accessible_name': 'Cowboys 14, Eagles 10, Final game at AT&T Stadium',
                    'description': 'Completed football game: Dallas Cowboys beat Philadelphia Eagles 14 to 10'
                }
            ]
        else:
            return [
                {
                    'display': f'Sample {sport} Game 1\nFinal Score: 100-95',
                    'accessible_name': f'Sample {sport} game 1, final score 100 to 95',
                    'description': f'Sample {sport} game with final score'
                }
            ]
    
    def show_game_details(self, game):
        """Show details for selected game"""
        self.status.setText(f"Selected: {game['accessible_name']}")
        self.status.setAccessibleDescription(f"Game details: {game['description']}")
        print(f"Game selected: {game['accessible_name']}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # macOS setup
    if platform.system() == "Darwin":
        app.setApplicationName("Accessible Sports Scores")
        app.setApplicationDisplayName("Accessible Sports Scores")
        
        # Accessibility attributes
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTabletEvents, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_MacDontSwapCtrlAndMeta, True)
        except:
            pass
        
        # Larger font
        font = QFont()
        font.setPointSize(14)
        app.setFont(font)
    
    window = AccessibleSportsApp()
    window.show()
    window.activateWindow()
    window.raise_()
    
    print("=== Accessible Sports Scores ===")
    print("VoiceOver-friendly design using buttons:")
    print("1. Tab to navigate between sports")
    print("2. Space/Enter to select sport")
    print("3. Tab through individual games")
    print("4. Each game is a separate button")
    print("5. All content announced by VoiceOver")
    print("==================================")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
