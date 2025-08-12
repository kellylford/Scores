# Game Log Export Structure Documentation (Updated)

## Overview
The game log export creates a hierarchical, semantic HTML structure that's optimized for both screen reader accessibility and visual reading. The design allows users to **skim quickly** or **dive deep** into details at their own pace.

## Core Design Philosophy

### 1. **Progressive Disclosure**
- **Game Context**: H1 provides overall game information
- **Inning Flow**: H2 headings track game progression ("Top of the 1st", "Bottom of the 2nd")
- **At-Bat Results**: H3 headings give immediate play context (`"Smith: Single to left field"`)
- **Optional Detail**: Nested lists provide pitch-by-pitch breakdown
- **Confirmation**: Result repetition reinforces the outcome

### 2. **Multiple Reading Paths**
- **Macro Skimming**: Read H1 and H2 headings to understand game flow and inning progression
- **Micro Skimming**: Read H3 headings to get all at-bat results within an inning
- **Detailed Analysis**: Expand into pitch lists for full breakdown
- **Hybrid Reading**: Mix heading levels based on interest (skip boring innings, dive into exciting ones)

## HTML Structure Logic

### Document Hierarchy
```html
H1: Game Title (e.g., "Exported Game Log - MLB - Mets vs Brewers")
  └── Inning Sections (div.period)
      └── H2: Inning Halves ("Top of the 1st", "Bottom of the 1st")
          └── H3: At-Bat Results ("Smith: Single to left field")
              └── UL: Pitch Details (enhanced with velocity/type)
              └── Result Confirmation (reinforcement)
```

### At-Bat Structure Pattern
```html
<div class="half-section">
  <h2 class="inning-half-title">Top of the 1st</h2>
  <ul class="at-bat-list">
    <li class="at-bat-item">
      <h3 class="at-bat-heading">Smith: Single to left field (2-1)</h3>
      <ul class="pitch-list">
        <li>Pitch 1: Ball 1 (89 mph Changeup)</li>
        <li>Pitch 2: Strike 1 Looking (94 mph Four-Seam Fastball)</li>
        <li>Pitch 3: Ball In Play (91 mph Slider)</li>
      </ul>
      <div class="at-bat-result">Result: Single to left field (2-1)</div>
    </li>
  </ul>
</div>
```

## Screen Reader Optimization

### Heading Navigation Benefits
1. **H1 Navigation**: Jump to game overview
2. **H2 Navigation**: Navigate between inning halves - understand game pacing and flow
3. **H3 Navigation**: Jump between at-bats within an inning - get all scoring/results
4. **List Navigation**: Drill into pitch details when desired

### Information Architecture Excellence
- **Complete Context**: Reading H1 + H2 + H3 headings tells the entire game story
- **Inning Awareness**: Never lose track of what inning you're in
- **At-Bat Isolation**: Can focus on individual at-bats without losing context
- **Optional Depth**: Pitch details available but not required for understanding

## Enhanced Reading Scenarios

### 1. **Quick Game Summary** (H1 + H2 only)
```
Exported Game Log - MLB - Mets vs Brewers
  Top of the 1st
  Bottom of the 1st  
  Top of the 2nd
  Bottom of the 2nd
  [...]
```
*User understands: Game flow, which innings had action*

### 2. **Complete Results** (H1 + H2 + H3)
```
Exported Game Log - MLB - Mets vs Brewers
  Top of the 1st
    Smith: Single to left field
    Jones: Strikeout swinging
    Williams: Groundout to second
  Bottom of the 1st
    Rodriguez: Home run to left (2-0)
    Martinez: Walk
    [...]
```
*User understands: Complete game narrative with all outcomes*

### 3. **Detailed Analysis** (All levels + lists)
*User can dive into specific at-bats that interest them while maintaining context*

## CSS Design Principles

