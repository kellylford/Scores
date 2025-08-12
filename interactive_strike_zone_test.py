#!/usr/bin/env python3
"""
Interactive Strike Zone Audio Test
==================================
Use arrow keys to move around the strike zone and test audio positioning
with adjustable left/right multiplier for fine-tuning stereo balance
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QGridLayout, QSpinBox,
                            QDoubleSpinBox, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette
from stereo_audio_mapper import StereoAudioPitchMapper

class StrikeZoneTestApp(QMainWindow):
    """Interactive strike zone audio testing application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Strike Zone Audio Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Audio system - use true stereo for better L/R multiplier testing
        # Use lr_multiplier=1.0 to disable built-in multiplier, we'll apply our own
        self.audio_mapper = StereoAudioPitchMapper(lr_multiplier=1.0)
        
        # Current position (start in center)
        self.current_x = 127
        self.current_y = 127
        self.min_x, self.max_x = 0, 255
        self.min_y, self.max_y = 0, 255
        
        # Movement step size
        self.step_size = 10
        
        # Left/Right balance multiplier - optimized value from testing
        self.lr_multiplier = 3.75
        
        self.setup_ui()
        self.update_display()
        
        # Enable keyboard focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def setup_ui(self):
        """Set up the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Strike Zone Audio Test")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Brief usage note
        usage_note = QLabel("Tab to Play button | Arrow Keys: move | I/K: L/R multiplier ±0.5 | Q/A: step size ±10 | Enter/Space: play")
        usage_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        usage_note.setStyleSheet("color: #666; padding: 5px;")
        main_layout.addWidget(usage_note)
        
        # Current position display
        self.position_frame = QFrame()
        self.position_frame.setFrameStyle(QFrame.Shape.Box)
        self.position_frame.setStyleSheet("background-color: #e8f4fd; padding: 15px; border-radius: 8px;")
        pos_layout = QVBoxLayout(self.position_frame)
        
        self.coords_label = QLabel()
        coords_font = QFont()
        coords_font.setPointSize(14)
        coords_font.setBold(True)
        self.coords_label.setFont(coords_font)
        self.coords_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pos_layout.addWidget(self.coords_label)
        
        self.location_label = QLabel()
        location_font = QFont()
        location_font.setPointSize(12)
        self.location_label.setFont(location_font)
        self.location_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pos_layout.addWidget(self.location_label)
        
        self.balance_label = QLabel()
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pos_layout.addWidget(self.balance_label)
        
        main_layout.addWidget(self.position_frame)
        
        # Controls section
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.Box)
        controls_frame.setStyleSheet("background-color: #f8f8f8; padding: 10px; border-radius: 5px;")
        controls_layout = QGridLayout(controls_frame)
        
        # Movement step size
        controls_layout.addWidget(QLabel("Arrow Key Step Size:"), 0, 0)
        self.step_spinbox = QSpinBox()
        self.step_spinbox.setRange(1, 50)
        self.step_spinbox.setValue(self.step_size)
        self.step_spinbox.valueChanged.connect(self.on_step_size_changed)
        self.step_spinbox.setKeyboardTracking(True)
        controls_layout.addWidget(self.step_spinbox, 0, 1)
        
        # Left/Right multiplier
        controls_layout.addWidget(QLabel("Left/Right Balance Multiplier:"), 1, 0)
        self.lr_spinbox = QDoubleSpinBox()
        self.lr_spinbox.setRange(0.1, 5.0)
        self.lr_spinbox.setSingleStep(0.05)
        self.lr_spinbox.setDecimals(2)
        self.lr_spinbox.setValue(self.lr_multiplier)
        self.lr_spinbox.valueChanged.connect(self.on_lr_multiplier_changed)
        self.lr_spinbox.setKeyboardTracking(True)
        controls_layout.addWidget(self.lr_spinbox, 1, 1)
        
        # Play audio button with coordinates
        self.play_button = QPushButton()
        self.play_button.clicked.connect(self.play_audio)
        self.play_button.setStyleSheet("QPushButton { padding: 15px; font-size: 14px; background-color: #4CAF50; color: white; border-radius: 5px; }")
        # Override the button's keyPressEvent to handle arrow keys
        self.play_button.keyPressEvent = self.play_button_key_press
        controls_layout.addWidget(self.play_button, 2, 0, 1, 2)
        
        main_layout.addWidget(controls_frame)
        
        # Visual strike zone representation
        zone_frame = QFrame()
        zone_frame.setFrameStyle(QFrame.Shape.Box)
        zone_frame.setStyleSheet("background-color: #ffffff; padding: 10px; border-radius: 5px;")
        zone_layout = QVBoxLayout(zone_frame)
        
        zone_title = QLabel("Strike Zone")
        zone_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zone_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        zone_layout.addWidget(zone_title)
        
        # Create 3x3 grid for strike zone
        self.zone_grid = QGridLayout()
        self.zone_buttons = []
        
        zone_positions = [
            ("High Left", 0, 0), ("High Center", 0, 1), ("High Right", 0, 2),
            ("Mid Left", 1, 0), ("Center", 1, 1), ("Mid Right", 1, 2),
            ("Low Left", 2, 0), ("Low Center", 2, 1), ("Low Right", 2, 2)
        ]
        
        for label, row, col in zone_positions:
            btn = QPushButton(label)
            btn.setFixedSize(100, 60)
            btn.clicked.connect(lambda checked, r=row, c=col: self.jump_to_zone(r, c))
            self.zone_grid.addWidget(btn, row, col)
            self.zone_buttons.append((btn, row, col))
        
        zone_widget = QWidget()
        zone_widget.setLayout(self.zone_grid)
        zone_layout.addWidget(zone_widget)
        main_layout.addWidget(zone_frame)
        
        # Sample pitch sequences section
        sequences_frame = QFrame()
        sequences_frame.setFrameStyle(QFrame.Shape.Box)
        sequences_frame.setStyleSheet("background-color: #f0f8ff; padding: 10px; border-radius: 5px;")
        sequences_layout = QVBoxLayout(sequences_frame)
        
        sequences_title = QLabel("Sample Pitch Sequences")
        sequences_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sequences_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        sequences_layout.addWidget(sequences_title)
        
        # Grid layout for sequence buttons
        seq_grid = QGridLayout()
        
        # Strikeout sequence
        strikeout_btn = QPushButton("Strikeout\n(3 strikes)")
        strikeout_btn.setFixedSize(140, 60)
        strikeout_btn.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; font-weight: bold; border-radius: 5px; }")
        strikeout_btn.clicked.connect(lambda: self.play_pitch_sequence("strikeout"))
        seq_grid.addWidget(strikeout_btn, 0, 0)
        
        # Walk sequence
        walk_btn = QPushButton("Walk\n(4 balls)")
        walk_btn.setFixedSize(140, 60)
        walk_btn.setStyleSheet("QPushButton { background-color: #4ecdc4; color: white; font-weight: bold; border-radius: 5px; }")
        walk_btn.clicked.connect(lambda: self.play_pitch_sequence("walk"))
        seq_grid.addWidget(walk_btn, 0, 1)
        
        # Hit by pitch
        hbp_btn = QPushButton("Hit By Pitch\n(Inside pitch)")
        hbp_btn.setFixedSize(140, 60)
        hbp_btn.setStyleSheet("QPushButton { background-color: #ffa726; color: white; font-weight: bold; border-radius: 5px; }")
        hbp_btn.clicked.connect(lambda: self.play_pitch_sequence("hbp"))
        seq_grid.addWidget(hbp_btn, 0, 2)
        
        # Home run sequence
        homerun_btn = QPushButton("Home Run\n(Down the middle)")
        homerun_btn.setFixedSize(140, 60)
        homerun_btn.setStyleSheet("QPushButton { background-color: #66bb6a; color: white; font-weight: bold; border-radius: 5px; }")
        homerun_btn.clicked.connect(lambda: self.play_pitch_sequence("homerun"))
        seq_grid.addWidget(homerun_btn, 1, 0)
        
        # Tough at-bat sequence
        tough_ab_btn = QPushButton("Tough At-Bat\n(10 pitches)")
        tough_ab_btn.setFixedSize(140, 60)
        tough_ab_btn.setStyleSheet("QPushButton { background-color: #7e57c2; color: white; font-weight: bold; border-radius: 5px; }")
        tough_ab_btn.clicked.connect(lambda: self.play_pitch_sequence("tough_ab"))
        seq_grid.addWidget(tough_ab_btn, 1, 1)
        
        sequences_layout.addLayout(seq_grid)
        
        # Sequence status
        self.sequence_status = QLabel("Click a sequence button to hear realistic pitch patterns")
        self.sequence_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sequence_status.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        sequences_layout.addWidget(self.sequence_status)
        
        main_layout.addWidget(sequences_frame)
        
        # Status and audio info
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        # Update status
        self.status_label.setText("True stereo audio enabled - use headphones for best results")
    
    def keyPressEvent(self, event):
        """Handle arrow key navigation"""
        key = event.key()
        
        # Only handle arrow keys if no widget has focus (or main window has focus)
        focused_widget = self.focusWidget()
        if focused_widget and focused_widget != self:
            # If a spinbox or other control has focus, let it handle the key event
            super().keyPressEvent(event)
            return
        
        if key == Qt.Key.Key_Up:
            self.current_y = max(self.min_y, self.current_y - self.step_size)
            self.update_display()
        elif key == Qt.Key.Key_Down:
            self.current_y = min(self.max_y, self.current_y + self.step_size)
            self.update_display()
        elif key == Qt.Key.Key_Left:
            self.current_x = max(self.min_x, self.current_x - self.step_size)
            self.update_display()
        elif key == Qt.Key.Key_Right:
            self.current_x = min(self.max_x, self.current_x + self.step_size)
            self.update_display()
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter or key == Qt.Key.Key_Space:
            self.play_audio()
        else:
            super().keyPressEvent(event)
    
    def play_button_key_press(self, event):
        """Handle key presses when play button has focus"""
        key = event.key()
        
        if key == Qt.Key.Key_Up:
            self.current_y = max(self.min_y, self.current_y - self.step_size)
            self.update_display()
            event.accept()
        elif key == Qt.Key.Key_Down:
            self.current_y = min(self.max_y, self.current_y + self.step_size)
            self.update_display()
            event.accept()
        elif key == Qt.Key.Key_Left:
            self.current_x = max(self.min_x, self.current_x - self.step_size)
            self.update_display()
            event.accept()
        elif key == Qt.Key.Key_Right:
            self.current_x = min(self.max_x, self.current_x + self.step_size)
            self.update_display()
            event.accept()
        elif key == Qt.Key.Key_I:  # Increase L/R multiplier
            self.lr_multiplier = min(5.0, self.lr_multiplier + 0.5)
            self.lr_spinbox.setValue(self.lr_multiplier)
            self.update_display()
            event.accept()
        elif key == Qt.Key.Key_K:  # Decrease L/R multiplier
            self.lr_multiplier = max(0.1, self.lr_multiplier - 0.5)
            self.lr_spinbox.setValue(self.lr_multiplier)
            self.update_display()
            event.accept()
        elif key == Qt.Key.Key_Q:  # Increase step size
            self.step_size = min(50, self.step_size + 10)
            self.step_spinbox.setValue(self.step_size)
            event.accept()
        elif key == Qt.Key.Key_A:  # Decrease step size
            self.step_size = max(1, self.step_size - 10)
            self.step_spinbox.setValue(self.step_size)
            event.accept()
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter or key == Qt.Key.Key_Space:
            self.play_audio()
            event.accept()
        else:
            # Let the button handle other keys normally (like Tab)
            QPushButton.keyPressEvent(self.play_button, event)
    
    def on_step_size_changed(self, value):
        """Update step size"""
        self.step_size = value
    
    def on_lr_multiplier_changed(self, value):
        """Update left/right multiplier"""
        self.lr_multiplier = value
        self.update_display()
    
    def jump_to_zone(self, row, col):
        """Jump to specific strike zone position"""
        # Map grid position to actual strike zone coordinates
        x_positions = [100, 127, 155]  # Left Edge, Center, Right Edge (actual strike zone)
        y_positions = [50, 127, 200]   # High, Middle, Low
        
        self.current_x = x_positions[col]
        self.current_y = y_positions[row]
        self.update_display()
        self.play_audio()
    
    def update_display(self):
        """Update the position display and visual indicators"""
        # Update coordinate display
        self.coords_label.setText(f"Position: ({self.current_x}, {self.current_y})")
        
        # Update play button with current coordinates and force accessibility update
        button_text = f"Play Audio at ({self.current_x}, {self.current_y})"
        self.play_button.setText(button_text)
        self.play_button.setAccessibleName(button_text)  # Force screen reader update
        
        # Calculate audio parameters with multiplier
        x_norm = (self.current_x - self.min_x) / (self.max_x - self.min_x)
        y_norm = (self.current_y - self.min_y) / (self.max_y - self.min_y)
        
        # Apply left/right multiplier
        balance = x_norm
        adjusted_balance = 0.5 + (balance - 0.5) * self.lr_multiplier
        adjusted_balance = max(0.0, min(1.0, adjusted_balance))  # Clamp to valid range
        
        # Get location description
        location_desc = self.audio_mapper._get_location_description(self.current_x, self.current_y, 'R')
        self.location_label.setText(f"Location: {location_desc}")
        
        # Show balance information
        if adjusted_balance < 0.2:
            balance_desc = "FAR LEFT"
            balance_color = "#ff4444"
        elif adjusted_balance < 0.4:
            balance_desc = "LEFT"
            balance_color = "#ff8844"
        elif adjusted_balance < 0.6:
            balance_desc = "CENTER"
            balance_color = "#44aa44"
        elif adjusted_balance < 0.8:
            balance_desc = "RIGHT"
            balance_color = "#4488ff"
        else:
            balance_desc = "FAR RIGHT"
            balance_color = "#4444ff"
        
        self.balance_label.setText(f"Audio Balance: {adjusted_balance:.3f} ({balance_desc})")
        self.balance_label.setStyleSheet(f"color: {balance_color}; font-weight: bold;")
        
        # Update zone visualization
        self.update_zone_highlight()
    
    def update_zone_highlight(self):
        """Highlight the current zone in the visual grid"""
        # Determine which zone we're closest to
        zone_x = 0 if self.current_x < 85 else (1 if self.current_x < 165 else 2)
        zone_y = 0 if self.current_y < 85 else (1 if self.current_y < 165 else 2)
        
        # Reset all button styles
        for btn, row, col in self.zone_buttons:
            if row == zone_y and col == zone_x:
                btn.setStyleSheet("QPushButton { background-color: #ffeb3b; font-weight: bold; }")
            else:
                btn.setStyleSheet("QPushButton { background-color: #f0f0f0; }")
    
    def play_audio(self):
        """Play audio at current position with applied multiplier"""
        try:
            # Create a modified stereo mapper that applies our L/R multiplier
            original_method = self.audio_mapper._coordinate_to_audio_params
            
            def modified_params(x, y, velocity=None, pitch_type=None, batter_hand=None):
                freq, duration, balance, location_desc = original_method(x, y, velocity, pitch_type, batter_hand)
                
                # Apply our multiplier to the balance
                adjusted_balance = 0.5 + (balance - 0.5) * self.lr_multiplier
                adjusted_balance = max(0.0, min(1.0, adjusted_balance))
                
                return freq, duration, adjusted_balance, location_desc
            
            # Temporarily replace the method
            self.audio_mapper._coordinate_to_audio_params = modified_params
            
            # Play the audio
            self.audio_mapper.generate_pitch_audio(
                self.current_x, self.current_y, 
                velocity=90, pitch_type="Test", batter_hand='R'
            )
            
            # Restore original method
            self.audio_mapper._coordinate_to_audio_params = original_method
            
            self.status_label.setText(f"✓ Stereo audio played at ({self.current_x}, {self.current_y}) with L/R multiplier {self.lr_multiplier}")
            
        except Exception as e:
            self.status_label.setText(f"Audio error: {str(e)}")
    
    def play_pitch_sequence(self, sequence_type):
        """Play a realistic pitch sequence with current L/R multiplier"""
        sequences = {
            "strikeout": [
                # Fastball strike, slider outside, curveball swinging strike
                {"x": 140, "y": 120, "velocity": 95, "pitch_type": "Fastball", "desc": "Strike 1: Fastball over plate"},
                {"x": 180, "y": 140, "velocity": 87, "pitch_type": "Slider", "desc": "Ball 1: Slider outside"},
                {"x": 130, "y": 180, "velocity": 78, "pitch_type": "Curveball", "desc": "Strike 2: Curveball low"}
            ],
            "walk": [
                # Four balls - pitcher missing the zone
                {"x": 80, "y": 100, "velocity": 92, "pitch_type": "Fastball", "desc": "Ball 1: Fastball inside"},
                {"x": 190, "y": 130, "velocity": 85, "pitch_type": "Changeup", "desc": "Ball 2: Changeup outside"},
                {"x": 120, "y": 60, "velocity": 94, "pitch_type": "Fastball", "desc": "Ball 3: Fastball high"},
                {"x": 200, "y": 160, "velocity": 89, "pitch_type": "Slider", "desc": "Ball 4: Slider way outside"}
            ],
            "hbp": [
                # Build up to hit by pitch - getting more inside
                {"x": 120, "y": 110, "velocity": 93, "pitch_type": "Fastball", "desc": "Strike 1: Fastball over plate"},
                {"x": 100, "y": 125, "velocity": 90, "pitch_type": "Fastball", "desc": "Ball 1: Fastball inside"},
                {"x": 70, "y": 120, "velocity": 92, "pitch_type": "Fastball", "desc": "HBP: Fastball way inside!"}
            ],
            "homerun": [
                # Pitcher gets behind, throws meatball down the middle
                {"x": 180, "y": 140, "velocity": 87, "pitch_type": "Slider", "desc": "Ball 1: Slider outside"},
                {"x": 200, "y": 80, "velocity": 84, "pitch_type": "Changeup", "desc": "Ball 2: Changeup high/outside"},
                {"x": 127, "y": 140, "velocity": 91, "pitch_type": "Fastball", "desc": "HOME RUN: Fastball down the middle!"}
            ],
            "tough_ab": [
                # Long at-bat with lots of foul balls
                {"x": 140, "y": 120, "velocity": 95, "pitch_type": "Fastball", "desc": "Strike 1: Fastball"},
                {"x": 180, "y": 140, "velocity": 87, "pitch_type": "Slider", "desc": "Ball 1: Slider outside"},
                {"x": 130, "y": 180, "velocity": 78, "pitch_type": "Curveball", "desc": "Strike 2: Curveball"},
                {"x": 160, "y": 110, "velocity": 92, "pitch_type": "Fastball", "desc": "Foul: Fastball outside"},
                {"x": 150, "y": 130, "velocity": 85, "pitch_type": "Changeup", "desc": "Foul: Changeup"},
                {"x": 110, "y": 120, "velocity": 90, "pitch_type": "Cutter", "desc": "Foul: Cutter inside"},
                {"x": 170, "y": 125, "velocity": 88, "pitch_type": "Slider", "desc": "Foul: Slider"},
                {"x": 145, "y": 135, "velocity": 93, "pitch_type": "Fastball", "desc": "Foul: Fastball"},
                {"x": 120, "y": 160, "velocity": 81, "pitch_type": "Curveball", "desc": "Ball 2: Curveball low"},
                {"x": 135, "y": 125, "velocity": 89, "pitch_type": "Changeup", "desc": "Strike 3: Changeup for the strikeout!"}
            ]
        }
        
        if sequence_type not in sequences:
            self.sequence_status.setText("Unknown sequence type")
            return
        
        pitches = sequences[sequence_type]
        self.sequence_status.setText(f"Playing {sequence_type} sequence ({len(pitches)} pitches)...")
        
        # Play each pitch with a delay
        self.current_sequence = pitches
        self.current_pitch_index = 0
        self.play_next_pitch_in_sequence()
    
    def play_next_pitch_in_sequence(self):
        """Play the next pitch in the current sequence"""
        if not hasattr(self, 'current_sequence') or self.current_pitch_index >= len(self.current_sequence):
            self.sequence_status.setText("Sequence complete!")
            return
        
        pitch = self.current_sequence[self.current_pitch_index]
        
        try:
            # Temporarily modify the audio mapper to use our multiplier
            original_method = self.audio_mapper._coordinate_to_audio_params
            
            def modified_params(x, y, velocity=None, pitch_type=None, batter_hand=None):
                freq, duration, balance, location_desc = original_method(x, y, velocity, pitch_type, batter_hand)
                
                # Apply our multiplier to the balance
                adjusted_balance = 0.5 + (balance - 0.5) * self.lr_multiplier
                adjusted_balance = max(0.0, min(1.0, adjusted_balance))
                
                return freq, duration, adjusted_balance, location_desc
            
            # Temporarily replace the method
            self.audio_mapper._coordinate_to_audio_params = modified_params
            
            # Play the pitch
            self.audio_mapper.generate_pitch_audio(
                pitch["x"], pitch["y"], 
                velocity=pitch["velocity"], 
                pitch_type=pitch["pitch_type"], 
                batter_hand='R'
            )
            
            # Restore original method
            self.audio_mapper._coordinate_to_audio_params = original_method
            
            # Update status
            self.sequence_status.setText(f"Pitch {self.current_pitch_index + 1}: {pitch['desc']}")
            
            # Move to next pitch
            self.current_pitch_index += 1
            
            # Schedule next pitch (1.5 second delay)
            QTimer.singleShot(1500, self.play_next_pitch_in_sequence)
            
        except Exception as e:
            self.sequence_status.setText(f"Sequence error: {str(e)}")

def main():
    """Run the interactive strike zone test application"""
    app = QApplication(sys.argv)
    
    window = StrikeZoneTestApp()
    window.show()
    
    print("Strike Zone Audio Test")
    print("Use arrow keys to navigate, Enter/Space to play audio")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
