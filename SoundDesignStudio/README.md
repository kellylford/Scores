# Sound Design Studio

A professional sound synthesis and design tool for creating custom audio for the Scores application.

## Files in This Directory

### Main Application
- **sound_design_studio.py** - Main GUI application for designing sounds
- **run_studio.bat** - Launcher script (double-click to run)

### Core Modules
- **advanced_synthesis.py** - Advanced synthesis techniques (FM, noise, filters, LFO, echo, PWM, Karplus-Strong)
- **sound_export_system.py** - Export/import system for sound configurations
- **export_dialog.py** - User-friendly export dialog

### Dependencies (in parent directory)
- **enhanced_audio_player.py** - Enhanced audio playback engine
- **football_audio_mapper.py** - Audio mapping for football plays

## Features

### Sound Synthesis
- **Basic Waveforms**: Sine, square, sawtooth, triangle
- **ADSR Envelope**: Full attack, decay, sustain, release control
- **Harmonic Layering**: Octave, fifth, and sub-bass harmonics
- **Waveform Blending**: Mix multiple waveforms for warmth

### Advanced Synthesis (Coming Soon)
- **FM Synthesis**: Create bells, electric pianos, brass sounds
- **Noise Generation**: White, pink, brown noise for percussion and atmospheres
- **Filters**: Bandpass, highpass, lowpass filtering
- **Effects**: LFO tremolo, echo/delay, ring modulation
- **Physical Modeling**: Karplus-Strong string synthesis

### Accessibility
- **Full Keyboard Navigation**: All controls accessible via keyboard
- **Screen Reader Support**: Proper ARIA labels and announcements
- **Keyboard Shortcuts**:
  - Alt+P: Play current sound
  - Ctrl+S: Save preset
  - Ctrl+L: Load preset
  - Ctrl+N: New preset
  - Ctrl+I: Show info
  - Delete: Delete preset
  - 1-9: Quick load presets 1-9

### Presets
22 built-in presets including:
- Gentle Bell, Power Bass, Bright Pluck
- Warm Pad, Laser Zap, Deep Rumble
- Kick Drum, Snare Hit, Whoosh
- And many more...

### Export System
- **Sound Library**: Export sounds to a central library for app integration
- **File Export**: Export individual sounds or collections as JSON
- **Integration Guides**: Auto-generated documentation for using sounds in the main app
- **Categories**: Organize sounds by purpose (Football Plays, Baseball Events, UI Feedback, etc.)

## Usage

### Running the Studio
1. Double-click `run_studio.bat`, or
2. Run from command line: `python sound_design_studio.py`

### Creating Sounds
1. Adjust frequency, wave type, duration, volume
2. Fine-tune ADSR envelope for shape
3. Enable harmonics for richness
4. Enable blending for warmth
5. Press Alt+P to play and hear your creation

### Exporting Sounds
1. Create your sound
2. Click "Export" button (coming soon)
3. Choose category and add usage notes
4. Export to library or file
5. Use in the main Scores application

### Loading Presets
- Click a preset in the list and press Enter
- Use quick load shortcuts (1-9 keys)
- Modify preset parameters to create variations

## Integration with Scores App

Sounds created in the studio can be exported and used in the main application:

```python
from sound_export_system import SoundLibrary

# Load your custom sound
library = SoundLibrary.load_library()
custom_sound = library['My Custom Sound']

# Use in the app
from enhanced_audio_player import EnhancedAudioPlayer
player = EnhancedAudioPlayer()
# ... configure and play
```

See the auto-generated integration guides for detailed instructions.

## Technical Details

### Audio Generation
- Pure Python synthesis using NumPy
- Sample rate: 44.1 kHz
- 16-bit audio output
- No external audio files required

### Platform Support
- Windows (tested)
- Linux (should work)
- macOS (should work)

### Requirements
- Python 3.8+
- PyQt6 6.9.1+
- NumPy 2.1.3+
- sounddevice (for audio playback)

## Development

### Adding New Features
1. Synthesis techniques go in `advanced_synthesis.py`
2. GUI controls go in `sound_design_studio.py`
3. Export functionality goes in `sound_export_system.py` or `export_dialog.py`

### Testing
Test audio quality:
```bash
python test_audio_quality.py
```

### Future Enhancements
- [ ] Integrate advanced synthesis into GUI
- [ ] Add spectral analyzer visualization
- [ ] Add waveform display
- [ ] Add more presets
- [ ] Add preset categories
- [ ] Add undo/redo functionality
- [ ] Add copy/paste parameters

## Support

For questions or issues, refer to the main Scores application documentation.

## License

Same as parent Scores application (see LICENSE in parent directory).
