#!/bin/bash
# Open Sports Scores iOS Project in Xcode

echo "🏈 Opening Sports Scores iOS Project..."
echo ""

PROJECT_PATH="/Users/kellyford/Documents/Scores/SportsScoresIOS/SportsScores.xcodeproj"

if [ -d "$PROJECT_PATH" ]; then
    echo "✅ Project found!"
    echo "📂 Opening Xcode..."
    open "$PROJECT_PATH"
    echo ""
    echo "🎉 Xcode should open now!"
    echo ""
    echo "Quick Tips:"
    echo "1. Connect your iPhone with USB"
    echo "2. Select iPhone from device menu (top bar)"
    echo "3. Click the Play button ▶️"
    echo ""
    echo "Need help? See README.md for complete instructions"
else
    echo "❌ Error: Project not found at:"
    echo "   $PROJECT_PATH"
    echo ""
    echo "Make sure you're running this from the correct location."
fi
