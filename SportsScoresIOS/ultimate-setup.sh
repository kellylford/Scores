#!/bin/bash

# Ultimate Xcode Project Creator
# Uses Xcode's built-in template instantiation

echo "🏈 Sports Scores iOS - Ultimate Auto-Setup"
echo "==========================================="
echo ""

SOURCE="/Users/kellyford/Documents/Scores/SportsScoresIOS/SportsScores"
TARGET="/Users/kellyford/Documents/Scores/SportsScoresApp"

# Find Xcode templates
XCODE_PATH=$(xcode-select -p)
TEMPLATE_PATH="$XCODE_PATH/Platforms/iPhoneOS.platform/Developer/Library/Xcode/Templates/Project Templates/iOS/Application"

echo "📍 Xcode path: $XCODE_PATH"
echo ""

# Method 1: Use xcodeproj gem if available
if command -v xcodeproj &> /dev/null; then
    echo "✅ Found xcodeproj tool"
    echo "🔨 Creating project with xcodeproj..."
    
    rm -rf "$TARGET"
    mkdir -p "$TARGET"
    cd "$TARGET"
    
    xcodeproj new SportsScores
    
    echo "✅ Project created!"
else
    echo "📦 xcodeproj not found (that's okay)"
fi

# Method 2: Use xcodegen if available  
if command -v xcodegen &> /dev/null; then
    echo "✅ Found xcodegen tool"
    echo "🔨 Creating project with xcodegen..."
    
    rm -rf "$TARGET"
    mkdir -p "$TARGET"
    cd "$TARGET"
    
    # Create xcodegen spec
    cat > project.yml << 'XGEOF'
name: SportsScores
options:
  bundleIdPrefix: com.sportsscores
targets:
  SportsScores:
    type: application
    platform: iOS
    deploymentTarget: "17.0"
    sources:
      - SportsScores
    settings:
      INFOPLIST_FILE: SportsScores/Info.plist
      PRODUCT_BUNDLE_IDENTIFIER: com.sportsscores.app
XGEOF
    
    # Copy source files
    cp -R "$SOURCE" "$TARGET/"
    
    # Generate project
    xcodegen generate
    
    echo ""
    echo "✅ Project generated successfully!"
    echo "📂 Location: $TARGET"
    echo ""
    echo "🎯 Opening in Xcode..."
    open "$TARGET/SportsScores.xcodeproj"
    exit 0
fi

# Method 3: Direct approach
echo "🔧 Using direct approach..."
echo ""
echo "Installing xcodegen for automatic project generation..."
echo ""

# Check if Homebrew is available
if command -v brew &> /dev/null; then
    echo "✅ Homebrew found"
    echo "📦 Installing xcodegen..."
    
    brew install xcodegen
    
    echo ""
    echo "✅ xcodegen installed!"
    echo "🔄 Re-running setup..."
    echo ""
    
    # Re-run this script
    exec "$0"
else
    echo ""
    echo "================================================================"
    echo "⚠️  Automatic setup requires xcodegen"
    echo "================================================================"
    echo ""
    echo "Option 1: Install Homebrew and xcodegen (RECOMMENDED)"
    echo "----------------------------------------"
    echo "  1. Install Homebrew:"
    echo "     /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    echo "  2. Install xcodegen:"
    echo "     brew install xcodegen"
    echo ""
    echo "  3. Re-run this script"
    echo ""
    echo "Option 2: Manual Setup in Xcode (5 minutes)"
    echo "----------------------------------------"
    echo "  See: SETUP_FIX.md"
    echo ""
    echo "================================================================"
fi
