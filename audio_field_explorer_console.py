"""
Console-based Interactive Audio Field Position Explorer

Test different field position and audio configurations for football audio.
Rate each configuration to find optimal settings.
"""

import json
import os
from datetime import datetime

# Import our audio system
from audio_player import AudioPlayer
from football_audio_mapper import PlayAudioConfig


class ConsoleAudioExplorer:
    def __init__(self):
        self.audio_player = AudioPlayer()
        self.log_file = "audio_experiments.log"
        self.current_config = {}
        
        # Default settings
        self.settings = {
            'yards_to_endzone': 65,
            'yards_gained': 8,
            'stereo_multiplier': 2.0,
            'play_type': 'Rush - Medium Gain',
            'base_frequency': 440,
            'duration': 0.2,
            'volume': 0.7
        }
        
        self.play_types = [
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
        ]
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_calculations(self):
        """Display calculated field positions"""
        yards_to_endzone = self.settings['yards_to_endzone']
        yards_gained = self.settings['yards_gained']
        multiplier = self.settings['stereo_multiplier']
        
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
        
        print("\n" + "="*70)
        print("CALCULATED FIELD POSITIONS:")
        print("="*70)
        print(f"Start: {yards_to_endzone} yards to endzone")
        print(f"       Raw position: {raw_position}")
        print(f"       Enhanced (x{multiplier}): {clamped_position:.1f} → {get_stereo_desc(clamped_position)}")
        print(f"\nGain:  {yards_gained:+d} yards")
        print(f"\nEnd:   {end_yards_to_endzone} yards to endzone")
        print(f"       Raw position: {end_raw_position}")
        print(f"       Enhanced (x{multiplier}): {end_clamped_position:.1f} → {get_stereo_desc(end_clamped_position)}")
        print("="*70)
        
    def display_menu(self):
        """Display the main menu"""
        self.clear_screen()
        print("="*70)
        print("FOOTBALL AUDIO FIELD POSITION EXPLORER")
        print("="*70)
        
        print("\nCURRENT SETTINGS:")
        print("-"*70)
        print(f"1. Yards to Endzone (0-100):     {self.settings['yards_to_endzone']}")
        print(f"2. Yards Gained (-20 to 99):     {self.settings['yards_gained']}")
        print(f"3. Stereo Multiplier (0.5-5.0):  {self.settings['stereo_multiplier']:.1f}")
        print(f"4. Play Type:                     {self.settings['play_type']}")
        print(f"5. Base Frequency (200-800 Hz):  {self.settings['base_frequency']}")
        print(f"6. Duration (0.1-2.0 sec):       {self.settings['duration']:.1f}")
        print(f"7. Volume (0.1-1.0):             {self.settings['volume']:.1f}")
        
        self.display_calculations()
        
        print("\nACTIONS:")
        print("-"*70)
        print("P - Play audio with current settings")
        print("Y - Mark last played config as LIKED")
        print("N - Mark last played config as DISLIKED")
        print("L - View experiment log")
        print("Q - Quit")
        print("1-7 - Change a setting")
        print("="*70)
        
    def get_input(self, prompt, value_type='int', min_val=None, max_val=None, default=None):
        """Get validated input from user"""
        while True:
            try:
                value_str = input(f"{prompt} (current: {default}): ").strip()
                if not value_str and default is not None:
                    return default
                    
                if value_type == 'int':
                    value = int(value_str)
                elif value_type == 'float':
                    value = float(value_str)
                else:
                    return value_str
                    
                if min_val is not None and value < min_val:
                    print(f"Value must be at least {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Value must be at most {max_val}")
                    continue
                    
                return value
            except ValueError:
                print(f"Invalid input. Please enter a valid {value_type}")
                
    def change_setting(self, setting_num):
        """Change a specific setting"""
        if setting_num == 1:
            self.settings['yards_to_endzone'] = self.get_input(
                "Enter yards to endzone", 'int', 0, 100, 
                self.settings['yards_to_endzone']
            )
        elif setting_num == 2:
            self.settings['yards_gained'] = self.get_input(
                "Enter yards gained", 'int', -20, 99,
                self.settings['yards_gained']
            )
        elif setting_num == 3:
            self.settings['stereo_multiplier'] = self.get_input(
                "Enter stereo multiplier", 'float', 0.5, 5.0,
                self.settings['stereo_multiplier']
            )
        elif setting_num == 4:
            print("\nPlay Types:")
            for i, pt in enumerate(self.play_types, 1):
                print(f"{i}. {pt}")
            choice = self.get_input("Select play type", 'int', 1, len(self.play_types), 1)
            self.settings['play_type'] = self.play_types[choice - 1]
        elif setting_num == 5:
            self.settings['base_frequency'] = self.get_input(
                "Enter base frequency (Hz)", 'int', 200, 800,
                self.settings['base_frequency']
            )
        elif setting_num == 6:
            self.settings['duration'] = self.get_input(
                "Enter duration (seconds)", 'float', 0.1, 2.0,
                self.settings['duration']
            )
        elif setting_num == 7:
            self.settings['volume'] = self.get_input(
                "Enter volume", 'float', 0.1, 1.0,
                self.settings['volume']
            )
            
    def play_audio(self):
        """Generate and play audio with current settings"""
        print("\n>> Playing audio...")
        
        # Get all settings
        yards_to_endzone = self.settings['yards_to_endzone']
        multiplier = self.settings['stereo_multiplier']
        
        # Calculate field position
        raw_position = 100 - yards_to_endzone
        enhanced_position = (raw_position - 50) * multiplier + 50
        field_position = max(0, min(100, enhanced_position))
        
        # Create audio config
        config = PlayAudioConfig(
            frequency=self.settings['base_frequency'],
            duration=self.settings['duration'],
            volume=self.settings['volume'],
            wave_type='sine',
            attack=0.05,
            decay=0.05,
            field_position=field_position
        )
        
        # Store config for rating
        self.current_config = {
            'timestamp': datetime.now().isoformat(),
            'yards_to_endzone': yards_to_endzone,
            'yards_gained': self.settings['yards_gained'],
            'stereo_multiplier': multiplier,
            'play_type': self.settings['play_type'],
            'base_frequency': self.settings['base_frequency'],
            'duration': self.settings['duration'],
            'volume': self.settings['volume'],
            'raw_position': raw_position,
            'enhanced_position': enhanced_position,
            'field_position': field_position
        }
        
        # Play the audio - pass field_position as separate parameter
        print(f">> Field position for audio: {field_position:.1f}")
        self.audio_player.play_audio_sequence([config], silence_between=0, field_positions=[field_position])
        
        print(f">> Played! Field position: {field_position:.1f}")
        input("\nPress Enter to continue...")
        
    def record_rating(self, rating):
        """Record the rating for the current config"""
        if not self.current_config:
            print("\n>> No audio has been played yet!")
            input("Press Enter to continue...")
            return
            
        self.current_config['rating'] = rating
        
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write("\n" + "="*80 + "\n")
            f.write(json.dumps(self.current_config, indent=2))
            f.write("\n")
        
        if rating == "LIKED":
            print(f"\n>> ✓ Marked as LIKED and logged to {self.log_file}!")
        else:
            print(f"\n>> ✗ Marked as DISLIKED and logged to {self.log_file}!")
            
        input("Press Enter to continue...")
        
    def view_log(self):
        """Display the experiment log"""
        self.clear_screen()
        print("="*70)
        print("EXPERIMENT LOG")
        print("="*70)
        
        try:
            with open(self.log_file, 'r') as f:
                content = f.read()
                if content.strip():
                    print(content)
                else:
                    print("\nNo experiments recorded yet.")
        except FileNotFoundError:
            print("\nNo experiments recorded yet.")
            
        input("\nPress Enter to continue...")
        
    def run(self):
        """Main program loop"""
        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ").strip().upper()
            
            if choice == 'Q':
                print("\nGoodbye!")
                break
            elif choice == 'P':
                self.play_audio()
            elif choice == 'Y':
                self.record_rating("LIKED")
            elif choice == 'N':
                self.record_rating("DISLIKED")
            elif choice == 'L':
                self.view_log()
            elif choice.isdigit() and 1 <= int(choice) <= 7:
                self.change_setting(int(choice))
            else:
                print("\nInvalid choice!")
                input("Press Enter to continue...")


def main():
    explorer = ConsoleAudioExplorer()
    explorer.run()


if __name__ == '__main__':
    main()
