#!/bin/bash
# Unix/Linux/macOS build script for File Generator App
# This script creates a standalone executable for Unix systems

echo "Building File Generator App for Unix systems..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Build executable with cross-platform data handling
echo "Building executable with PyInstaller..."
pyinstaller --onefile --windowed --name="FileGenerator" --add-data "templates:templates" --hidden-import="config_manager" --hidden-import="validators" --hidden-import="constants" --hidden-import="docxtpl" --hidden-import="docxcompose" main.py

echo "Build complete! Executable is in dist/ folder"
echo ""
echo "Note: For Windows builds, use build.bat"
