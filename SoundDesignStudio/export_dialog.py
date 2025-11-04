"""
Export Dialog for Sound Design Studio
Provides a user-friendly interface for exporting sound configurations.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QComboBox, QTextEdit, QLineEdit, QPushButton,
                            QGroupBox, QRadioButton, QButtonGroup, QCheckBox,
                            QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from sound_export_system import SoundConfigExporter, SoundLibrary
import json


class ExportDialog(QDialog):
    """Dialog for exporting sound configurations."""
    
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Export Sound Configuration")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Sound info section
        info_group = QGroupBox("Sound Information")
        info_layout = QVBoxLayout()
        
        # Sound name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Sound Name:"))
        self.name_input = QLineEdit()
        self.name_input.setText(self.config.get('name', 'Untitled Sound'))
        self.name_input.setAccessibleName("Sound name")
        self.name_input.setAccessibleDescription("Name for this sound configuration")
        name_layout.addWidget(self.name_input)
        info_layout.addLayout(name_layout)
        
        # Description
        info_layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe this sound and when to use it...")
        self.description_input.setMaximumHeight(80)
        self.description_input.setTabChangesFocus(True)
        self.description_input.setAccessibleName("Sound description")
        info_layout.addWidget(self.description_input)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Export destination
        dest_group = QGroupBox("Export Destination")
        dest_layout = QVBoxLayout()
        
        self.dest_button_group = QButtonGroup()
        
        self.dest_library = QRadioButton("Add to Sound Library (for app integration)")
        self.dest_library.setChecked(True)
        self.dest_library.setAccessibleName("Export to sound library")
        self.dest_button_group.addButton(self.dest_library)
        dest_layout.addWidget(self.dest_library)
        
        self.dest_file = QRadioButton("Export to File (for sharing or backup)")
        self.dest_file.setAccessibleName("Export to file")
        self.dest_button_group.addButton(self.dest_file)
        dest_layout.addWidget(self.dest_file)
        
        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)
        
        # Category selection
        category_group = QGroupBox("Category")
        category_layout = QVBoxLayout()
        
        category_layout.addWidget(QLabel("Choose a category for organization:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(SoundConfigExporter.CATEGORIES)
        self.category_combo.setAccessibleName("Sound category")
        category_layout.addWidget(self.category_combo)
        
        category_group.setLayout(category_layout)
        layout.addWidget(category_group)
        
        # Usage notes
        notes_group = QGroupBox("Usage Notes")
        notes_layout = QVBoxLayout()
        
        notes_layout.addWidget(QLabel("How should this sound be used?"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText(
            "Example:\n"
            "Use for touchdown celebrations in football\n"
            "Play when score > 20 points\n"
            "Frequency range: 800-1200 Hz works best"
        )
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setTabChangesFocus(True)
        self.notes_input.setAccessibleName("Usage notes")
        notes_layout.addWidget(self.notes_input)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Integration options
        options_group = QGroupBox("Integration Options")
        options_layout = QVBoxLayout()
        
        self.include_code_cb = QCheckBox("Include Python code example")
        self.include_code_cb.setChecked(True)
        self.include_code_cb.setAccessibleName("Include Python code example")
        options_layout.addWidget(self.include_code_cb)
        
        self.include_guide_cb = QCheckBox("Generate integration guide")
        self.include_guide_cb.setChecked(True)
        self.include_guide_cb.setAccessibleName("Generate integration guide")
        options_layout.addWidget(self.include_guide_cb)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Preview Export")
        self.preview_btn.setAccessibleName("Preview export")
        self.preview_btn.clicked.connect(self._preview_export)
        button_layout.addWidget(self.preview_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setAccessibleName("Cancel export")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.setAccessibleName("Confirm export")
        self.export_btn.setDefault(True)
        self.export_btn.clicked.connect(self._do_export)
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
    
    def _preview_export(self):
        """Show a preview of what will be exported."""
        name = self.name_input.text() or "Untitled"
        category = self.category_combo.currentText()
        description = self.description_input.toPlainText()
        notes = self.notes_input.toPlainText()
        
        # Build preview text
        preview = f"""Sound Export Preview
{'=' * 50}

