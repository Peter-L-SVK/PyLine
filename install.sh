#!/usr/bin/env sh
set -e  # Exit on error

# Check for pyinstaller
if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "Installing pyinstaller..."
    pip install pyinstaller || { echo "Failed to install pyinstaller"; exit 1; }
fi

# Build the binary with explicit paths
cd ./src/
pyinstaller --onefile --add-data "dirops.py:." --add-data "execmode.py:." --add-data "utils.py:." --add-data "text_buffer.py:." editor.py -n pyline

# Verify build succeeded
if [ ! -f "./dist/pyline" ]; then
    echo "Error: PyLine binary not found in ./dist/"
    exit 1
fi

# Verify build succeeded
if [ ! -f "./dist/pyline" ]; then
    echo "Error: PyLine binary not found in ./dist/"
    exit 1
fi

# Create config dir
mkdir ~/.pyline

# Copy files to /usr/local/bin (requires sudo)
sudo cp ./dist/pyline ./license-parts.txt /usr/local/bin/ || {
    echo "Error: Failed to copy files to /usr/local/bin (check permissions?)";
    exit 1;
}
# Install LICENSE system-wide
sudo mkdir -p /usr/share/licenses/PyLine && sudo cp ../LICENSE /usr/share/licenses/PyLine/ || {
    echo "Error: Failed to copy LICENSE to /usr/share/licenses (check permissions?)";
    exit 1;
}

# Cleaning up
rm -rf ./build ./dist
echo "Installation successful! PyLine is now in /usr/local/bin"
echo "To run or test, run: pyline"
exit 0
