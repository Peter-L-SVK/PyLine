#!/usr/bin/env sh
set -e  # Exit on error

# Check for pyinstaller
if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "Installing pyinstaller..."
    pip install pyinstaller || { echo "Failed to install pyinstaller"; exit 1; }
fi

# Build the binary
cd ./src/
pyinstaller --onefile editor.py -n pyline

# Verify build succeeded
if [ ! -f "./dist/pyline" ]; then
    echo "Error: PyLine binary not found in ./dist/"
    exit 1
fi

# Copy files to /usr/local/bin (requires sudo)
sudo cp ./dist/pyline ./license-parts.txt /usr/local/bin/ || {
    echo "Error: Failed to copy files to /usr/local/bin (check permissions?)";
    exit 1;
}

# Cleaning up
rm -rf ./build ./dist
echo "Installation successful! PyLine is now in /usr/local/bin"
echo "To run or test, run: pyline"
exit 0
