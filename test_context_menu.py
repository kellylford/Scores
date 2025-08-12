#!/usr/bin/env python3
"""
Test Context Menu Audio Features
================================
"""

from simple_audio_mapper import SimpleAudioPitchMapper
from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QMenu, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
import sys

class TestContextMenu(QWidget):
    """Test widget for context menu functionality"""
    
    def __init__(self):
        super().__init__()
        self.audio_mapper = SimpleAudioPitchMapper(self)
        self.setup_ui()
        self.create_sample_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Pitch Description"])
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.setWindowTitle("Test Pitch Audio Context Menu")
        self.resize(600, 400)
    
    def create_sample_data(self):
        """Create sample pitch data for testing"""
        
        # Create at-bat item
        at_bat = QTreeWidgetItem(["Francisco Lindor: Hit By Pitch"])
        self.tree.addTopLevelItem(at_bat)
        
        # Sample pitches from our analysis
        pitches = [
            {
                'text': "Strike Looking (95 mph Sinker) - Strike Zone (127, 115)",
                'data': {'is_pitch': True, 'x': 127, 'y': 115, 'velocity': 95, 'pitch_type': 'Sinker', 'batter_hand': 'R'}
            },
            {
                'text': "Strike Looking (93 mph Cutter) - Strike Zone (127, 100)", 
                'data': {'is_pitch': True, 'x': 127, 'y': 100, 'velocity': 93, 'pitch_type': 'Cutter', 'batter_hand': 'R'}
            },
            {
                'text': "Ball (82 mph Curve) - Low Outside (80, 180)",
                'data': {'is_pitch': True, 'x': 80, 'y': 180, 'velocity': 82, 'pitch_type': 'Curve', 'batter_hand': 'R'}
            },
            {
                'text': "Ball (92 mph Cutter) - Outside (90, 140)",
                'data': {'is_pitch': True, 'x': 90, 'y': 140, 'velocity': 92, 'pitch_type': 'Cutter', 'batter_hand': 'R'}
            },
            {
                'text': "Hit By Pitch (94 mph Sinker) - Low Way Inside (28, 199)",
                'data': {'is_pitch': True, 'x': 28, 'y': 199, 'velocity': 94, 'pitch_type': 'Sinker', 'batter_hand': 'R'}
            }
        ]
        
        for pitch in pitches:
            item = QTreeWidgetItem([f"  {pitch['text']}"])
            item.setData(0, Qt.ItemDataRole.UserRole, pitch['data'])
            at_bat.addChild(item)
        
        at_bat.setExpanded(True)
    
    def show_context_menu(self, position):
        """Show context menu for pitch items"""
        item = self.tree.itemAt(position)
        if item and self.is_pitch_item(item):
            self.show_pitch_context_menu(item, self.tree.mapToGlobal(position))
    
    def is_pitch_item(self, item):
        """Check if item represents a pitch"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        return data and isinstance(data, dict) and data.get('is_pitch', False)
    
    def show_pitch_context_menu(self, tree_item, global_position):
        """Show context menu for pitch audio options"""
        menu = QMenu(self)
        menu.setAccessibleName("Pitch Audio Options")
        
        # Option 1: Play current pitch audio
        play_action = QAction("🔊 Play Pitch Audio", self)
        play_action.setShortcut("P")
        play_action.setStatusTip("Play spatial audio for the current pitch location")
        play_action.triggered.connect(lambda: self.play_pitch_audio(tree_item))
        menu.addAction(play_action)
        
        # Option 2: Play pitch sequence
        sequence_action = QAction("🎵 Play Pitch Sequence", self)
        sequence_action.setShortcut("S") 
        sequence_action.setStatusTip("Play audio for all pitches in this at-bat")
        sequence_action.triggered.connect(lambda: self.play_pitch_sequence(tree_item))
        menu.addAction(sequence_action)
        
        # Show menu
        menu.exec(global_position)
    
    def play_pitch_audio(self, tree_item):
        """Play audio for a single pitch"""
        data = tree_item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get('is_pitch'):
            x = data.get('x')
            y = data.get('y')
            velocity = data.get('velocity')
            pitch_type = data.get('pitch_type')
            batter_hand = data.get('batter_hand')
            
            print(f"Playing audio for: {pitch_type} {velocity}mph at ({x},{y})")
            self.audio_mapper.generate_pitch_audio(x, y, velocity, pitch_type, batter_hand)
    
    def play_pitch_sequence(self, tree_item):
        """Play audio sequence for all pitches in the at-bat"""
        at_bat_item = tree_item.parent()
        if not at_bat_item:
            return
        
        # Collect all pitch items
        pitch_items = []
        for i in range(at_bat_item.childCount()):
            child = at_bat_item.child(i)
            if self.is_pitch_item(child):
                pitch_items.append(child)
        
        print(f"Playing pitch sequence: {len(pitch_items)} pitches")
        self.play_sequence_with_timing(pitch_items, 0)
    
    def play_sequence_with_timing(self, pitch_items, index):
        """Play sequence with timing"""
        if index >= len(pitch_items):
            print("Sequence complete!")
            return
        
        # Play current pitch
        self.play_pitch_audio(pitch_items[index])
        
        # Schedule next pitch
        QTimer.singleShot(1200, lambda: self.play_sequence_with_timing(pitch_items, index + 1))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    widget = TestContextMenu()
    widget.show()
    
    print("Test Context Menu Application")
    print("==============================")
    print("1. Right-click on any pitch to show context menu")
    print("2. Or use Shift+F10 when pitch is selected")
    print("3. Choose 'Play Pitch Audio' or 'Play Pitch Sequence'")
    print("4. Listen for beeps representing pitch locations!")
    
    app.exec()