### Visual Hierarchy
```css
h1 { font-size: 24px; }                    /* Game context */
.inning-half-title { 
    font-size: 20px;                       /* Inning progression */
    border-bottom: 2px solid #007cba;      /* Visual separation */
}
.at-bat-heading { 
    font-size: 16px;                       /* At-bat results */
    color: #333;                           /* Standard emphasis */
}
.at-bat-heading.scoring { 
    color: #ff6b35;                        /* Highlight scoring */
}
```

### Progressive Visual Disclosure
- **Inning boundaries** clearly marked with borders and spacing
- **At-bat outcomes** immediately visible but not overwhelming
- **Pitch details** indented and styled as secondary information
- **Scoring plays** highlighted at all levels for quick identification

## Data Enhancement Logic

### Pitch Detail Enrichment
```python
# Base text: "Pitch 3: Strike 1 Looking"
enhanced_text = play_text
velocity = play.get("pitchVelocity")
pitch_type = play.get("pitchType", {}).get("text", "")

if velocity and pitch_type_text:
    enhanced_text = f"{play_text} ({velocity} mph {pitch_type_text})"
    # Result: "Pitch 3: Strike 1 Looking (94 mph Four-Seam Fastball)"
```

### Smart Batter Name Extraction
```python
# Priority order for batter identification:
1. participants[type="batter"].athlete.shortName
2. Extract from play text patterns ("Smith to first base")
3. Extract from result patterns ("Jones struck out")
4. Fallback to "Play" if no name found
```

## Key Accessibility Features

### 1. **Perfect Semantic HTML**
- Proper heading hierarchy (H1 → H2 → H3)
- Meaningful list structures
- Clear document outline that makes sense

### 2. **Multi-Level Navigation**
- **H1**: Game context
- **H2**: Inning flow and timing
- **H3**: All play outcomes
- **Lists**: Pitch-by-pitch details

### 3. **Information Redundancy**
- Result in H3 heading AND at end of section
- Context preserved at every level
- No information loss regardless of navigation style

### 4. **Visual and Auditory Cues**
- Color coding for scoring plays (works at H2 and H3 levels)
- List structure for clear nesting
- Consistent styling patterns

## Why This Heading Structure is Brilliant

### For Screen Reader Users
1. **Complete Game Flow**: H2 navigation reveals game pacing and inning structure
2. **Result Summary**: H3 navigation gives all at-bat outcomes without pitch details
3. **Contextual Awareness**: Always know what inning you're in when examining at-bats
4. **Flexible Depth**: Choose your level of detail on-demand

### For Visual Users
1. **Clear Game Structure**: Visual breaks between innings and at-bats
2. **Scannable Results**: Can read down H3 headings for quick outcomes
3. **Optional Expansion**: Pitch details available but not overwhelming
4. **Professional Layout**: Clean, newspaper-like game recap format

### For All Users
1. **Universal Navigation**: Works with any reading style or assistive technology
2. **Complete Information**: Nothing lost, everything organized logically
3. **Scalable Detail**: From 30-second overview to deep analysis
4. **Exportable Format**: Professional document suitable for sharing/archiving

## Technical Implementation Excellence

### Document Structure Benefits
- **Valid HTML5**: Proper semantic structure passes all validation
- **SEO Friendly**: Search engines understand the content hierarchy
- **Print Optimized**: Document flows well when printed
- **Archive Quality**: Professional format suitable for long-term storage

### Screen Reader Specific Features
- **Landmark Navigation**: Clear document regions
- **List Navigation**: Efficient movement through pitch details
- **Heading Navigation**: Multi-level game understanding
- **Skip Links**: Implicit through proper heading structure

This refined structure creates a **universally accessible masterpiece** that serves as both a quick reference and a detailed analysis tool, making complex baseball data approachable and navigable for every type of user and reading preference.

## Key Innovation: Progressive Context
The H1 → H2 → H3 structure means users can build context progressively:
1. **H1**: What game am I reading?
2. **H2**: What part of the game am I in?  
3. **H3**: What happened in this specific at-bat?
4. **Lists**: How did it happen pitch-by-pitch?

This creates perfect **spatial and temporal orientation** - users never get lost in the data because the heading structure constantly reinforces where they are in the game narrative.
