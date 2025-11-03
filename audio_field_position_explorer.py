"""
Interactive Audio Field Position Explorer

Keyboard-accessible tool for experimenting with football audio field positioning.
Test different configurations and rate them to find optimal settings.
"""

import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, 
                             QComboBox, QPushButton, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

# Import our audio system
from audio_player import AudioPlayer
from football_audio_mapper import PlayAudioConfig


class AudioExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Football Audio Field Position Explorer")
        self.audio_player = AudioPlayer(stereo_enabled=True)
        self.log_file = "audio_experiments.log"
        self.current_config = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the UI with keyboard-accessible controls"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Instructions
        instructions = QLabel(
            "CONTROLS:\n"
            "Tab/Shift+Tab: Navigate between fields\n"
            "Up/Down Arrows: Adjust numeric values\n"
            "Space: Play audio with current settings\n"
            "Alt+Y: Mark current config as 'LIKED'\n"
            "Alt+N: Mark current config as 'DISLIKED'\n"
            "Alt+L: View experiment log\n"
            "Escape: Quit"
        )
        instructions.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        layout.addWidget(instructions)
        
        # Field Position Settings
        layout.addWidget(QLabel("\n=== FIELD POSITION SETTINGS ==="))
        
        # Starting position (yards to endzone)
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Yards to Endzone (0-100):"))
        self.yards_to_endzone = QSpinBox()
        self.yards_to_endzone.setRange(0, 100)
        self.yards_to_endzone.setValue(65)
        self.yards_to_endzone.setAccessibleName("Yards to endzone")
        pos_layout.addWidget(self.yards_to_endzone)
        layout.addLayout(pos_layout)
        
        # Yards gained on play
        gain_layout = QHBoxLayout()
        gain_layout.addWidget(QLabel("Yards Gained (-20 to 99):"))
        self.yards_gained = QSpinBox()
        self.yards_gained.setRange(-20, 99)
        self.yards_gained.setValue(8)
        self.yards_gained.setAccessibleName("Yards gained")
        gain_layout.addWidget(self.yards_gained)
        layout.addLayout(gain_layout)
        
        # Stereo multiplier
        mult_layout = QHBoxLayout()
        mult_layout.addWidget(QLabel("Stereo Multiplier (0.5 to 5.0):"))
        self.stereo_multiplier = QDoubleSpinBox()
        self.stereo_multiplier.setRange(0.5, 5.0)
        self.stereo_multiplier.setValue(2.0)
        self.stereo_multiplier.setSingleStep(0.1)
        self.stereo_multiplier.setDecimals(1)
        self.stereo_multiplier.setAccessibleName("Stereo multiplier")
        mult_layout.addWidget(self.stereo_multiplier)
        layout.addLayout(mult_layout)
        
        # Play Type
        layout.addWidget(QLabel("\n=== PLAY CHARACTERISTICS ==="))
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Play Type:"))
        self.play_type = QComboBox()
        self.play_type.addItems([
            "Rush - Short Gain",
            "Rush - Medium Gain", 
            "Rush - Long Gain",
            "Pass - Complete Short",
            "Pass - Complete Medium",
            "Pass - Complete Long",
            "Pass - Incomplete",
            "Sack",
            "Field Goal",
            "Punt",
            "Touchdown"
        ])
        self.play_type.setAccessibleName("Play type")
        type_layout.addWidget(self.play_type)
        layout.addLayout(type_layout)
        
        # Audio Settings
        layout.addWidget(QLabel("\n=== AUDIO SETTINGS ==="))
        
        # Base frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Base Frequency (200-800 Hz):"))
        self.base_frequency = QSpinBox()
        self.base_frequency.setRange(200, 800)
        self.base_frequency.setValue(440)
        self.base_frequency.setSingleStep(10)
        self.base_frequency.setAccessibleName("Base frequency")
        freq_layout.addWidget(self.base_frequency)
        layout.addLayout(freq_layout)
        
        # Duration
        dur_layout = QHBoxLayout()
        dur_layout.addWidget(QLabel("Duration (0.1 to 2.0 seconds):"))
        self.duration = QDoubleSpinBox()
        self.duration.setRange(0.1, 2.0)
        self.duration.setValue(0.2)
        self.duration.setSingleStep(0.1)
        self.duration.setDecimals(1)
        self.duration.setAccessibleName("Duration")
        dur_layout.addWidget(self.duration)
        layout.addLayout(dur_layout)
        
        # Volume
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Volume (0.1 to 1.0):"))
        self.volume = QDoubleSpinBox()
        self.volume.setRange(0.1, 1.0)
        self.volume.setValue(0.7)
        self.volume.setSingleStep(0.1)
        self.volume.setDecimals(1)
        self.volume.setAccessibleName("Volume")
        vol_layout.addWidget(self.volume)
        layout.addLayout(vol_layout)
        
        # Current calculated position display
        layout.addWidget(QLabel("\n=== CALCULATED VALUES ==="))
        self.calc_display = QLabel()
        self.calc_display.setStyleSheet("background-color: #e8f4f8; padding: 10px; font-family: monospace;")
        layout.addWidget(self.calc_display)
        self.update_calculations()
        
        # Connect value changes to update display
        self.yards_to_endzone.valueChanged.connect(self.update_calculations)
        self.yards_gained.valueChanged.connect(self.update_calculations)
        self.stereo_multiplier.valueChanged.connect(self.update_calculations)
        
        # Status
        self.status = QLabel("\nReady. Press SPACE to play audio.")
        self.status.setStyleSheet("font-weight: bold; color: green;")
        layout.addWidget(self.status)
        
        # Set initial focus
        self.yards_to_endzone.setFocus()
        
    def update_calculations(self):
        """Update the display of calculated field positions"""
        yards_to_endzone = self.yards_to_endzone.value()
        yards_gained = self.yards_gained.value()
        multiplier = self.stereo_multiplier.value()
        
        # Calculate raw position
        raw_position = 100 - yards_to_endzone
        
        # Calculate enhanced position with multiplier
        enhanced_position = (raw_position - 50) * multiplier + 50
        clamped_position = max(0, min(100, enhanced_position))
        
        # Calculate end position after play
        end_yards_to_endzone = max(0, yards_to_endzone - yards_gained)
        end_raw_position = 100 - end_yards_to_endzone
        end_enhanced_position = (end_raw_position - 50) * multiplier + 50
        end_clamped_position = max(0, min(100, end_enhanced_position))
        
        # Stereo interpretation
        def get_stereo_desc(pos):
            if pos < 20:
                return "FAR LEFT"
            elif pos < 40:
                return "LEFT"
            elif pos < 60:
                return "CENTER"
            elif pos < 80:
                return "RIGHT"
            else:
                return "FAR RIGHT"
        
        text = (
            f"Start: {yards_to_endzone} yards to endzone → "
            f"raw={raw_position} → enhanced={clamped_position:.1f} ({get_stereo_desc(clamped_position)})\n"
            f"Gain:  {yards_gained:+d} yards\n"
            f"End:   {end_yards_to_endzone} yards to endzone → "
            f"raw={end_raw_position} → enhanced={end_clamped_position:.1f} ({get_stereo_desc(end_clamped_position)})"
        )
        
        self.calc_display.setText(text)
        
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard shortcuts"""
        key = event.key()
        modifiers = event.modifiers()
        
        # Space to play
        if key == Qt.Key.Key_Space:
            self.play_audio()
            event.accept()
            return
            
        # Alt+Y to mark as liked
        if key == Qt.Key.Key_Y and modifiers == Qt.KeyboardModifier.AltModifier:
            self.record_rating("LIKED")
            event.accept()
            return
            
        # Alt+N to mark as disliked
        if key == Qt.Key.Key_N and modifiers == Qt.KeyboardModifier.AltModifier:
            self.record_rating("DISLIKED")
            event.accept()
            return
            
        # Alt+L to view log
        if key == Qt.Key.Key_L and modifiers == Qt.KeyboardModifier.AltModifier:
            self.view_log()
            event.accept()
            return
            
        # Escape to quit
        if key == Qt.Key.Key_Escape:
            self.close()
            event.accept()
            return
            
        super().keyPressEvent(event)
        
    def play_audio(self):
        """Generate and play audio with current settings"""
        self.status.setText("Playing audio...")
        QApplication.processEvents()
        
        # Get all settings
        yards_to_endzone = self.yards_to_endzone.value()
        multiplier = self.stereo_multiplier.value()
        
        # Calculate field position
        raw_position = 100 - yards_to_endzone
        enhanced_position = (raw_position - 50) * multiplier + 50
        field_position = max(0, min(100, enhanced_position))
        
        # Create audio config
        config = PlayAudioConfig(
            frequency=self.base_frequency.value(),
            duration=self.duration.value(),
            volume=self.volume.value(),
            wave_type='sine',
            attack=0.05,
            decay=0.05,
            field_position=field_position
        )
        
        # Store config for rating
        self.current_config = {
            'timestamp': datetime.now().isoformat(),
            'yards_to_endzone': yards_to_endzone,
            'yards_gained': self.yards_gained.value(),
            'stereo_multiplier': multiplier,
            'play_type': self.play_type.currentText(),
            'base_frequency': self.base_frequency.value(),
            'duration': self.duration.value(),
            'volume': self.volume.value(),
            'raw_position': raw_position,
            'enhanced_position': enhanced_position,
            'field_position': field_position
        }
        
        # Play the audio
        self.audio_player.play_audio_sequence([config], silence_between=0)
        
        self.status.setText(
            f"Played! Field position: {field_position:.1f}\n"
            "Press Alt+Y if you liked it, Alt+N if you didn't"
        )
        
    def record_rating(self, rating):
        """Record the rating for the current config"""
        if not self.current_config:
            self.status.setText("No audio has been played yet!")
            return
            
        self.current_config['rating'] = rating
        
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write("\n" + "="*80 + "\n")
            f.write(json.dumps(self.current_config, indent=2))
            f.write("\n")
        
        if rating == "LIKED":
            self.status.setText(f"✓ Marked as LIKED and logged!")
            self.status.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.status.setText(f"✗ Marked as DISLIKED and logged!")
            self.status.setStyleSheet("font-weight: bold; color: red;")
            
    def view_log(self):
        """Display the experiment log in a dialog"""
        from PyQt6.QtWidgets import QDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Experiment Log")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("font-family: monospace;")
        
        try:
            with open(self.log_file, 'r') as f:
                text_edit.setPlainText(f.read())
        except FileNotFoundError:
            text_edit.setPlainText("No experiments recorded yet.")
            
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close (Escape)")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()


def main():
    app = QApplication(sys.argv)
    explorer = AudioExplorer()
    explorer.resize(700, 850)
    explorer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
