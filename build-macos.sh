#!/bin/bash

echo "====================================="
echo "Scores Application macOS Build Script"
echo "====================================="
echo

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Build the executable
echo
echo "====================================="
echo -e "${YELLOW}Building macOS application...${NC}"
echo "====================================="

# For macOS, we'll create an app bundle instead of just an executable
pyinstaller --onefile --windowed --name=Scores main.py

# Check if build was successful
if [ -f "dist/Scores" ]; then
    echo
    echo "====================================="
    echo -e "${GREEN}Build SUCCESSFUL!${NC}"
    echo "====================================="
    echo
    echo "Executable created at: dist/Scores"
    
    # Get file size
    file_size=$(stat -f%z "dist/Scores" 2>/dev/null || stat -c%s "dist/Scores" 2>/dev/null)
    file_size_mb=$((file_size / 1024 / 1024))
    echo "File size: $file_size bytes (~${file_size_mb}MB)"
    
    echo
    echo "To run the application:"
    echo "  1. Navigate to the dist folder"
    echo "  2. Run: ./Scores"
    echo "  3. Or double-click Scores in Finder (may need to allow in Security settings)"
    echo
    echo "The executable includes all dependencies and can be"
    echo "distributed to other macOS machines with the same architecture."
    echo "====================================="
    
    # Make the executable... executable
    chmod +x dist/Scores
    
else
    echo
    echo "====================================="
    echo -e "${RED}Build FAILED!${NC}"
    echo "====================================="
    echo "Check the output above for errors."
    echo "Common issues:"
    echo "  - Missing dependencies (check requirements-minimal.txt)"
    echo "  - PyInstaller not installed"
    echo "  - Python path issues"
    echo "====================================="
    exit 1
fi

echo
echo -e "${GREEN}Build completed successfully!${NC}"
echo "Press Enter to continue..."
read
