"""
Sound Design Studio - Fully Keyboard-Accessible Audio Experimentation Tool

An interactive studio for exploring audio synthesis possibilities in Python.
Build, test, and save custom sound designs without pre-made WAV files!

Features:
- Real-time waveform parameter editing
- Harmonic layering controls
- ADSR envelope shaping
- Sound preset library
- A/B comparison testing
- Export/import sound configurations
- Full keyboard navigation

Keyboard Shortcuts:
- Tab/Shift+Tab: Navigate controls
- Space/Enter: Play current sound
- Ctrl+S: Save preset
- Ctrl+L: Load preset
- Ctrl+N: New sound
- Ctrl+C: Copy current settings
- 1-9: Quick load preset slots
- Alt+C: Compare with previous sound
"""

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QComboBox, QPushButton, QGroupBox, QTextEdit,
    QCheckBox, QSpinBox, QDoubleSpinBox, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QTabWidget, QGridLayout, QLineEdit, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from enhanced_audio_player import EnhancedAudioPlayer
from football_audio_mapper import PlayAudioConfig
from SoundDesignStudio.advanced_synthesis import AdvancedSynthesis


class SoundDesignStudio(QMainWindow):
    """Main window for sound design experimentation."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Design Studio - Audio Experimentation Tool")
        self.setMinimumSize(1000, 700)
        
        # Add status bar
        self.statusBar().showMessage("Ready - Press Alt+P to play sound, Ctrl+I for current settings info")
        
        # Audio system
        self.audio_player = EnhancedAudioPlayer()
        
        # Current sound configuration
        self.current_config = self._default_config()
        self.previous_config = None  # For A/B comparison
        
        # Preset library
        self.presets = self._load_default_presets()
        self.preset_file = Path("sound_presets.json")
        
        self.setup_ui()
        self.setup_shortcuts()
        self.load_presets_from_file()
        self.update_sound_description()
        
        # Initialize advanced controls visibility based on default synth type
        self._update_advanced_controls_visibility()
    
    def _default_config(self):
        """Create default sound configuration."""
        return {
            'frequency': 440.0,
            'wave_type': 'sine',
            'duration': 0.5,
            'volume': 0.3,
            'attack': 0.01,
            'decay': 0.1,
            'sustain': 0.7,
            'release': 0.15,
            'harmonics': {
                'enabled': True,
                'octave_volume': 0.3,
                'fifth_volume': 0.2,
                'sub_bass_volume': 0.0
            },
            'blending': {
                'enabled': True,
                'blend_ratio': 0.5
            },
            'advanced': {
                'enabled': False,
                'synthesis_type': 'fm',  # 'fm', 'noise', 'karplus'
                # FM Synthesis
                'fm_mod_ratio': 1.4,
                'fm_mod_index': 5.0,
                # Noise
                'noise_type': 'white',  # 'white', 'pink', 'brown'
                'noise_filter_enabled': False,
                'noise_filter_type': 'bandpass',  # 'bandpass', 'highpass', 'lowpass'
                'noise_filter_low': 2000.0,
                'noise_filter_high': 8000.0,
                # Effects
                'lfo_enabled': False,
                'lfo_frequency': 5.0,
                'lfo_depth': 0.3,
                'echo_enabled': False,
                'echo_delay': 0.3,
                'echo_feedback': 0.4
            },
            'name': 'Untitled Sound',
            'description': '',
            'play_type': 'custom'
        }
    
    def setup_ui(self):
        """Build the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Store control references for easy access
        self.controls = {}
        
        # Left side: Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Sound info
        info_group = QGroupBox("Sound Information")
        info_layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Sound name...")
        self.name_input.setAccessibleName("Sound name")
        self.name_input.setAccessibleDescription("Enter a name for this sound")
        self.name_input.textChanged.connect(self._on_name_changed)
        info_layout.addWidget(QLabel("Name:"))
        info_layout.addWidget(self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe this sound...")
        self.description_input.setMaximumHeight(60)
        self.description_input.setAccessibleName("Sound description")
        self.description_input.setAccessibleDescription("Enter a description for this sound")
        self.description_input.setTabChangesFocus(True)  # Tab navigates out instead of inserting tab
        self.description_input.textChanged.connect(self._on_description_changed)
        info_layout.addWidget(QLabel("Description:"))
        info_layout.addWidget(self.description_input)
        
        info_group.setLayout(info_layout)
        left_layout.addWidget(info_group)
        
        # Tabs for different parameter groups
        tabs = QTabWidget()
        
        # Tab 1: Basic Parameters
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Frequency
        freq_group = self._create_slider_control(
            "Frequency (Hz)",
            20, 2000, 440,
            callback=self._on_frequency_changed,
            suffix=" Hz"
        )
        self.controls['frequency'] = freq_group
        basic_layout.addWidget(freq_group)
        
        # Wave type
        wave_group = QGroupBox("Waveform Type")
        wave_layout = QVBoxLayout()
        wave_desc = QLabel("Select waveform shape")
        wave_layout.addWidget(wave_desc)
        self.wave_combo = QComboBox()
        self.wave_combo.addItems(['sine', 'square', 'sawtooth', 'triangle'])
        self.wave_combo.setAccessibleName("Waveform type")
        self.wave_combo.setAccessibleDescription("Choose the basic waveform: sine (smooth), square (harsh), sawtooth (bright), triangle (soft)")
        self.wave_combo.currentTextChanged.connect(self._on_wave_type_changed)
        wave_layout.addWidget(self.wave_combo)
        wave_group.setLayout(wave_layout)
        basic_layout.addWidget(wave_group)
        
        # Duration
        duration_group = self._create_double_slider_control(
            "Duration (seconds)",
            0.1, 3.0, 0.5, 0.1,
            callback=self._on_duration_changed
        )
        self.controls['duration'] = duration_group
        basic_layout.addWidget(duration_group)
        
        # Volume
        volume_group = self._create_slider_control(
            "Volume",
            0, 100, 30,
            callback=self._on_volume_changed,
            suffix="%"
        )
        self.controls['volume'] = volume_group
        basic_layout.addWidget(volume_group)
        
        basic_layout.addStretch()
        tabs.addTab(basic_tab, "🎵 Basic")
        
        # Tab 2: ADSR Envelope
        envelope_tab = QWidget()
        envelope_layout = QVBoxLayout(envelope_tab)
        
        attack_group = self._create_slider_control(
            "Attack (ms)",
            0, 200, 10,
            callback=self._on_attack_changed,
            suffix=" ms"
        )
        self.controls['attack'] = attack_group
        envelope_layout.addWidget(attack_group)
        
        decay_group = self._create_slider_control(
            "Decay (ms)",
            0, 500, 100,
            callback=self._on_decay_changed,
            suffix=" ms"
        )
        self.controls['decay'] = decay_group
        envelope_layout.addWidget(decay_group)
        
        sustain_group = self._create_slider_control(
            "Sustain Level",
            0, 100, 70,
            callback=self._on_sustain_changed,
            suffix="%"
        )
        self.controls['sustain'] = sustain_group
        envelope_layout.addWidget(sustain_group)
        
        release_group = self._create_slider_control(
            "Release (ms)",
            0, 1000, 150,
            callback=self._on_release_changed,
            suffix=" ms"
        )
        self.controls['release'] = release_group
        envelope_layout.addWidget(release_group)
        
        # ADSR visualization description
        adsr_desc = QLabel(
            "ADSR Envelope shapes the sound over time:\n"
            "• Attack: How quickly sound reaches peak\n"
            "• Decay: Time to fall to sustain level\n"
            "• Sustain: Level maintained during play\n"
            "• Release: Fade out time at end"
        )
        adsr_desc.setWordWrap(True)
        adsr_desc.setStyleSheet("color: #666; font-size: 9pt; margin: 10px;")
        envelope_layout.addWidget(adsr_desc)
        
        envelope_layout.addStretch()
        tabs.addTab(envelope_tab, "📊 Envelope")
        
        # Tab 3: Harmonics
        harmonics_tab = QWidget()
        harmonics_layout = QVBoxLayout(harmonics_tab)
        
        self.harmonics_enabled = QCheckBox("Enable Harmonic Layering")
        self.harmonics_enabled.setChecked(True)
        self.harmonics_enabled.setAccessibleName("Enable harmonics")
        self.harmonics_enabled.setAccessibleDescription("Enable or disable harmonic layering for richer sound")
        self.harmonics_enabled.stateChanged.connect(self._on_harmonics_toggled)
        harmonics_layout.addWidget(self.harmonics_enabled)
        
        octave_group = self._create_slider_control(
            "Octave Up Volume (2x freq)",
            0, 100, 30,
            callback=self._on_octave_changed,
            suffix="%"
        )
        self.controls['octave'] = octave_group
        harmonics_layout.addWidget(octave_group)
        
        fifth_group = self._create_slider_control(
            "Fifth Volume (1.5x freq)",
            0, 100, 20,
            callback=self._on_fifth_changed,
            suffix="%"
        )
        self.controls['fifth'] = fifth_group
        harmonics_layout.addWidget(fifth_group)
        
        subbass_group = self._create_slider_control(
            "Sub-Bass Volume (0.5x freq)",
            0, 100, 0,
            callback=self._on_subbass_changed,
            suffix="%"
        )
        self.controls['subbass'] = subbass_group
        harmonics_layout.addWidget(subbass_group)
        
        harmonics_desc = QLabel(
            "Harmonics add richness and complexity:\n"
            "• Octave: Adds brightness and presence\n"
            "• Fifth: Adds musicality and warmth\n"
            "• Sub-bass: Adds weight and impact"
        )
        harmonics_desc.setWordWrap(True)
        harmonics_desc.setStyleSheet("color: #666; font-size: 9pt; margin: 10px;")
        harmonics_layout.addWidget(harmonics_desc)
        
        harmonics_layout.addStretch()
        tabs.addTab(harmonics_tab, "🎼 Harmonics")
        
        # Tab 4: Blending
        blending_tab = QWidget()
        blending_layout = QVBoxLayout(blending_tab)
        
        self.blending_enabled = QCheckBox("Enable Waveform Blending")
        self.blending_enabled.setChecked(True)
        self.blending_enabled.setAccessibleName("Enable blending")
        self.blending_enabled.setAccessibleDescription("Enable or disable waveform blending for warmer tones")
        self.blending_enabled.stateChanged.connect(self._on_blending_toggled)
        blending_layout.addWidget(self.blending_enabled)
        
        blend_group = self._create_slider_control(
            "Blend Ratio (Primary vs Secondary)",
            0, 100, 50,
            callback=self._on_blend_ratio_changed,
            suffix="%"
        )
        self.controls['blend_ratio'] = blend_group
        blending_layout.addWidget(blend_group)
        
        blend_desc = QLabel(
            "Blending mixes waveforms for warmer tones:\n"
            "• Square blends with Triangle\n"
            "• Sawtooth blends with Sine\n"
            "• Pure Sine stays unblended\n\n"
            "Blend ratio: 0% = pure primary, 100% = pure secondary"
        )
        blend_desc.setWordWrap(True)
        blend_desc.setStyleSheet("color: #666; font-size: 9pt; margin: 10px;")
        blending_layout.addWidget(blend_desc)
        
        blending_layout.addStretch()
        tabs.addTab(blending_tab, "🌊 Blending")
        
        # Tab 5: Advanced Synthesis
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        self.advanced_enabled = QCheckBox("Enable Advanced Synthesis")
        self.advanced_enabled.setChecked(False)
        self.advanced_enabled.setAccessibleName("Enable advanced synthesis")
        self.advanced_enabled.setAccessibleDescription("Enable or disable advanced synthesis techniques like FM, noise, and effects")
        self.advanced_enabled.stateChanged.connect(self._on_advanced_toggled)
        advanced_layout.addWidget(self.advanced_enabled)
        
        # Synthesis type selector
        synth_type_group = QGroupBox("Synthesis Type")
        synth_type_layout = QVBoxLayout()
        synth_type_layout.addWidget(QLabel("Choose advanced synthesis method:"))
        self.synth_type_combo = QComboBox()
        self.synth_type_combo.addItems(['fm', 'noise', 'karplus'])
        self.synth_type_combo.setAccessibleName("Synthesis type")
        self.synth_type_combo.setAccessibleDescription("Choose synthesis method: FM (bells, electric piano), Noise (percussion, atmospheres), Karplus-Strong (plucked strings)")
        self.synth_type_combo.currentTextChanged.connect(self._on_synth_type_changed)
        synth_type_layout.addWidget(self.synth_type_combo)
        synth_type_group.setLayout(synth_type_layout)
        advanced_layout.addWidget(synth_type_group)
        
        # FM Synthesis controls
        self.fm_group = QGroupBox("FM Synthesis Parameters")
        fm_layout = QVBoxLayout()
        
        fm_ratio_group = self._create_double_slider_control(
            "Modulator Ratio",
            0.5, 5.0, 1.4, 0.1,
            callback=self._on_fm_ratio_changed
        )
        self.controls['fm_ratio'] = fm_ratio_group
        fm_layout.addWidget(fm_ratio_group)
        
        fm_index_group = self._create_double_slider_control(
            "Modulation Index",
            0.0, 10.0, 5.0, 0.5,
            callback=self._on_fm_index_changed
        )
        self.controls['fm_index'] = fm_index_group
        fm_layout.addWidget(fm_index_group)
        
        fm_desc = QLabel(
            "FM Synthesis (Frequency Modulation):\n"
            "• Ratio 1.4, Index 5 = Bell\n"
            "• Ratio 14, Index 3 = Electric Piano\n"
            "• Ratio 1, Index 5 = Brass\n"
            "• Ratio 0.5, Index 2 = Organ"
        )
        fm_desc.setWordWrap(True)
        fm_desc.setStyleSheet("color: #666; font-size: 9pt; margin: 10px;")
        fm_layout.addWidget(fm_desc)
        self.fm_group.setLayout(fm_layout)
        advanced_layout.addWidget(self.fm_group)
        
        # Noise controls
        self.noise_group = QGroupBox("Noise Generator")
        noise_layout = QVBoxLayout()
        
        noise_layout.addWidget(QLabel("Noise Type:"))
        self.noise_type_combo = QComboBox()
        self.noise_type_combo.addItems(['white', 'pink', 'brown'])
        self.noise_type_combo.setAccessibleName("Noise type")
        self.noise_type_combo.setAccessibleDescription("White (hi-hat), Pink (ocean), Brown (thunder)")
        self.noise_type_combo.currentTextChanged.connect(self._on_noise_type_changed)
        noise_layout.addWidget(self.noise_type_combo)
        
        self.noise_filter_enabled = QCheckBox("Enable Noise Filter")
        self.noise_filter_enabled.setAccessibleName("Enable noise filter")
        self.noise_filter_enabled.stateChanged.connect(self._on_noise_filter_toggled)
        noise_layout.addWidget(self.noise_filter_enabled)
        
        noise_layout.addWidget(QLabel("Filter Type:"))
        self.noise_filter_combo = QComboBox()
        self.noise_filter_combo.addItems(['bandpass', 'highpass', 'lowpass'])
        self.noise_filter_combo.setAccessibleName("Filter type")
        self.noise_filter_combo.currentTextChanged.connect(self._on_noise_filter_type_changed)
        noise_layout.addWidget(self.noise_filter_combo)
        
        filter_low_group = self._create_slider_control(
            "Filter Low Cutoff (Hz)",
            100, 10000, 2000,
            callback=self._on_filter_low_changed,
            suffix=" Hz"
        )
        self.controls['filter_low'] = filter_low_group
        noise_layout.addWidget(filter_low_group)
        
        filter_high_group = self._create_slider_control(
            "Filter High Cutoff (Hz)",
            100, 10000, 8000,
            callback=self._on_filter_high_changed,
            suffix=" Hz"
        )
        self.controls['filter_high'] = filter_high_group
        noise_layout.addWidget(filter_high_group)
        
        noise_desc = QLabel(
            "Noise types:\n"
            "• White: Hi-hats, cymbals\n"
            "• Pink: Ocean, wind\n"
            "• Brown: Thunder, rumble"
        )
        noise_desc.setWordWrap(True)
        noise_desc.setStyleSheet("color: #666; font-size: 9pt; margin: 10px;")
        noise_layout.addWidget(noise_desc)
        self.noise_group.setLayout(noise_layout)
        advanced_layout.addWidget(self.noise_group)
        
        # Effects controls
        effects_group = QGroupBox("Effects")
        effects_layout = QVBoxLayout()
        
        # LFO
        self.lfo_enabled = QCheckBox("Enable LFO Tremolo")
        self.lfo_enabled.setAccessibleName("Enable LFO tremolo")
        self.lfo_enabled.stateChanged.connect(self._on_lfo_toggled)
        effects_layout.addWidget(self.lfo_enabled)
        
        lfo_freq_group = self._create_double_slider_control(
            "LFO Frequency",
            0.5, 10.0, 5.0, 0.5,
            callback=self._on_lfo_freq_changed
        )
        self.controls['lfo_freq'] = lfo_freq_group
        effects_layout.addWidget(lfo_freq_group)
        
        lfo_depth_group = self._create_slider_control(
            "LFO Depth",
            0, 100, 30,
            callback=self._on_lfo_depth_changed,
            suffix="%"
        )
        self.controls['lfo_depth'] = lfo_depth_group
        effects_layout.addWidget(lfo_depth_group)
        
        # Echo
        self.echo_enabled = QCheckBox("Enable Echo/Delay")
        self.echo_enabled.setAccessibleName("Enable echo delay")
        self.echo_enabled.stateChanged.connect(self._on_echo_toggled)
        effects_layout.addWidget(self.echo_enabled)
        
        echo_delay_group = self._create_double_slider_control(
            "Echo Delay Time",
            0.05, 1.0, 0.3, 0.05,
            callback=self._on_echo_delay_changed
        )
        self.controls['echo_delay'] = echo_delay_group
        effects_layout.addWidget(echo_delay_group)
        
        echo_feedback_group = self._create_slider_control(
            "Echo Feedback",
            0, 90, 40,
            callback=self._on_echo_feedback_changed,
            suffix="%"
        )
        self.controls['echo_feedback'] = echo_feedback_group
        effects_layout.addWidget(echo_feedback_group)
        
        effects_group.setLayout(effects_layout)
        advanced_layout.addWidget(effects_group)
        
        advanced_layout.addStretch()
        tabs.addTab(advanced_tab, "⚡ Advanced")
        
        left_layout.addWidget(tabs)
        
        # Play button
        play_button = QPushButton("▶️ Play Sound (Alt+P)")
        play_button.setAccessibleName("Play current sound")
        play_button.setAccessibleDescription("Play the current sound with all configured settings. Hotkey: Alt+P")
        play_button.clicked.connect(self.play_current_sound)
        play_button.setStyleSheet("font-size: 14pt; padding: 10px;")
        left_layout.addWidget(play_button)
        
        main_layout.addWidget(left_panel, stretch=2)
        
        # Right side: Presets and info
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Sound description (computed)
        desc_group = QGroupBox("Current Sound Analysis")
        desc_layout = QVBoxLayout()
        self.sound_description = QTextEdit()
        self.sound_description.setReadOnly(True)
        self.sound_description.setMaximumHeight(150)
        self.sound_description.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Don't tab to read-only display
        self.sound_description.setAccessibleName("Sound analysis")
        self.sound_description.setAccessibleDescription("Read-only display showing computed sound characteristics")
        desc_layout.addWidget(self.sound_description)
        desc_group.setLayout(desc_layout)
        right_layout.addWidget(desc_group)
        
        # Preset management
        preset_group = QGroupBox("Preset Library")
        preset_layout = QVBoxLayout()
        
        # Preset list
        self.preset_list = QListWidget()
        self.preset_list.setAccessibleName("Preset library")
        self.preset_list.setAccessibleDescription("List of saved sound presets. Press Enter to load, Delete to remove. Number keys 1-9 for quick load.")
        self.preset_list.itemActivated.connect(self._on_preset_activated)
        self.preset_list.itemClicked.connect(self._on_preset_clicked)
        # Prevent Space from playing sound when on preset list
        self.preset_list.keyPressEvent = self._preset_list_key_handler
        preset_layout.addWidget(self.preset_list)
        
        # Preset buttons
        preset_buttons = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save")
        save_btn.setAccessibleName("Save preset")
        save_btn.setAccessibleDescription("Save current sound as a preset. Hotkey: Ctrl+S")
        save_btn.clicked.connect(self.save_preset)
        save_btn.setToolTip("Save current sound as preset (Ctrl+S)")
        preset_buttons.addWidget(save_btn)
        
        load_btn = QPushButton("📂 Load")
        load_btn.setAccessibleName("Load preset")
        load_btn.setAccessibleDescription("Load the selected preset from the list. Hotkey: Ctrl+L")
        load_btn.clicked.connect(self.load_selected_preset)
        load_btn.setToolTip("Load selected preset (Ctrl+L)")
        preset_buttons.addWidget(load_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setAccessibleName("Delete preset")
        delete_btn.setAccessibleDescription("Delete the selected preset. Hotkey: Delete")
        delete_btn.clicked.connect(self.delete_preset)
        delete_btn.setToolTip("Delete selected preset (Delete)")
        preset_buttons.addWidget(delete_btn)
        
        preset_layout.addLayout(preset_buttons)
        
        preset_group.setLayout(preset_layout)
        right_layout.addWidget(preset_group)
        
        # Comparison tools
        compare_group = QGroupBox("A/B Comparison")
        compare_layout = QVBoxLayout()
        
        compare_desc = QLabel(
            "Test sounds side-by-side:\n"
            "1. Play a sound\n"
            "2. Modify parameters\n"
            "3. Use Compare to hear both"
        )
        compare_desc.setWordWrap(True)
        compare_layout.addWidget(compare_desc)
        
        compare_btn = QPushButton("🔊 Compare A/B (Alt+C)")
        compare_btn.setAccessibleName("Compare sounds A B")
        compare_btn.setAccessibleDescription("Play the previous sound followed by the current sound for comparison. Hotkey: Alt+C")
        compare_btn.clicked.connect(self.compare_sounds)
        compare_layout.addWidget(compare_btn)
        
        compare_group.setLayout(compare_layout)
        right_layout.addWidget(compare_group)
        
        # Export/Import
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        
        export_btn = QPushButton("📤 Export Presets")
        export_btn.setAccessibleName("Export presets")
        export_btn.setAccessibleDescription("Export all presets to a JSON file")
        export_btn.clicked.connect(self.export_presets)
        file_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📥 Import Presets")
        import_btn.setAccessibleName("Import presets")
        import_btn.setAccessibleDescription("Import presets from a JSON file")
        import_btn.clicked.connect(self.import_presets)
        file_layout.addWidget(import_btn)
        
        file_group.setLayout(file_layout)
        right_layout.addWidget(file_group)
        
        main_layout.addWidget(right_panel, stretch=1)
        
        # Load presets into list
        self.refresh_preset_list()
    
    def _create_slider_control(self, label, min_val, max_val, default_val, callback, suffix=""):
        """Create a labeled slider with value display and keyboard-accessible spinbox."""
        group = QGroupBox(label)
        layout = QVBoxLayout()
        
        # Add description label for screen readers
        desc_label = QLabel(f"{label}: {default_val}{suffix}")
        desc_label.setObjectName(f"{label}_desc")
        layout.addWidget(desc_label)
        
        control_layout = QHBoxLayout()
        
        # Use SpinBox for keyboard accessibility instead of slider
        spinbox = QSpinBox()
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setValue(default_val)
        spinbox.setSuffix(suffix)
        spinbox.setMinimumWidth(100)
        spinbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        spinbox.setAccessibleName(label)
        spinbox.setAccessibleDescription(f"Adjust {label} from {min_val} to {max_val}")
        spinbox.setKeyboardTracking(True)  # Update as you type/arrow
        
        # Optional: Add slider for mouse users (but spinbox is primary)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Don't tab to slider, only spinbox
        
        # Sync slider and spinbox
        def on_spinbox_change(value):
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
            desc_label.setText(f"{label}: {value}{suffix}")
            # Update accessible name with current value for screen readers
            spinbox.setAccessibleName(f"{label} {value}{suffix}")
            callback(value)
        
        def on_slider_change(value):
            spinbox.blockSignals(True)
            spinbox.setValue(value)
            spinbox.blockSignals(False)
        
        spinbox.valueChanged.connect(on_spinbox_change)
        slider.valueChanged.connect(on_slider_change)
        
        control_layout.addWidget(spinbox)
        control_layout.addWidget(slider)
        
        layout.addLayout(control_layout)
        group.setLayout(layout)
        
        # Store references for later updates
        setattr(group, 'spinbox', spinbox)
        setattr(group, 'slider', slider)
        setattr(group, 'desc_label', desc_label)
        
        return group
    
    def _create_double_slider_control(self, label, min_val, max_val, default_val, step, callback):
        """Create a control for floating point values with keyboard-accessible spinbox."""
        group = QGroupBox(label)
        layout = QVBoxLayout()
        
        # Add description label for screen readers
        desc_label = QLabel(f"{label}: {default_val:.2f}s")
        desc_label.setObjectName(f"{label}_desc")
        layout.addWidget(desc_label)
        
        control_layout = QHBoxLayout()
        
        # Use DoubleSpinBox for keyboard accessibility
        spinbox = QDoubleSpinBox()
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setValue(default_val)
        spinbox.setSingleStep(step)
        spinbox.setDecimals(2)
        spinbox.setSuffix(" s")
        spinbox.setMinimumWidth(100)
        spinbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        spinbox.setAccessibleName(label)
        spinbox.setAccessibleDescription(f"Adjust {label} from {min_val} to {max_val} seconds")
        spinbox.setKeyboardTracking(True)  # Update as you type/arrow
        
        # Optional slider for mouse users
        int_min = int(min_val / step)
        int_max = int(max_val / step)
        int_default = int(default_val / step)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(int_min)
        slider.setMaximum(int_max)
        slider.setValue(int_default)
        slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Don't tab to slider
        
        # Sync slider and spinbox
        def on_spinbox_change(float_val):
            int_val = int(float_val / step)
            slider.blockSignals(True)
            slider.setValue(int_val)
            slider.blockSignals(False)
            desc_label.setText(f"{label}: {float_val:.2f}s")
            # Update accessible name with current value for screen readers
            spinbox.setAccessibleName(f"{label} {float_val:.2f} seconds")
            callback(float_val)
        
        def on_slider_change(int_val):
            float_val = int_val * step
            spinbox.blockSignals(True)
            spinbox.setValue(float_val)
            spinbox.blockSignals(False)
        
        spinbox.valueChanged.connect(on_spinbox_change)
        slider.valueChanged.connect(on_slider_change)
        
        control_layout.addWidget(spinbox)
        control_layout.addWidget(slider)
        
        layout.addLayout(control_layout)
        group.setLayout(layout)
        
        setattr(group, 'spinbox', spinbox)
        setattr(group, 'slider', slider)
        setattr(group, 'desc_label', desc_label)
        
        return group
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Play sound - Use Alt+P instead of Space to avoid conflicts
        QShortcut(QKeySequence("Alt+P"), self, self.play_current_sound)
        
        # Enter only plays on specific widgets, not globally
        enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        enter_shortcut.activated.connect(self._on_enter_pressed)
        enter_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        
        enter2_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        enter2_shortcut.activated.connect(self._on_enter_pressed)
        enter2_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        
        # Save/Load
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_preset)
        QShortcut(QKeySequence("Ctrl+L"), self, self.load_selected_preset)
        QShortcut(QKeySequence("Ctrl+N"), self, self.new_sound)
        
        # Compare
        QShortcut(QKeySequence("Alt+C"), self, self.compare_sounds)
        
        # Delete
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self, self.delete_preset)
        
        # Quick load presets 1-9
        for i in range(1, 10):
            QShortcut(QKeySequence(f"{i}"), self, lambda idx=i-1: self.quick_load_preset(idx))
        
        # Status message
        QShortcut(QKeySequence("Ctrl+I"), self, self.show_current_settings)
    
    def _on_enter_pressed(self):
        """Handle Enter key - context-sensitive behavior."""
        focused = self.focusWidget()
        
        # Enter on preset list loads the preset
        if focused == self.preset_list:
            self.load_selected_preset()
        # Enter on Play button plays sound
        elif isinstance(focused, QPushButton) and "Play" in focused.text():
            self.play_current_sound()
        # Enter on spinboxes does nothing (use arrows to adjust)
        # Enter on checkboxes does nothing (use space to toggle)
        # Enter elsewhere does nothing by default
        else:
            pass
    
    # Parameter change callbacks
    def _on_frequency_changed(self, value):
        self.current_config['frequency'] = float(value)
        self.update_sound_description()
    
    def _on_wave_type_changed(self, wave_type):
        self.current_config['wave_type'] = wave_type
        self.update_sound_description()
    
    def _on_duration_changed(self, value):
        self.current_config['duration'] = value
        self.update_sound_description()
    
    def _on_volume_changed(self, value):
        self.current_config['volume'] = value / 100.0
        self.update_sound_description()
    
    def _on_attack_changed(self, value):
        self.current_config['attack'] = value / 1000.0  # ms to seconds
        self.update_sound_description()
    
    def _on_decay_changed(self, value):
        self.current_config['decay'] = value / 1000.0
        self.update_sound_description()
    
    def _on_sustain_changed(self, value):
        self.current_config['sustain'] = value / 100.0
        self.update_sound_description()
    
    def _on_release_changed(self, value):
        self.current_config['release'] = value / 1000.0
        self.update_sound_description()
    
    def _on_harmonics_toggled(self, state):
        self.current_config['harmonics']['enabled'] = (state == Qt.CheckState.Checked.value)
        self.update_sound_description()
    
    def _on_octave_changed(self, value):
        self.current_config['harmonics']['octave_volume'] = value / 100.0
        self.update_sound_description()
    
    def _on_fifth_changed(self, value):
        self.current_config['harmonics']['fifth_volume'] = value / 100.0
        self.update_sound_description()
    
    def _on_subbass_changed(self, value):
        self.current_config['harmonics']['sub_bass_volume'] = value / 100.0
        self.update_sound_description()
    
    def _on_blending_toggled(self, state):
        self.current_config['blending']['enabled'] = (state == Qt.CheckState.Checked.value)
        self.update_sound_description()
    
    def _on_blend_ratio_changed(self, value):
        self.current_config['blending']['blend_ratio'] = value / 100.0
        self.update_sound_description()
    
    def _on_name_changed(self):
        self.current_config['name'] = self.name_input.text()
    
    def _on_description_changed(self):
        self.current_config['description'] = self.description_input.toPlainText()
    
    # Advanced synthesis callbacks
    def _on_advanced_toggled(self, state):
        self.current_config['advanced']['enabled'] = bool(state)
        self.update_sound_description()
    
    def _on_synth_type_changed(self, synth_type):
        self.current_config['advanced']['synthesis_type'] = synth_type
        self._update_advanced_controls_visibility()
        self.update_sound_description()
    
    def _update_advanced_controls_visibility(self):
        """Show/hide synthesis parameter groups based on selected type."""
        # Check if advanced key exists (older presets may not have it)
        if 'advanced' not in self.current_config:
            # Hide all advanced groups for presets without advanced synthesis
            self.fm_group.setVisible(False)
            self.noise_group.setVisible(False)
            return
        
        synth_type = self.current_config['advanced']['synthesis_type']
        
        # Show/hide FM parameters
        self.fm_group.setVisible(synth_type == 'fm')
        
        # Show/hide Noise parameters
        self.noise_group.setVisible(synth_type == 'noise')
        
        # Karplus-Strong has no extra parameters (just uses frequency from Basic tab)
    
    def _on_fm_ratio_changed(self, value):
        self.current_config['advanced']['fm_mod_ratio'] = value
        self.update_sound_description()
    
    def _on_fm_index_changed(self, value):
        self.current_config['advanced']['fm_mod_index'] = value
        self.update_sound_description()
    
    def _on_noise_type_changed(self, noise_type):
        self.current_config['advanced']['noise_type'] = noise_type
        self.update_sound_description()
    
    def _on_noise_filter_toggled(self, state):
        self.current_config['advanced']['noise_filter_enabled'] = bool(state)
        self.update_sound_description()
    
    def _on_noise_filter_type_changed(self, filter_type):
        self.current_config['advanced']['noise_filter_type'] = filter_type
        self.update_sound_description()
    
    def _on_filter_low_changed(self, value):
        self.current_config['advanced']['noise_filter_low'] = value
        self.update_sound_description()
    
    def _on_filter_high_changed(self, value):
        self.current_config['advanced']['noise_filter_high'] = value
        self.update_sound_description()
    
    def _on_lfo_toggled(self, state):
        self.current_config['advanced']['lfo_enabled'] = bool(state)
        self.update_sound_description()
    
    def _on_lfo_freq_changed(self, value):
        self.current_config['advanced']['lfo_frequency'] = value
        self.update_sound_description()
    
    def _on_lfo_depth_changed(self, value):
        self.current_config['advanced']['lfo_depth'] = value / 100.0
        self.update_sound_description()
    
    def _on_echo_toggled(self, state):
        self.current_config['advanced']['echo_enabled'] = bool(state)
        self.update_sound_description()
    
    def _on_echo_delay_changed(self, value):
        self.current_config['advanced']['echo_delay'] = value
        self.update_sound_description()
    
    def _on_echo_feedback_changed(self, value):
        self.current_config['advanced']['echo_feedback'] = value / 100.0
        self.update_sound_description()
    
    def update_sound_description(self):
        """Update the computed sound description."""
        config = self.current_config
        
        desc = f"<b>Sound Profile Analysis</b><br><br>"
        desc += f"<b>Base:</b> {config['frequency']:.1f} Hz {config['wave_type']} wave<br>"
        desc += f"<b>Duration:</b> {config['duration']:.2f}s at {config['volume']*100:.0f}% volume<br><br>"
        
        desc += f"<b>Envelope:</b><br>"
        desc += f"• Attack: {config['attack']*1000:.0f}ms<br>"
        desc += f"• Decay: {config['decay']*1000:.0f}ms<br>"
        desc += f"• Sustain: {config['sustain']*100:.0f}%<br>"
        desc += f"• Release: {config['release']*1000:.0f}ms<br><br>"
        
        if config['harmonics']['enabled']:
            desc += f"<b>Harmonics:</b><br>"
            if config['harmonics']['octave_volume'] > 0:
                desc += f"• Octave: {config['harmonics']['octave_volume']*100:.0f}%<br>"
            if config['harmonics']['fifth_volume'] > 0:
                desc += f"• Fifth: {config['harmonics']['fifth_volume']*100:.0f}%<br>"
            if config['harmonics']['sub_bass_volume'] > 0:
                desc += f"• Sub-bass: {config['harmonics']['sub_bass_volume']*100:.0f}%<br>"
        else:
            desc += f"<b>Harmonics:</b> Disabled<br>"
        
        desc += f"<br>"
        if config['blending']['enabled']:
            desc += f"<b>Blending:</b> {config['blending']['blend_ratio']*100:.0f}% mix<br>"
        else:
            desc += f"<b>Blending:</b> Disabled<br>"
        
        # Character assessment
        desc += f"<br><b>Character:</b> "
        if config['attack'] < 0.02:
            desc += "Percussive, "
        else:
            desc += "Smooth, "
        
        if config['harmonics']['enabled'] and config['harmonics']['octave_volume'] > 0.2:
            desc += "Bright, "
        
        if config['harmonics']['sub_bass_volume'] > 0.3:
            desc += "Heavy, "
        
        if config['blending']['enabled']:
            desc += "Warm"
        else:
            desc += "Sharp"
        
        self.sound_description.setHtml(desc)
    
    def play_current_sound(self):
        """Play the current sound configuration."""
        # Save as previous for A/B comparison
        import copy
        self.previous_config = copy.deepcopy(self.current_config)
        
        # Check if advanced synthesis is enabled
        if self.current_config['advanced']['enabled']:
            self._play_advanced_sound()
        else:
            self._play_basic_sound()
    
    def _play_basic_sound(self):
        """Play using basic waveform synthesis."""
        # Create PlayAudioConfig from current settings
        play_config = PlayAudioConfig(
            frequency=self.current_config['frequency'],
            wave_type=self.current_config['wave_type'],
            duration=self.current_config['duration'],
            volume=self.current_config['volume'],
            attack=self.current_config['attack'],
            decay=self.current_config['decay'],
            play_type=self.current_config['play_type']
        )
        
        # Configure enhanced player
        self.audio_player.set_harmonic_layering(self.current_config['harmonics']['enabled'])
        self.audio_player.set_waveform_blending(self.current_config['blending']['enabled'])
        
        # Show what we're playing
        status = f"Playing: {self.current_config['name']} - {self.current_config['frequency']:.0f}Hz {self.current_config['wave_type']}"
        print(status)
        self.statusBar().showMessage(status, 3000)
        
        # Play the sound
        self.audio_player.play_single_play(play_config, field_position=50)
    
    def _play_advanced_sound(self):
        """Play using advanced synthesis techniques."""
        import numpy as np
        import wave
        import tempfile
        import winsound
        
        config = self.current_config
        adv = config['advanced']
        sample_rate = 44100
        duration = config['duration']
        
        # Generate base sound based on synthesis type
        synth_type = adv['synthesis_type']
        freq = config['frequency']
        
        if synth_type == 'fm':
            # FM Synthesis
            carrier_freq = freq
            modulator_freq = freq * adv['fm_mod_ratio']
            audio = AdvancedSynthesis.generate_fm_synthesis(
                carrier_freq,
                modulator_freq,
                adv['fm_mod_index'],
                duration,
                sample_rate
            )
            synth_desc = f"FM (ratio={adv['fm_mod_ratio']:.1f}, index={adv['fm_mod_index']:.1f})"
            
        elif synth_type == 'noise':
            # Noise Generation
            noise_type = adv['noise_type']
            if noise_type == 'white':
                audio = AdvancedSynthesis.generate_white_noise(duration, sample_rate)
            elif noise_type == 'pink':
                audio = AdvancedSynthesis.generate_pink_noise(duration, sample_rate)
            else:  # brown
                audio = AdvancedSynthesis.generate_brown_noise(duration, sample_rate)
            
            # Apply filter if enabled
            if adv['noise_filter_enabled']:
                filter_type = adv['noise_filter_type']
                low_cutoff = adv['noise_filter_low']
                high_cutoff = adv['noise_filter_high']
                
                if filter_type == 'bandpass':
                    audio = AdvancedSynthesis.apply_bandpass_filter(audio, low_cutoff, high_cutoff, sample_rate)
                elif filter_type == 'highpass':
                    audio = AdvancedSynthesis.apply_highpass_filter(audio, low_cutoff, sample_rate)
                else:  # lowpass
                    audio = AdvancedSynthesis.apply_lowpass_filter(audio, high_cutoff, sample_rate)
            
            synth_desc = f"{noise_type.capitalize()} Noise"
            if adv['noise_filter_enabled']:
                synth_desc += f" + {adv['noise_filter_type']} filter"
        
        elif synth_type == 'karplus':
            # Karplus-Strong (plucked string)
            audio = AdvancedSynthesis.karplus_strong(freq, duration, sample_rate)
            synth_desc = "Karplus-Strong (plucked string)"
        
        # Apply LFO if enabled
        if adv['lfo_enabled']:
            audio = AdvancedSynthesis.apply_lfo(
                audio,
                adv['lfo_frequency'],
                adv['lfo_depth'],
                'tremolo',
                sample_rate
            )
            synth_desc += f" + LFO tremolo"
        
        # Apply echo if enabled
        if adv['echo_enabled']:
            audio = AdvancedSynthesis.apply_simple_echo(
                audio,
                adv['echo_delay'],
                adv['echo_feedback'],
                sample_rate
            )
            synth_desc += f" + echo"
        
        # Apply ADSR envelope
        attack = config['attack']
        decay = config['decay']
        sustain = config['sustain']
        release = config['release']
        
        attack_samples = int(attack * sample_rate)
        decay_samples = int(decay * sample_rate)
        release_samples = int(release * sample_rate)
        sustain_samples = len(audio) - attack_samples - decay_samples - release_samples
        
        if sustain_samples < 0:
            sustain_samples = 0
        
        # Create ADSR envelope
        envelope = np.concatenate([
            np.linspace(0, 1, attack_samples),  # Attack
            np.linspace(1, sustain, decay_samples),  # Decay
            np.full(sustain_samples, sustain),  # Sustain
            np.linspace(sustain, 0, release_samples)  # Release
        ])
        
        # Ensure envelope matches audio length
        if len(envelope) > len(audio):
            envelope = envelope[:len(audio)]
        elif len(envelope) < len(audio):
            audio = audio[:len(envelope)]
        
        audio = audio * envelope
        
        # Apply volume
        audio = audio * config['volume']
        
        # Normalize to prevent clipping
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val * 0.9
        
        # Convert to int16 for WAV file
        audio_int = (audio * 32767).astype(np.int16)
        
        # Show what we're playing
        status = f"Playing: {config['name']} - {synth_desc} @ {freq:.0f}Hz"
        print(status)
        self.statusBar().showMessage(status, 3000)
        
        # Write to temporary WAV file and play using winsound (same as basic player)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav', mode='wb')
        temp_filename = temp_file.name
        temp_file.close()
        
        with wave.open(temp_filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int.tobytes())
        
        # Play the audio using winsound (non-blocking)
        winsound.PlaySound(temp_filename, winsound.SND_FILENAME | winsound.SND_ASYNC)
    
    def show_current_settings(self):
        """Show current settings in a list box (Ctrl+I for Info)."""
        config = self.current_config
        
        # Create a custom dialog with a list box
        dialog = QDialog(self)
        dialog.setWindowTitle("Current Sound Settings")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        # Create list widget
        settings_list = QListWidget()
        settings_list.setAccessibleName("Sound settings list")
        settings_list.setAccessibleDescription("Current sound configuration. Use arrow keys to navigate through settings.")
        
        # Add settings as individual list items
        settings_items = [
            "=== BASIC PARAMETERS ===",
            f"Name: {config['name']}",
            f"Frequency: {config['frequency']:.0f} Hz",
            f"Waveform: {config['wave_type']}",
            f"Duration: {config['duration']:.2f} seconds",
            f"Volume: {config['volume']*100:.0f}%",
            "",
            "=== ENVELOPE (ADSR) ===",
            f"Attack: {config['attack']*1000:.0f} ms",
            f"Decay: {config['decay']*1000:.0f} ms",
            f"Sustain: {config['sustain']*100:.0f}%",
            f"Release: {config['release']*1000:.0f} ms",
            "",
            f"=== HARMONICS: {'ENABLED' if config['harmonics']['enabled'] else 'DISABLED'} ===",
            f"Octave volume: {config['harmonics']['octave_volume']*100:.0f}%",
            f"Fifth volume: {config['harmonics']['fifth_volume']*100:.0f}%",
            f"Sub-bass volume: {config['harmonics']['sub_bass_volume']*100:.0f}%",
            "",
            f"=== BLENDING: {'ENABLED' if config['blending']['enabled'] else 'DISABLED'} ===",
            f"Blend ratio: {config['blending']['blend_ratio']*100:.0f}%"
        ]
        
        for item_text in settings_items:
            item = QListWidgetItem(item_text)
            # Make header items non-selectable (visual separation)
            if item_text.startswith("===") or item_text == "":
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            settings_list.addItem(item)
        
        # Select first selectable item
        settings_list.setCurrentRow(1)  # Skip header, select "Name:"
        
        layout.addWidget(settings_list)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close settings dialog")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def compare_sounds(self):
        """Play previous sound then current sound for A/B comparison."""
        if self.previous_config is None:
            QMessageBox.information(self, "No Previous Sound", 
                                   "Play a sound first, then modify it and compare!")
            return
        
        print("A/B Comparison: Playing A (previous)...")
        
        # Play previous (A)
        prev_config = PlayAudioConfig(
            frequency=self.previous_config['frequency'],
            wave_type=self.previous_config['wave_type'],
            duration=self.previous_config['duration'],
            volume=self.previous_config['volume'],
            attack=self.previous_config['attack'],
            decay=self.previous_config['decay'],
            play_type=self.previous_config['play_type']
        )
        
        self.audio_player.set_harmonic_layering(self.previous_config['harmonics']['enabled'])
        self.audio_player.set_waveform_blending(self.previous_config['blending']['enabled'])
        self.audio_player.play_single_play(prev_config, field_position=50)
        
        # Brief pause
        QApplication.processEvents()
        import time
        time.sleep(0.3)
        
        print("Playing B (current)...")
        
        # Play current (B)
        self.play_current_sound()
    
    def new_sound(self):
        """Reset to default configuration."""
        self.current_config = self._default_config()
        self.load_config_to_ui(self.current_config)
        print("New sound created")
    
    def save_preset(self):
        """Save current configuration as preset."""
        name = self.current_config['name']
        if not name or name == "Untitled Sound":
            name = f"Preset {len(self.presets) + 1}"
            self.current_config['name'] = name
            self.name_input.setText(name)
        
        # Add to presets
        self.presets[name] = self.current_config.copy()
        self.refresh_preset_list()
        self.save_presets_to_file()
        
        print(f"Saved preset: {name}")
        QMessageBox.information(self, "Preset Saved", f"Saved '{name}' to preset library")
    
    def load_selected_preset(self):
        """Load the selected preset from list."""
        current_item = self.preset_list.currentItem()
        if current_item:
            preset_name = current_item.text().split('\n')[0]  # Get name before description
            print(f"Load button pressed - loading: {preset_name}")
            self._load_preset_by_name(preset_name)
        else:
            print("Load button pressed but no preset selected")
            QMessageBox.information(self, "No Selection", "Please select a preset from the list first.")
    
    def _preset_list_key_handler(self, event):
        """Handle key presses in preset list to prevent Space from playing global sound."""
        from PyQt6.QtGui import QKeyEvent
        if event.key() == Qt.Key.Key_Space:
            # Space should do nothing in preset list
            event.accept()
            return
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            # Enter loads the preset
            current_item = self.preset_list.currentItem()
            if current_item:
                self._on_preset_activated(current_item)
            event.accept()
            return
        # For other keys, use default behavior
        QListWidget.keyPressEvent(self.preset_list, event)
    
    def _on_preset_activated(self, item):
        """Handle preset double-click or Enter."""
        preset_name = item.text().split('\n')[0]
        self._load_preset_by_name(preset_name)
    
    def _on_preset_clicked(self, item):
        """Handle preset single click - show description."""
        preset_name = item.text().split('\n')[0]
        if preset_name in self.presets:
            preset = self.presets[preset_name]
            desc = preset.get('description', 'No description')
            item.setToolTip(desc)
    
    def _load_preset_by_name(self, preset_name):
        """Load a preset by name."""
        if preset_name in self.presets:
            # Deep copy to avoid reference issues with nested dicts
            import copy
            self.current_config = copy.deepcopy(self.presets[preset_name])
            
            # Ensure 'advanced' key exists for older presets
            if 'advanced' not in self.current_config:
                self.current_config['advanced'] = self._default_config()['advanced']
            
            self.load_config_to_ui(self.current_config)
            print(f"Loaded preset: {preset_name}")
            # Play the loaded preset automatically so user hears it
            self.play_current_sound()
        else:
            QMessageBox.warning(self, "Preset Not Found", f"Could not find preset '{preset_name}'")
    
    def quick_load_preset(self, index):
        """Load preset by number (1-9)."""
        if index < self.preset_list.count():
            item = self.preset_list.item(index)
            preset_name = item.text().split('\n')[0]
            self._load_preset_by_name(preset_name)
    
    def delete_preset(self):
        """Delete the selected preset."""
        current_item = self.preset_list.currentItem()
        if current_item:
            preset_name = current_item.text().split('\n')[0]
            reply = QMessageBox.question(self, "Delete Preset", 
                                        f"Delete preset '{preset_name}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                del self.presets[preset_name]
                self.refresh_preset_list()
                self.save_presets_to_file()
                print(f"Deleted preset: {preset_name}")
    
    def load_config_to_ui(self, config):
        """Load a configuration into the UI controls."""
        # Block signals while updating to avoid triggering callbacks
        self.name_input.blockSignals(True)
        self.description_input.blockSignals(True)
        self.wave_combo.blockSignals(True)
        self.harmonics_enabled.blockSignals(True)
        self.blending_enabled.blockSignals(True)
        
        # Update name and description
        self.name_input.setText(config['name'])
        self.description_input.setPlainText(config.get('description', ''))
        self.wave_combo.setCurrentText(config['wave_type'])
        
        # Update all spinboxes via stored control references
        if 'frequency' in self.controls:
            self.controls['frequency'].spinbox.blockSignals(True)
            self.controls['frequency'].spinbox.setValue(int(config['frequency']))
            self.controls['frequency'].spinbox.blockSignals(False)
        
        if 'duration' in self.controls:
            self.controls['duration'].spinbox.blockSignals(True)
            self.controls['duration'].spinbox.setValue(config['duration'])
            self.controls['duration'].spinbox.blockSignals(False)
        
        if 'volume' in self.controls:
            self.controls['volume'].spinbox.blockSignals(True)
            self.controls['volume'].spinbox.setValue(int(config['volume'] * 100))
            self.controls['volume'].spinbox.blockSignals(False)
        
        if 'attack' in self.controls:
            self.controls['attack'].spinbox.blockSignals(True)
            self.controls['attack'].spinbox.setValue(int(config['attack'] * 1000))
            self.controls['attack'].spinbox.blockSignals(False)
        
        if 'decay' in self.controls:
            self.controls['decay'].spinbox.blockSignals(True)
            self.controls['decay'].spinbox.setValue(int(config['decay'] * 1000))
            self.controls['decay'].spinbox.blockSignals(False)
        
        if 'sustain' in self.controls:
            self.controls['sustain'].spinbox.blockSignals(True)
            self.controls['sustain'].spinbox.setValue(int(config['sustain'] * 100))
            self.controls['sustain'].spinbox.blockSignals(False)
        
        if 'release' in self.controls:
            self.controls['release'].spinbox.blockSignals(True)
            self.controls['release'].spinbox.setValue(int(config['release'] * 1000))
            self.controls['release'].spinbox.blockSignals(False)
        
        # Update harmonics
        self.harmonics_enabled.setChecked(config['harmonics']['enabled'])
        
        if 'octave' in self.controls:
            self.controls['octave'].spinbox.blockSignals(True)
            self.controls['octave'].spinbox.setValue(int(config['harmonics']['octave_volume'] * 100))
            self.controls['octave'].spinbox.blockSignals(False)
        
        if 'fifth' in self.controls:
            self.controls['fifth'].spinbox.blockSignals(True)
            self.controls['fifth'].spinbox.setValue(int(config['harmonics']['fifth_volume'] * 100))
            self.controls['fifth'].spinbox.blockSignals(False)
        
        if 'subbass' in self.controls:
            self.controls['subbass'].spinbox.blockSignals(True)
            self.controls['subbass'].spinbox.setValue(int(config['harmonics']['sub_bass_volume'] * 100))
            self.controls['subbass'].spinbox.blockSignals(False)
        
        # Update blending
        self.blending_enabled.setChecked(config['blending']['enabled'])
        
        if 'blend_ratio' in self.controls:
            self.controls['blend_ratio'].spinbox.blockSignals(True)
            self.controls['blend_ratio'].spinbox.setValue(int(config['blending']['blend_ratio'] * 100))
            self.controls['blend_ratio'].spinbox.blockSignals(False)
        
        # Update advanced synthesis
        if 'advanced' in config:
            adv = config['advanced']
            
            self.advanced_enabled.blockSignals(True)
            self.advanced_enabled.setChecked(adv.get('enabled', False))
            self.advanced_enabled.blockSignals(False)
            
            self.synth_type_combo.blockSignals(True)
            self.synth_type_combo.setCurrentText(adv.get('synthesis_type', 'fm'))
            self.synth_type_combo.blockSignals(False)
            
            # FM parameters
            if 'fm_ratio' in self.controls:
                self.controls['fm_ratio'].spinbox.blockSignals(True)
                self.controls['fm_ratio'].spinbox.setValue(adv.get('fm_mod_ratio', 1.4))
                self.controls['fm_ratio'].spinbox.blockSignals(False)
            
            if 'fm_index' in self.controls:
                self.controls['fm_index'].spinbox.blockSignals(True)
                self.controls['fm_index'].spinbox.setValue(adv.get('fm_mod_index', 5.0))
                self.controls['fm_index'].spinbox.blockSignals(False)
            
            # Noise parameters
            self.noise_type_combo.blockSignals(True)
            self.noise_type_combo.setCurrentText(adv.get('noise_type', 'white'))
            self.noise_type_combo.blockSignals(False)
            
            self.noise_filter_enabled.blockSignals(True)
            self.noise_filter_enabled.setChecked(adv.get('noise_filter_enabled', False))
            self.noise_filter_enabled.blockSignals(False)
            
            self.noise_filter_combo.blockSignals(True)
            self.noise_filter_combo.setCurrentText(adv.get('noise_filter_type', 'bandpass'))
            self.noise_filter_combo.blockSignals(False)
            
            if 'filter_low' in self.controls:
                self.controls['filter_low'].spinbox.blockSignals(True)
                self.controls['filter_low'].spinbox.setValue(adv.get('noise_filter_low', 2000))
                self.controls['filter_low'].spinbox.blockSignals(False)
            
            if 'filter_high' in self.controls:
                self.controls['filter_high'].spinbox.blockSignals(True)
                self.controls['filter_high'].spinbox.setValue(adv.get('noise_filter_high', 8000))
                self.controls['filter_high'].spinbox.blockSignals(False)
            
            # LFO parameters
            self.lfo_enabled.blockSignals(True)
            self.lfo_enabled.setChecked(adv.get('lfo_enabled', False))
            self.lfo_enabled.blockSignals(False)
            
            if 'lfo_freq' in self.controls:
                self.controls['lfo_freq'].spinbox.blockSignals(True)
                self.controls['lfo_freq'].spinbox.setValue(adv.get('lfo_frequency', 5.0))
                self.controls['lfo_freq'].spinbox.blockSignals(False)
            
            if 'lfo_depth' in self.controls:
                self.controls['lfo_depth'].spinbox.blockSignals(True)
                self.controls['lfo_depth'].spinbox.setValue(int(adv.get('lfo_depth', 0.3) * 100))
                self.controls['lfo_depth'].spinbox.blockSignals(False)
            
            # Echo parameters
            self.echo_enabled.blockSignals(True)
            self.echo_enabled.setChecked(adv.get('echo_enabled', False))
            self.echo_enabled.blockSignals(False)
            
            if 'echo_delay' in self.controls:
                self.controls['echo_delay'].spinbox.blockSignals(True)
                self.controls['echo_delay'].spinbox.setValue(adv.get('echo_delay', 0.3))
                self.controls['echo_delay'].spinbox.blockSignals(False)
            
            if 'echo_feedback' in self.controls:
                self.controls['echo_feedback'].spinbox.blockSignals(True)
                self.controls['echo_feedback'].spinbox.setValue(int(adv.get('echo_feedback', 0.4) * 100))
                self.controls['echo_feedback'].spinbox.blockSignals(False)
        
        # Unblock signals
        self.name_input.blockSignals(False)
        self.description_input.blockSignals(False)
        self.wave_combo.blockSignals(False)
        self.harmonics_enabled.blockSignals(False)
        self.blending_enabled.blockSignals(False)
        
        # Update advanced controls visibility based on loaded synthesis type
        self._update_advanced_controls_visibility()
        
        # Update the display
        self.update_sound_description()
        
        print(f"Loaded config: {config['name']} - Freq: {config['frequency']}Hz, Wave: {config['wave_type']}")
    
    def refresh_preset_list(self):
        """Refresh the preset list widget."""
        self.preset_list.clear()
        for idx, (name, preset) in enumerate(self.presets.items()):
            desc = preset.get('description', '')
            short_desc = desc[:50] + "..." if len(desc) > 50 else desc
            item_text = f"{name}\n   {short_desc}" if short_desc else name
            item = QListWidgetItem(item_text)
            # Set accessible name for screen reader
            freq = preset.get('frequency', 0)
            wave = preset.get('wave_type', 'sine')
            accessible_text = f"Preset {idx+1}: {name}. {freq:.0f} hertz {wave} wave. {desc}"
            item.setData(Qt.ItemDataRole.AccessibleTextRole, accessible_text)
            self.preset_list.addItem(item)
    
    def save_presets_to_file(self):
        """Save presets to JSON file."""
        try:
            with open(self.preset_file, 'w') as f:
                json.dump(self.presets, f, indent=2)
            print(f"Saved {len(self.presets)} presets to {self.preset_file}")
        except Exception as e:
            print(f"Error saving presets: {e}")
    
    def load_presets_from_file(self):
        """Load presets from JSON file."""
        if self.preset_file.exists():
            try:
                with open(self.preset_file, 'r') as f:
                    loaded = json.load(f)
                    self.presets.update(loaded)
                print(f"Loaded {len(loaded)} presets from {self.preset_file}")
                self.refresh_preset_list()
            except Exception as e:
                print(f"Error loading presets: {e}")
    
    def export_presets(self):
        """Export presets to a user-chosen file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Presets", "", "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.presets, f, indent=2)
                QMessageBox.information(self, "Export Successful", 
                                       f"Exported {len(self.presets)} presets to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Error: {e}")
    
    def import_presets(self):
        """Import presets from a user-chosen file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Presets", "", "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    imported = json.load(f)
                self.presets.update(imported)
                self.refresh_preset_list()
                self.save_presets_to_file()
                QMessageBox.information(self, "Import Successful", 
                                       f"Imported {len(imported)} presets")
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Error: {e}")
    
    def _load_default_presets(self):
        """Create some default example presets."""
        return {
            "Gentle Bell": {
                'frequency': 523.25,
                'wave_type': 'sine',
                'duration': 1.0,
                'volume': 0.25,
                'attack': 0.005,
                'decay': 0.3,
                'sustain': 0.4,
                'release': 0.5,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.2,
                    'fifth_volume': 0.15,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': True, 'blend_ratio': 0.5},
                'name': 'Gentle Bell',
                'description': 'Soft bell-like tone with smooth envelope',
                'play_type': 'custom'
            },
            "Power Bass": {
                'frequency': 110.0,
                'wave_type': 'square',
                'duration': 0.6,
                'volume': 0.35,
                'attack': 0.02,
                'decay': 0.1,
                'sustain': 0.8,
                'release': 0.2,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.25,
                    'fifth_volume': 0.1,
                    'sub_bass_volume': 0.5
                },
                'blending': {'enabled': True, 'blend_ratio': 0.7},
                'name': 'Power Bass',
                'description': 'Heavy bass with sub-harmonics for impact',
                'play_type': 'custom'
            },
            "Bright Pluck": {
                'frequency': 660.0,
                'wave_type': 'sawtooth',
                'duration': 0.3,
                'volume': 0.3,
                'attack': 0.001,
                'decay': 0.15,
                'sustain': 0.2,
                'release': 0.1,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.4,
                    'fifth_volume': 0.3,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': True, 'blend_ratio': 0.3},
                'name': 'Bright Pluck',
                'description': 'Percussive plucked sound with harmonics',
                'play_type': 'custom'
            },
            "Warm Pad": {
                'frequency': 220.0,
                'wave_type': 'triangle',
                'duration': 2.0,
                'volume': 0.2,
                'attack': 0.3,
                'decay': 0.2,
                'sustain': 0.7,
                'release': 0.8,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.15,
                    'fifth_volume': 0.25,
                    'sub_bass_volume': 0.2
                },
                'blending': {'enabled': True, 'blend_ratio': 0.6},
                'name': 'Warm Pad',
                'description': 'Slow, evolving ambient pad sound',
                'play_type': 'custom'
            },
            "Laser Zap": {
                'frequency': 1500.0,
                'wave_type': 'sawtooth',
                'duration': 0.15,
                'volume': 0.3,
                'attack': 0.001,
                'decay': 0.05,
                'sustain': 0.3,
                'release': 0.08,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.5,
                    'fifth_volume': 0.0,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': False, 'blend_ratio': 0.0},
                'name': 'Laser Zap',
                'description': 'Sharp, bright sci-fi laser sound',
                'play_type': 'custom'
            },
            "Deep Rumble": {
                'frequency': 55.0,
                'wave_type': 'sine',
                'duration': 1.5,
                'volume': 0.4,
                'attack': 0.1,
                'decay': 0.3,
                'sustain': 0.6,
                'release': 0.4,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.15,
                    'fifth_volume': 0.0,
                    'sub_bass_volume': 0.6
                },
                'blending': {'enabled': True, 'blend_ratio': 0.5},
                'name': 'Deep Rumble',
                'description': 'Very low frequency rumble with sub-bass',
                'play_type': 'custom'
            },
            "Kick Drum": {
                'frequency': 60.0,
                'wave_type': 'sine',
                'duration': 0.3,
                'volume': 0.4,
                'attack': 0.001,
                'decay': 0.15,
                'sustain': 0.1,
                'release': 0.08,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.1,
                    'fifth_volume': 0.0,
                    'sub_bass_volume': 0.7
                },
                'blending': {'enabled': True, 'blend_ratio': 0.3},
                'name': 'Kick Drum',
                'description': 'Punchy low-frequency percussion',
                'play_type': 'custom'
            },
            "Snare Hit": {
                'frequency': 200.0,
                'wave_type': 'square',
                'duration': 0.12,
                'volume': 0.35,
                'attack': 0.001,
                'decay': 0.08,
                'sustain': 0.0,
                'release': 0.03,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.6,
                    'fifth_volume': 0.4,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': False, 'blend_ratio': 0.0},
                'name': 'Snare Hit',
                'description': 'Sharp, bright percussion hit',
                'play_type': 'custom'
            },
            "Whoosh": {
                'frequency': 800.0,
                'wave_type': 'sawtooth',
                'duration': 0.6,
                'volume': 0.25,
                'attack': 0.001,
                'decay': 0.5,
                'sustain': 0.0,
                'release': 0.05,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.35,
                    'fifth_volume': 0.25,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': True, 'blend_ratio': 0.4},
                'name': 'Whoosh',
                'description': 'Sweeping transitional sound effect',
                'play_type': 'custom'
            },
            "Retro Beep": {
                'frequency': 880.0,
                'wave_type': 'square',
                'duration': 0.08,
                'volume': 0.3,
                'attack': 0.001,
                'decay': 0.02,
                'sustain': 0.5,
                'release': 0.04,
                'harmonics': {
                    'enabled': False,
                    'octave_volume': 0.0,
                    'fifth_volume': 0.0,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': False, 'blend_ratio': 0.0},
                'name': 'Retro Beep',
                'description': 'Classic 8-bit game notification sound',
                'play_type': 'custom'
            },
            "Soft Chime": {
                'frequency': 1046.5,
                'wave_type': 'sine',
                'duration': 1.2,
                'volume': 0.2,
                'attack': 0.01,
                'decay': 0.4,
                'sustain': 0.3,
                'release': 0.6,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.25,
                    'fifth_volume': 0.35,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': True, 'blend_ratio': 0.5},
                'name': 'Soft Chime',
                'description': 'Delicate high-pitched chime',
                'play_type': 'custom'
            },
            "Wind Synth": {
                'frequency': 293.66,
                'wave_type': 'sine',
                'duration': 1.0,
                'volume': 0.25,
                'attack': 0.08,
                'decay': 0.15,
                'sustain': 0.6,
                'release': 0.25,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.15,
                    'fifth_volume': 0.3,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': True, 'blend_ratio': 0.5},
                'name': 'Wind Synth',
                'description': 'Breathy wind instrument sound',
                'play_type': 'custom'
            },
            "Electric Pop": {
                'frequency': 440.0,
                'wave_type': 'triangle',
                'duration': 0.15,
                'volume': 0.35,
                'attack': 0.001,
                'decay': 0.1,
                'sustain': 0.0,
                'release': 0.03,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.4,
                    'fifth_volume': 0.2,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': True, 'blend_ratio': 0.3},
                'name': 'Electric Pop',
                'description': 'Quick electric pop or click',
                'play_type': 'custom'
            },
            "Hollow Knock": {
                'frequency': 150.0,
                'wave_type': 'triangle',
                'duration': 0.25,
                'volume': 0.3,
                'attack': 0.001,
                'decay': 0.15,
                'sustain': 0.1,
                'release': 0.08,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.2,
                    'fifth_volume': 0.15,
                    'sub_bass_volume': 0.3
                },
                'blending': {'enabled': True, 'blend_ratio': 0.6},
                'name': 'Hollow Knock',
                'description': 'Wooden or hollow percussion',
                'play_type': 'custom'
            },
            "String Pluck": {
                'frequency': 196.0,
                'wave_type': 'sawtooth',
                'duration': 0.8,
                'volume': 0.28,
                'attack': 0.002,
                'decay': 0.3,
                'sustain': 0.4,
                'release': 0.15,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.3,
                    'fifth_volume': 0.4,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': True, 'blend_ratio': 0.5},
                'name': 'String Pluck',
                'description': 'Plucked string instrument',
                'play_type': 'custom'
            },
            "Glass Chime": {
                'frequency': 1760.0,
                'wave_type': 'sine',
                'duration': 2.0,
                'volume': 0.15,
                'attack': 0.001,
                'decay': 0.8,
                'sustain': 0.2,
                'release': 1.0,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.3,
                    'fifth_volume': 0.5,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': True, 'blend_ratio': 0.3},
                'name': 'Glass Chime',
                'description': 'Delicate high-pitched glass-like tone',
                'play_type': 'custom'
            },
            "Dark Pad": {
                'frequency': 82.4,
                'wave_type': 'triangle',
                'duration': 3.0,
                'volume': 0.25,
                'attack': 0.5,
                'decay': 0.3,
                'sustain': 0.8,
                'release': 1.2,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.2,
                    'fifth_volume': 0.15,
                    'sub_bass_volume': 0.3
                },
                'blending': {'enabled': True, 'blend_ratio': 0.7},
                'name': 'Dark Pad',
                'description': 'Deep, mysterious ambient pad',
                'play_type': 'custom'
            },
            "Metallic Clang": {
                'frequency': 350.0,
                'wave_type': 'square',
                'duration': 0.4,
                'volume': 0.3,
                'attack': 0.001,
                'decay': 0.25,
                'sustain': 0.1,
                'release': 0.1,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.6,
                    'fifth_volume': 0.5,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': False, 'blend_ratio': 0.0},
                'name': 'Metallic Clang',
                'description': 'Sharp metallic percussion',
                'play_type': 'custom'
            },
            "Soft Tom": {
                'frequency': 120.0,
                'wave_type': 'sine',
                'duration': 0.5,
                'volume': 0.35,
                'attack': 0.005,
                'decay': 0.3,
                'sustain': 0.2,
                'release': 0.15,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.15,
                    'fifth_volume': 0.0,
                    'sub_bass_volume': 0.4
                },
                'blending': {'enabled': True, 'blend_ratio': 0.5},
                'name': 'Soft Tom',
                'description': 'Mellow tom drum sound',
                'play_type': 'custom'
            },
            "Bright Lead": {
                'frequency': 880.0,
                'wave_type': 'sawtooth',
                'duration': 0.6,
                'volume': 0.28,
                'attack': 0.01,
                'decay': 0.08,
                'sustain': 0.7,
                'release': 0.12,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.5,
                    'fifth_volume': 0.3,
                    'sub_bass_volume': 0.0
                },
                'blending': {'enabled': True, 'blend_ratio': 0.3},
                'name': 'Bright Lead',
                'description': 'Cutting lead synth sound',
                'play_type': 'custom'
            },
            "Underwater": {
                'frequency': 65.4,
                'wave_type': 'sine',
                'duration': 2.5,
                'volume': 0.2,
                'attack': 0.8,
                'decay': 0.5,
                'sustain': 0.6,
                'release': 1.0,
                'harmonics': {
                    'enabled': True,
                    'octave_volume': 0.1,
                    'fifth_volume': 0.2,
                    'sub_bass_volume': 0.5
                },
                'blending': {'enabled': True, 'blend_ratio': 0.6},
                'name': 'Underwater',
                'description': 'Deep submerged ambient tone',
                'play_type': 'custom'
            }
        }
    
    def closeEvent(self, event):
        """Save presets on close."""
        self.save_presets_to_file()
        self.audio_player.cleanup()
        event.accept()


def main():
    """Launch the Sound Design Studio."""
    app = QApplication(sys.argv)
    studio = SoundDesignStudio()
    studio.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