Name: {name}
Category: {category}
Description: {description or '(none)'}

Usage Notes:
{notes or '(none)'}

Configuration Parameters:
- Frequency: {self.config.get('frequency', 440)} Hz
- Wave Type: {self.config.get('wave_type', 'sine')}
- Duration: {self.config.get('duration', 0.3)} seconds
- Volume: {self.config.get('volume', 0.5)}
- Attack: {self.config.get('attack', 0.01)} s
- Decay: {self.config.get('decay', 0.1)} s
- Sustain: {self.config.get('sustain', 0.7)}
- Release: {self.config.get('release', 0.1)} s

Harmonics Enabled: {self.config.get('harmonics', {}).get('enabled', False)}
Blending Enabled: {self.config.get('blending', {}).get('enabled', False)}

Export Destination: {'Sound Library' if self.dest_library.isChecked() else 'File'}
Include Code Example: {self.include_code_cb.isChecked()}
Include Integration Guide: {self.include_guide_cb.isChecked()}
"""
        
        # Show preview dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("Export Preview")
        msg.setText("Review your export configuration:")
        msg.setDetailedText(preview)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def _do_export(self):
        """Perform the export."""
        # Update config with user input
        self.config['name'] = self.name_input.text() or "Untitled"
        self.config['description'] = self.description_input.toPlainText()
        
        category = self.category_combo.currentText()
        notes = self.notes_input.toPlainText()
        
        try:
            if self.dest_library.isChecked():
                # Add to sound library
                SoundLibrary.add_to_library(
                    self.config,
                    category=category,
                    tags=[category.lower(), "custom"]
                )
                
                result_msg = (
                    f"✅ Sound '{self.config['name']}' added to library!\n\n"
                    f"Category: {category}\n"
                    f"Library file: sound_library.json"
                )
                
                # Generate integration guide if requested
                if self.include_guide_cb.isChecked():
                    guide = self._generate_integration_guide(category, notes)
                    guide_file = Path(f"{self.config['name'].replace(' ', '_')}_integration_guide.txt")
                    guide_file.write_text(guide)
                    result_msg += f"\n\n📄 Integration guide saved to:\n{guide_file}"
            
            else:
                # Export to file
                export_path = SoundConfigExporter.export_for_app(
                    self.config,
                    category=category,
                    notes=notes
                )
                
                result_msg = (
                    f"✅ Sound exported successfully!\n\n"
                    f"File: {export_path}\n"
                    f"Category: {category}"
                )
                
                # Generate integration guide if requested
                if self.include_guide_cb.isChecked():
                    guide = SoundConfigExporter.generate_integration_guide(
                        export_path,
                        notes or f"Custom sound: {self.config['name']}"
                    )
                    guide_file = Path(export_path).with_suffix('.integration.txt')
                    guide_file.write_text(guide)
                    result_msg += f"\n\n📄 Integration guide saved to:\n{guide_file}"
            
            # Show success message
            QMessageBox.information(self, "Export Successful", result_msg)
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export sound:\n{str(e)}"
            )
    
    def _generate_integration_guide(self, category: str, notes: str) -> str:
        """Generate an integration guide for the sound."""
        name = self.config['name']
        
        guide = f"""
{'=' * 70}
SOUND INTEGRATION GUIDE
Sound: {name}
Category: {category}
{'=' * 70}

OVERVIEW
--------
{self.config.get('description', 'Custom sound configuration')}

USAGE NOTES
-----------
{notes or 'No specific usage notes provided.'}

CONFIGURATION
-------------
Frequency: {self.config.get('frequency', 440)} Hz
Wave Type: {self.config.get('wave_type', 'sine')}
Duration: {self.config.get('duration', 0.3)} seconds
Volume: {self.config.get('volume', 0.5)}

ADSR Envelope:
- Attack: {self.config.get('attack', 0.01)} s
- Decay: {self.config.get('decay', 0.1)} s
- Sustain: {self.config.get('sustain', 0.7)}
- Release: {self.config.get('release', 0.1)} s

Harmonics: {'Enabled' if self.config.get('harmonics', {}).get('enabled', False) else 'Disabled'}
Blending: {'Enabled' if self.config.get('blending', {}).get('enabled', False) else 'Disabled'}

