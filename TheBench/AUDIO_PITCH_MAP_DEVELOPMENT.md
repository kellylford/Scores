# Audio Pitch Map Feature - Development Notes

## 🎯 **Feature Overview**
Revolutionary accessibility feature that converts pitch coordinate data into spatial audio feedback, creating an "audio pitch map" for enhanced baseball understanding.

## 🔊 **Core Concept**
Transform our validated pitch location data into multi-dimensional audio experience:
- **Location → Stereo Position**: Inside pitches = left audio, Outside = right audio
- **Height → Frequency**: High pitches = higher tones, Low = lower tones  
- **Velocity → Tempo**: Fastballs = quick sounds, Changeups = slow sounds
- **Pitch Type → Sound Character**: Different instruments/tones per pitch type

## 🛠 **Technical Foundation Already in Place**
✅ **Validated Coordinate System**: 85.4% accuracy with real umpire calls  
✅ **Real ESPN API Data**: Precise x,y coordinates for every pitch  
✅ **PyQt6 Framework**: Built-in audio capabilities with QMediaPlayer  
✅ **Pitch Classification**: Velocity, type, and outcome data available

## 🎹 **Audio Mapping Strategy**

### **Spatial Audio Theater Approach**
```
User Position: Sitting behind home plate (catcher's perspective)
Audio Field: 180-degree stereo field representing strike zone + foul territory

Coordinate Mapping:
- X: 85-145 (Strike Zone) → Center stereo field  
- X: <85 (Inside) → Left stereo pan
- X: >145 (Outside) → Right stereo pan
- Y: >195 (High) → Higher frequency tones
- Y: <150 (Low) → Lower frequency tones
```

### **Sound Design Elements**

#### **Pitch Location Audio**
- **Strike Zone Center**: Pure 440Hz tone, center stereo
- **Outside Corner**: 500Hz tone, 75% right pan
- **Way Outside**: 600Hz tone, 100% right pan
- **Inside Corner**: 380Hz tone, 75% left pan  
- **Way Inside**: 320Hz tone, 100% left pan

#### **Pitch Type Audio Signatures**
- **Four-seam Fastball**: Sharp, clean click
- **Slider**: Swooshing sound with frequency bend
- **Changeup**: Soft, muted tone
- **Curveball**: Descending frequency sweep
- **Sinker**: Deep, heavy tone

#### **Velocity Integration**
- **90+ mph**: Rapid sound onset
- **80-89 mph**: Medium timing
- **<80 mph**: Slower, more deliberate sound

## 🎮 **User Interface Design**

### **New Hotkey System**
- **Enter on Pitch**: Activate audio pitch map mode
- **Up/Down Arrows**: Navigate pitches with audio feedback
- **Left/Right Arrows**: Fine-tune audio parameters
- **Space**: Replay current pitch audio
- **P**: Play entire at-bat as audio sequence
- **Escape**: Return to normal text navigation

### **Audio Controls**
- **Volume slider**: Master audio level
- **Stereo width**: Adjust left/right separation intensity
- **Frequency range**: Adjust high/low pitch spread
- **Tempo scaling**: Adjust velocity-to-timing mapping

## 🌟 **Advanced Features (Future Development)**

### **"Pitch Symphony" Mode**
- Play entire at-bat as musical sequence
- Each pitch becomes a note in the composition
- Different pitchers have unique "musical signatures"
- Famous at-bats become recognizable audio "songs"

### **Comparative Audio Analysis**
- Compare pitcher's typical locations vs current at-bat
- Audio "heat map" of where pitcher usually throws
- "This pitcher works the outside corner" → more right-panned audio history

### **Learning & Quiz Modes**
- **Training Mode**: Learn to identify pitch locations by sound
- **Quiz Mode**: Listen to audio, guess location/type
- **Progress Tracking**: Improve audio pitch recognition skills

### **Game Flow Audio**
- **Count Tension**: Audio intensity changes with ball/strike count
- **Situational Context**: Different base tones for runners on base
- **Momentum Shifts**: Audio cues for key moments

## 🔧 **Implementation Phases**

### **Phase 1: Basic Audio Location (MVP)**
- Simple tone generation for pitch locations
- Basic stereo panning for inside/outside
- Integration with existing pitch navigation

### **Phase 2: Multi-Dimensional Audio**
- Add velocity and pitch type audio elements
- Frequency mapping for high/low locations
- Enhanced stereo field positioning

### **Phase 3: Advanced Features**
- Pitch sequence playback
- Comparative analysis audio
- Learning modes and user customization

### **Phase 4: Audio Innovation**
- 3D spatial audio with binaural processing
- Haptic feedback integration
- Real-time audio generation

## 📚 **Technical Research Needed**

### **Audio Libraries to Evaluate**
- **PyAudio**: Real-time audio generation and processing
- **pygame.mixer**: Simple sound effects and mixing
- **pydub**: Audio manipulation and effects processing
- **numpy + scipy**: Custom waveform generation
- **OpenAL**: 3D positional audio (advanced)

### **Audio Format Considerations**
- **Synthetic vs Pre-recorded**: Generate tones vs use sound samples
- **Latency Requirements**: Real-time audio feedback timing
- **Cross-platform Compatibility**: Windows/Mac/Linux audio systems
- **Accessibility Standards**: Integration with screen readers

## 🏆 **Accessibility Impact Potential**

### **Revolutionary Features**
- **First-ever spatial audio pitch tracking** for accessibility
- **Transforms abstract data** into intuitive audio experience
- **New way to "see" baseball strategy** through sound
- **Could become industry standard** for accessible sports

### **User Benefits**
- **Enhanced Understanding**: Pitch location becomes immediately apparent
- **Strategic Insight**: Hear pitching patterns and tendencies
- **Immersive Experience**: Feel like you're behind the plate
- **Educational Tool**: Learn baseball strategy through audio

## 🎯 **Success Metrics**

### **User Experience Goals**
- Users can identify pitch locations by audio alone
- 90%+ accuracy in audio-to-location mapping
- Reduced cognitive load for processing pitch information
- Increased engagement and enjoyment

### **Technical Goals**
- <100ms audio latency for real-time feedback
- Seamless integration with existing navigation
- Customizable audio parameters for user preferences
- Cross-platform audio compatibility

## 📋 **Next Steps for Development**

1. **Research & Prototyping**
   - Evaluate audio libraries and capabilities
   - Create simple tone generation prototype
   - Test stereo panning and frequency mapping

2. **User Testing**
   - Gather feedback from screen reader users
   - Test audio mapping intuitivenes
   - Refine audio design based on user input

3. **Integration Planning**
   - Design seamless integration with existing UI
   - Plan hotkey system and navigation flow
   - Ensure compatibility with current features

4. **Implementation**
   - Start with Phase 1 MVP features
   - Iterate based on user feedback
   - Gradually add advanced functionality

---

**Branch Purpose**: Experimental development of audio pitch mapping features  
**Base**: main branch with validated pitch location system  
**Status**: Planning and research phase  
**Goal**: Revolutionary accessibility enhancement for baseball audio experience
