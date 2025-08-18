#!/bin/bash

echo "========================================="
echo "Scores Application macOS App Bundle Build"
echo "========================================="
echo

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment!${NC}"
        echo "Make sure Python 3 is installed and accessible."
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install/upgrade dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
python -m pip install --upgrade pip
python -m pip install -r requirements-minimal.txt

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf dist build Scores.spec

# Build the app bundle
echo
echo "========================================="
echo -e "${YELLOW}Building macOS .app bundle...${NC}"
echo "========================================="

# Create the .app bundle with proper macOS integration
pyinstaller \
    --onedir \
    --windowed \
    --name=Scores \
    --osx-bundle-identifier=com.kellylford.scores \
    --add-data="README.md:." \
    --add-data="macos_accessibility.py:." \
    main.py

# Check if build was successful
if [ -d "dist/Scores.app" ]; then
    echo
    echo "========================================="
    echo -e "${GREEN}Build SUCCESSFUL!${NC}"
    echo "========================================="
    echo
    echo -e "${GREEN}macOS App Bundle created at: dist/Scores.app${NC}"
    
    # Get app bundle size
    app_size=$(du -sh "dist/Scores.app" | cut -f1)
    echo "App Bundle size: $app_size"
    
    echo
    echo -e "${BLUE}Installation and Usage:${NC}"
    echo "  1. Copy dist/Scores.app to your Applications folder"
    echo "  2. Double-click to launch from Applications or Launchpad"
    echo "  3. If prompted by Gatekeeper, go to System Preferences > Security & Privacy"
    echo "     and click 'Open Anyway' to allow the app to run"
    echo
    echo -e "${BLUE}Distribution:${NC}"
    echo "  - The .app bundle includes all dependencies"
    echo "  - Can be distributed to other macOS machines with same architecture"
    echo "  - For distribution to other users, consider code signing"
    echo
    echo "========================================="
    
    # Optional: Create a simple installer script
    echo -e "${YELLOW}Creating installer script...${NC}"
    cat > dist/install-scores.sh << 'EOF'
#!/bin/bash
echo "Installing Scores to Applications folder..."
if [ -d "/Applications/Scores.app" ]; then
    echo "Removing existing installation..."
    rm -rf "/Applications/Scores.app"
fi
cp -R "Scores.app" "/Applications/"
echo "Scores has been installed to Applications folder!"
echo "You can now launch it from Launchpad or Applications folder."
EOF
    chmod +x dist/install-scores.sh
    echo -e "${GREEN}Installer script created: dist/install-scores.sh${NC}"
    
else
    echo
    echo "========================================="
    echo -e "${RED}Build FAILED!${NC}"
    echo "========================================="
    echo "Check the output above for errors."
    echo "Common issues:"
    echo "  - Missing dependencies (check requirements-minimal.txt)"
    echo "  - PyInstaller not installed"
    echo "  - Python path issues"
    echo "  - macOS development tools not installed"
    echo "========================================="
    exit 1
fi

echo
echo -e "${GREEN}macOS App Bundle build completed successfully!${NC}"
echo "Press Enter to continue..."
read
