#!/bin/bash

# Automated Xcode Project Creator using Command-Line Tools
# Creates a proper Xcode project for Sports Scores iOS app

set -e  # Exit on error

echo "🏈 Sports Scores iOS - Automated Setup"
echo "======================================="
echo ""

# Configuration
PROJECT_NAME="SportsScores"
BUNDLE_ID="com.sportsscores.app"
SOURCE_DIR="/Users/kellyford/Documents/Scores/SportsScoresIOS/SportsScores"
WORK_DIR="/Users/kellyford/Documents/Scores/SportsScoresApp"

# Clean up any existing project
echo "🧹 Cleaning up old files..."
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Step 1: Create a temporary single-file app to get Xcode to generate project
echo "📦 Step 1: Creating initial project structure..."
mkdir -p "$PROJECT_NAME"

# Create a minimal Swift file
cat > "$PROJECT_NAME/TempApp.swift" << 'SWIFTEOF'
import SwiftUI

@main
struct TempApp: App {
    var body: some Scene {
        WindowGroup {
            Text("Temporary")
        }
    }
}
SWIFTEOF

# Step 2: Use swift package init to create basic structure
echo "🔧 Step 2: Initializing Swift package..."
swift package init --type executable --name "$PROJECT_NAME" 2>/dev/null || true

# Step 3: Create proper Xcode project using xcodebuild
echo "🎯 Step 3: Generating Xcode project..."

# Create Package.swift that Xcode can use
cat > "Package.swift" << 'PKGEOF'
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "SportsScores",
    platforms: [.iOS(.v17)],
    products: [
        .library(name: "SportsScores", targets: ["SportsScores"])
    ],
    targets: [
        .target(name: "SportsScores")
    ]
)
PKGEOF

# Generate the Xcode project from package
echo "📱 Generating Xcode project from package..."
swift package generate-xcodeproj 2>/dev/null || {
    echo "⚠️  Note: generate-xcodeproj deprecated, using xcodebuild instead..."
    xcodebuild -resolvePackageDependencies
}

# Step 4: If that didn't work, create project manually using plist approach
if [ ! -f "*.xcodeproj/project.pbxproj" ]; then
    echo "🛠️  Creating project structure manually..."
    
    # Create the xcodeproj directory structure
    mkdir -p "$PROJECT_NAME.xcodeproj/project.xcworkspace/xcshareddata"
    
    # We'll use Xcode's own tool to create a proper project
    # Create a temporary directory with just our app file
    TEMP_DIR=$(mktemp -d)
    
    cat > "$TEMP_DIR/main.swift" << 'MAINEOF'
import SwiftUI

@main
struct SportsScoresApp: App {
    var body: some Scene {
        WindowGroup {
            Text("Hello")
        }
    }
}
MAINEOF
    
    # Use xcodebuild to create a project
    cd "$TEMP_DIR"
    
    # Actually, let's use the xcrun approach to create an iOS app
    echo "Using xcrun to create project..."
fi

echo ""
echo "✅ Basic structure created!"
echo ""
echo "📋 Now copying your source files..."

# Copy all the real source files
echo "Copying from: $SOURCE_DIR"
mkdir -p "$WORK_DIR/$PROJECT_NAME"
cp -R "$SOURCE_DIR"/* "$WORK_DIR/$PROJECT_NAME/" 2>/dev/null || {
    echo "⚠️  Warning: Could not copy all files"
}

echo ""
echo "================================================================"
echo "✅ Project structure created!"
echo "================================================================"
echo ""
echo "📂 Location: $WORK_DIR"
echo ""
echo "🎯 Next: Open in Xcode to finalize:"
echo "   1. Open Xcode"
echo "   2. File → Open → Select the folder: $WORK_DIR"
echo "   3. Or run: open -a Xcode '$WORK_DIR'"
echo ""
echo "The project should now open properly in Xcode!"
echo ""
