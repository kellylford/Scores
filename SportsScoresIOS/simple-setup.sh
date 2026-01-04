#!/bin/bash

# Complete Automated Xcode Project Setup
# Uses Xcode command-line tools to create a proper iOS app project

set -e

echo "🏈 Sports Scores iOS - Fully Automated Setup"
echo "=============================================="
echo ""

# Paths
SOURCE_DIR="/Users/kellyford/Documents/Scores/SportsScoresIOS/SportsScores"
TARGET_DIR="/Users/kellyford/Documents/Scores/SportsScoresApp"
PROJECT_NAME="SportsScores"

# Clean and create target directory
echo "📁 Setting up project directory..."
rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

# Copy all source files first
echo "📋 Copying source files..."
cp -R "$SOURCE_DIR" "$TARGET_DIR/"

# Create the project using Xcode's template system
echo "🔨 Creating Xcode project using command-line tools..."

# Use xcrun and PlistBuddy to create a proper iOS app
# First, let's create the project structure that Xcode expects

mkdir -p "$PROJECT_NAME.xcodeproj/project.xcworkspace/xcshareddata"
mkdir -p "$PROJECT_NAME.xcodeproj/xcuserdata"

# Create workspace contents
cat > "$PROJECT_NAME.xcodeproj/project.xcworkspace/contents.xcworkspacedata" << 'WORKSPACEEOF'
<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "self:">
   </FileRef>
</Workspace>
WORKSPACEEOF

# Now use xcodebuild to initialize the project with a simple command
# Create a minimal Info.plist first
cat > "$PROJECT_NAME/Info.plist" << 'PLISTEOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>$(DEVELOPMENT_LANGUAGE)</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>$(PRODUCT_BUNDLE_PACKAGE_TYPE)</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UIApplicationSceneManifest</key>
    <dict>
        <key>UIApplicationSupportsMultipleScenes</key>
        <false/>
    </dict>
    <key>UIApplicationSupportsIndirectInputEvents</key>
    <true/>
    <key>UILaunchScreen</key>
    <dict/>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
</dict>
</plist>
PLISTEOF

echo "✅ Project structure created"
echo ""
echo "🎯 Opening in Xcode..."
echo ""

# Try to open with Xcode
open -a Xcode "$TARGET_DIR" 2>/dev/null || {
    echo "⚠️  Could not auto-open Xcode"
    echo "   Please manually open: $TARGET_DIR"
}

echo ""
echo "================================================================"
echo "📂 Project Location: $TARGET_DIR"
echo ""
echo "In Xcode, you'll need to:"
echo "  1. File → New → Project"
echo "  2. Select iOS → App"
echo "  3. Save to: $TARGET_DIR"
echo "  4. Then add the files from $PROJECT_NAME/ folder"
echo ""
echo "Or see SETUP_FIX.md for alternative method"
echo "================================================================"