INTEGRATION STEPS
-----------------
1. Load the sound from the library:

   from sound_export_system import SoundLibrary
   
   library = SoundLibrary.load_library()
   sound = library['{name}']
   config = sound['config']

2. Create an audio player:

   from enhanced_audio_player import EnhancedAudioPlayer
   
   player = EnhancedAudioPlayer()
   player.set_harmonic_layering(config['harmonics']['enabled'])
   player.set_waveform_blending(config['blending']['enabled'])

3. Create audio configuration:

   from football_audio_mapper import PlayAudioConfig
   
   audio_config = PlayAudioConfig(
       frequency=config['frequency'],
       wave_type=config['wave_type'],
       duration=config['duration'],
       volume=config['volume'],
       attack=config['attack'],
       decay=config['decay'],
       sustain=config['sustain'],
       release=config['release']
   )

4. Play the sound:

   player.play_single_play(audio_config)

CUSTOMIZATION
-------------
To modify this sound:
1. Open sound_library.json
2. Find the '{name}' entry
3. Modify parameters as needed
4. Save and reload

No need to regenerate - just edit the JSON!

FOOTBALL-SPECIFIC INTEGRATION
------------------------------
To use this sound for specific play types:

"""

        # Add football-specific examples
        if category == "Football Plays":
            guide += """
# In your football audio code:
from football_audio_mapper import FootballAudioMapper

# Load your custom sound
custom_sound = library['{name}']

# Use it for specific play types:
def play_custom_touchdown_sound(self):
    config = PlayAudioConfig(
        frequency=custom_sound['config']['frequency'],
        wave_type=custom_sound['config']['wave_type'],
        duration=custom_sound['config']['duration'],
        volume=custom_sound['config']['volume'],
        attack=custom_sound['config']['attack'],
        decay=custom_sound['config']['decay'],
        play_type='touchdown'  # Activates sub-bass
    )
    self.audio_player.play_single_play(config, field_position=50)

# Available play types:
# - 'rush': Running plays
# - 'pass': Passing plays  
# - 'touchdown': Touchdowns (adds sub-bass)
# - 'field_goal': Field goals (adds sub-bass)
# - 'sack': Sacks
# - 'interception': Interceptions
# - 'fumble': Fumbles
# - 'penalty': Penalties
# - 'punt': Punts
# - 'kickoff': Kickoffs
""".format(name=name)
        
        guide += """

TIPS
----
- Test your sound in context before deploying
- Adjust volume based on other app sounds
- Consider user accessibility (frequency range, duration)
- Document any special usage requirements

For questions or issues, refer to the Sound Design Studio documentation.

{'=' * 70}
"""
        
        return guide


class BulkExportDialog(QDialog):
    """Dialog for exporting multiple sounds at once."""
    
    def __init__(self, presets: dict, parent=None):
        super().__init__(parent)
        self.presets = presets
        self.setWindowTitle("Bulk Export Presets")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(f"Export {len(self.presets)} presets as a collection:"))
        
        # Collection name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Collection Name:"))
        self.collection_name = QLineEdit()
        self.collection_name.setText("My Sound Collection")
        self.collection_name.setAccessibleName("Collection name")
        name_layout.addWidget(self.collection_name)
        layout.addLayout(name_layout)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description = QTextEdit()
        self.description.setPlaceholderText("Describe this collection of sounds...")
        self.description.setMaximumHeight(100)
        self.description.setTabChangesFocus(True)
        self.description.setAccessibleName("Collection description")
        layout.addWidget(self.description)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        export_btn = QPushButton("Export Collection")
        export_btn.setDefault(True)
        export_btn.clicked.connect(self._export_collection)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
    
    def _export_collection(self):
        """Export the preset collection."""
        collection_name = self.collection_name.text() or "Untitled Collection"
        
        try:
            export_path = SoundConfigExporter.export_preset_collection(
                self.presets,
                collection_name
            )
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"✅ Exported {len(self.presets)} sounds!\n\nFile: {export_path}"
            )
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export collection:\n{str(e)}"
            )
