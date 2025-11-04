"""
Sound Configuration Export System
Allows exporting sound designs from the studio for use in the main Scores app.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class SoundConfigExporter:
    """Export and import sound configurations."""
    
    # Standard export location
    EXPORT_DIR = Path("exported_sounds")
    
    # Categories for organizing sounds
    CATEGORIES = [
        "Football Plays",
        "Baseball Events", 
        "UI Feedback",
        "Notifications",
        "Transitions",
        "Celebrations",
        "Warnings",
        "Ambient",
        "Custom"
    ]
    
    @classmethod
    def export_for_app(cls, config: Dict, category: str = "Custom", 
                      notes: str = "") -> str:
        """
        Export a sound configuration for use in the Scores app.
        
        Args:
            config: Sound configuration dictionary
            category: Category (e.g., "Football Plays")
            notes: Usage notes for developers
            
        Returns:
            Path to exported file
        """
        cls.EXPORT_DIR.mkdir(exist_ok=True)
        
        # Create export data with metadata
        export_data = {
            "sound_config": config,
            "metadata": {
                "name": config.get('name', 'Untitled'),
                "description": config.get('description', ''),
                "category": category,
                "usage_notes": notes,
                "exported_from": "Sound Design Studio",
                "version": "1.0"
            },
            "usage_example": cls._generate_usage_example(config)
        }
        
        # Generate filename
        safe_name = "".join(c for c in config['name'] if c.isalnum() or c in (' ', '-', '_'))
        filename = f"{safe_name.replace(' ', '_')}.sound.json"
        filepath = cls.EXPORT_DIR / filename
        
        # Save
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Exported sound to: {filepath}")
        print(f"📁 Category: {category}")
        print(f"📝 Usage notes: {notes}")
        
        return str(filepath)
    
    @classmethod
    def export_preset_collection(cls, presets: Dict, collection_name: str) -> str:
        """
        Export multiple presets as a collection.
        
        Args:
            presets: Dictionary of preset name -> config
            collection_name: Name for the collection
            
        Returns:
            Path to exported collection file
        """
        cls.EXPORT_DIR.mkdir(exist_ok=True)
        
        collection_data = {
            "collection_name": collection_name,
            "presets": presets,
            "count": len(presets),
            "version": "1.0"
        }
        
        filename = f"{collection_name.replace(' ', '_')}_collection.json"
        filepath = cls.EXPORT_DIR / filename
        
        with open(filepath, 'w') as f:
            json.dump(collection_data, f, indent=2)
        
        print(f"✅ Exported {len(presets)} sounds to: {filepath}")
        
        return str(filepath)
    
    @classmethod
    def _generate_usage_example(cls, config: Dict) -> str:
        """Generate Python code example for using the sound."""
        return f"""
# Usage example in Scores app:

from enhanced_audio_player import EnhancedAudioPlayer
from football_audio_mapper import PlayAudioConfig
import json

# Load sound configuration
with open('exported_sounds/{config['name'].replace(' ', '_')}.sound.json') as f:
    sound_data = json.load(f)
    sound_config = sound_data['sound_config']

# Create audio config
audio_config = PlayAudioConfig(
    frequency=sound_config['frequency'],
    wave_type=sound_config['wave_type'],
    duration=sound_config['duration'],
    volume=sound_config['volume'],
    attack=sound_config['attack'],
    decay=sound_config['decay'],
    play_type=sound_config.get('play_type', 'custom')
)

# Play the sound
player = EnhancedAudioPlayer()
player.set_harmonic_layering(sound_config['harmonics']['enabled'])
player.set_waveform_blending(sound_config['blending']['enabled'])
player.play_single_play(audio_config, field_position=50)
"""
    
    @classmethod
    def generate_integration_guide(cls, export_path: str, use_case: str) -> str:
        """
        Generate detailed integration instructions.
        
        Args:
            export_path: Path to the exported sound file
            use_case: Description of how to use (e.g., "Touchdown celebration")
            
        Returns:
            Integration guide text
        """
        guide = f"""
# Sound Integration Guide
## Exported Sound: {Path(export_path).stem}

### Use Case
{use_case}

### Integration Steps

1. **Copy the exported file** to your project:
   ```
   exported_sounds/{Path(export_path).name}
   ```

2. **Load in your code**:
   ```python
   import json
   from pathlib import Path
   
   sound_file = Path('exported_sounds/{Path(export_path).name}')
   with open(sound_file) as f:
       sound_data = json.load(f)
   ```

3. **Create audio player** (if not already done):
   ```python
   from enhanced_audio_player import EnhancedAudioPlayer
   player = EnhancedAudioPlayer()
   ```

4. **Configure player** with sound settings:
   ```python
   config = sound_data['sound_config']
   player.set_harmonic_layering(config['harmonics']['enabled'])
   player.set_waveform_blending(config['blending']['enabled'])
   ```

5. **Play the sound**:
   ```python
   from football_audio_mapper import PlayAudioConfig
   
   audio_config = PlayAudioConfig(
       frequency=config['frequency'],
       wave_type=config['wave_type'],
       duration=config['duration'],
       volume=config['volume'],
       attack=config['attack'],
       decay=config['decay']
   )
   
   player.play_single_play(audio_config)
   ```

### Quick Reference
- **Name**: {use_case}
- **File**: {Path(export_path).name}
- **Ready to use**: Yes
- **Dependencies**: enhanced_audio_player.py, football_audio_mapper.py

### Customization
To tweak the sound:
1. Open the .sound.json file
2. Modify parameters (frequency, duration, volume, etc.)
3. Save and reload in your app

No need to regenerate - just edit the JSON!
"""
        return guide


class SoundLibrary:
    """Manage a library of sound configurations for the app."""
    
    LIBRARY_FILE = Path("sound_library.json")
    
    @classmethod
    def add_to_library(cls, config: Dict, category: str, tags: List[str] = None):
        """Add a sound to the app's sound library."""
        library = cls.load_library()
        
        sound_entry = {
            "name": config['name'],
            "config": config,
            "category": category,
            "tags": tags or [],
            "description": config.get('description', '')
        }
        
        # Use name as key
        library[config['name']] = sound_entry
        
        cls.save_library(library)
        print(f"✅ Added '{config['name']}' to sound library")
        print(f"   Category: {category}")
        print(f"   Tags: {', '.join(tags or [])}")
    
    @classmethod
    def load_library(cls) -> Dict:
        """Load the sound library."""
        if cls.LIBRARY_FILE.exists():
            with open(cls.LIBRARY_FILE) as f:
                return json.load(f)
        return {}
    
    @classmethod
    def save_library(cls, library: Dict):
        """Save the sound library."""
        with open(cls.LIBRARY_FILE, 'w') as f:
            json.dump(library, f, indent=2)
    
    @classmethod
    def search_library(cls, query: str = "", category: str = "", 
                      tags: List[str] = None) -> Dict:
        """Search the sound library."""
        library = cls.load_library()
        results = {}
        
        for name, entry in library.items():
            # Check query
            if query and query.lower() not in name.lower() and \
               query.lower() not in entry.get('description', '').lower():
                continue
            
            # Check category
            if category and entry.get('category') != category:
                continue
            
            # Check tags
            if tags and not any(tag in entry.get('tags', []) for tag in tags):
                continue
            
            results[name] = entry
        
        return results
    
    @classmethod
    def list_categories(cls) -> Dict[str, int]:
        """List categories and count of sounds in each."""
        library = cls.load_library()
        categories = {}
        
        for entry in library.values():
            cat = entry.get('category', 'Uncategorized')
            categories[cat] = categories.get(cat, 0) + 1
        
        return categories
