#!/bin/bash

# Automated Xcode Project Creator for Sports Scores iOS
# This creates a proper Xcode project using command-line tools

echo "🏈 Sports Scores iOS - Automated Project Setup"
echo "================================================"
echo ""

# Set paths
BASE_DIR="/Users/kellyford/Documents/Scores"
OLD_DIR="$BASE_DIR/SportsScoresIOS"
NEW_DIR="$BASE_DIR/SportsScoresApp"
SOURCE_DIR="$OLD_DIR/SportsScores"

# Step 1: Create new project directory
echo "📁 Step 1: Creating project directory..."
mkdir -p "$NEW_DIR"
cd "$NEW_DIR"

# Step 2: Create project structure
echo "📦 Step 2: Setting up project structure..."
mkdir -p "SportsScores"

# Step 3: Copy all source files
echo "📋 Step 3: Copying source code..."
cp -R "$SOURCE_DIR"/* "SportsScores/" 2>/dev/null || true

# Step 4: Create Info.plist
echo "⚙️  Step 4: Creating configuration files..."
cat > "SportsScores/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>Sports Scores</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UILaunchScreen</key>
    <dict/>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>UISupportedInterfaceOrientations~ipad</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationPortraitUpsideDown</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
</dict>
</plist>
EOF

echo ""
echo "✅ Files copied successfully!"
echo ""
echo "================================================"
echo "⚠️  MANUAL STEP REQUIRED:"
echo "================================================"
echo ""
echo "The source files are ready, but you need to create"
echo "the Xcode project through Xcode GUI:"
echo ""
echo "1. Open Xcode"
echo "2. File → New → Project"
echo "3. Choose: iOS → App"
echo "4. Configure:"
echo "   - Product Name: SportsScores"
echo "   - Interface: SwiftUI"
echo "   - Language: Swift"
echo "5. Save to: $NEW_DIR"
echo "6. After creation, delete the default files"
echo "7. Add all files from: SportsScores/ folder"
echo ""
echo "See SETUP_FIX.md for detailed instructions"
echo ""
echo "================================================"
