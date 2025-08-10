

Made changes.



Made changes.



Made changes.



Made changes.



Made changes.

# Sports Data Information Design Principles

## Overview
This document outlines the design principles we've developed for presenting complex sports data in an accessible and intuitive hierarchical format.

## Core Principles

### 1. **Hierarchical Progressive Disclosure**
- **Principle**: Present information from general to specific, allowing users to drill down as needed
- **Implementation**: 
  - Game → Inning → Half-Inning → At-Bat → Pitch-by-Pitch
  - NFL: Game → Quarter → Drive → Play → Details
- **Rationale**: Users can get quick overviews or detailed analysis without information overload

### 2. **Result-First Organization**
- **Principle**: Lead with outcomes, provide process details as expandable children
- **Implementation**: 
  - "Player Name: Final Result" as main node
  - Pitch-by-pitch details as collapsed children
- **Rationale**: Most users want to know "what happened" before "how it happened"

### 3. **Semantic Labeling**
- **Principle**: Use natural language that matches how humans think about the sport
- **Implementation**:
  - "Top of the 3rd" instead of "Top Half"
  - "TJ Friedl: Struck out swinging" instead of "At-Bat: TJ Friedl"
- **Rationale**: Reduces cognitive load and matches sports terminology

### 4. **Smart Filtering and Noise Reduction**
- **Principle**: Hide administrative/transition information unless specifically requested
- **Implementation**:
  - Filter out inning markers, empty plays
  - Skip pitcher-batter announcements in pitch lists
  - Focus on meaningful game events
- **Rationale**: Keeps focus on actual game action

### 5. **Visual and Auditory Hierarchy**
- **Principle**: Use consistent visual/accessibility cues to indicate importance and type
- **Implementation**:
  - ⚾ icon for scoring plays
  - Color highlighting for important events
  - Proper accessibility labels for screen readers
- **Rationale**: Quick visual scanning and screen reader compatibility

### 6. **Enhanced Contextual Information**
- **Principle**: Add relevant context without cluttering the primary information
- **Implementation**:
  - "Strike 1 Looking (93 mph Four-seam FB)"
  - Score updates with scoring plays
  - Game state indicators (inning, count, outs)
- **Rationale**: Provides depth for interested users without overwhelming casual viewers

### 7. **Temporal Organization**
- **Principle**: Present events in chronological order with clear time/sequence indicators
- **Implementation**:
  - Innings in order (1st, 2nd, 3rd...)
  - Most recent events easily accessible
  - Clear sequence within at-bats
- **Rationale**: Matches natural flow of sports narrative

### 8. **Interactive Exploration**
- **Principle**: Allow users to control their level of detail engagement
- **Implementation**:
  - Collapsible tree nodes
  - F5 refresh at all levels
  - F6 navigation between sections
- **Rationale**: Different users have different information needs

### 9. **Accessibility-First Design**
- **Principle**: Ensure full functionality with screen readers and keyboard navigation
- **Implementation**:
  - Proper ARIA labels and roles
  - Keyboard shortcuts for common actions
  - Row context communication in tables
- **Rationale**: Sports information should be accessible to all fans

### 10. **Real-Time Responsiveness**
- **Principle**: Keep information current and allow easy updates
- **Implementation**:
  - F5 refresh functionality
  - Live game state indicators
  - Current score displays
- **Rationale**: Sports are dynamic; information systems must be too

## Application Patterns

### Baseball (Implemented)
```
Game
├── 1st Inning
│   ├── Top of the 1st
│   │   ├── TJ Friedl: Struck out swinging
│   │   │   ├── Pitch 1: Strike 1 Looking (93 mph Four-seam FB)
│   │   │   ├── Pitch 2: Strike 2 Foul (92 mph Sinker)
│   │   │   └── Pitch 3: Strike 3 Swinging (82 mph Sweeper)
│   │   └── Matt McLain: Walked
│   │       ├── Pitch 1: Ball 1 (91 mph Fastball)
│   │       └── [...]
│   └── Bottom of the 1st
│       └── [similar structure]
└── 2nd Inning
    └── [...]
```

### NFL (Proposed)
```
Game
├── 1st Quarter
│   ├── Drive 1 (Team A)
│   │   ├── Play 1: Pass complete to WR for 12 yards
│   │   │   ├── Formation: Shotgun 3WR
│   │   │   ├── Down & Distance: 1st & 10
│   │   │   └── Field Position: Own 25
│   │   ├── Play 2: Rush for 3 yards
│   │   └── Play 3: Touchdown pass (7 yards)
│   └── Drive 2 (Team B)
│       └── [similar structure]
└── 2nd Quarter
    └── [...]
```

## Implementation Guidelines

### Data Collection
1. **Identify Key Events**: What are the meaningful moments in this sport?
2. **Determine Hierarchy**: How do events naturally group?
3. **Extract Context**: What additional information enhances understanding?
4. **Filter Noise**: What administrative data can be hidden?

### User Interface Design
1. **Start Collapsed**: Show overview, allow expansion for details
2. **Clear Labels**: Use sport-specific terminology
3. **Visual Cues**: Highlight important events consistently
4. **Keyboard Support**: Full navigation without mouse

### Accessibility Considerations
1. **Screen Reader Testing**: Test with actual assistive technology
2. **Keyboard Navigation**: All features accessible via keyboard
3. **Context Announcement**: Provide location/state information
4. **Refresh Notifications**: Announce when data updates

## Validation Metrics

### User Experience
- Time to find specific information
- Accuracy of information retrieval
- User satisfaction with detail levels
- Accessibility compliance

### Technical Performance
- Data load times
- Refresh responsiveness
- Memory usage with large datasets
- Error handling and recovery

## Future Applications

These principles can extend to:
- **Basketball**: Game → Quarter → Possession → Play → Shot Details
- **Soccer**: Game → Half → Attack → Pass Sequence → Shot/Goal
- **Hockey**: Game → Period → Shift → Play → Shot/Save Details
- **Tennis**: Match → Set → Game → Point → Shot Sequence

The key is identifying the natural hierarchical structure of each sport and applying consistent information design principles.
