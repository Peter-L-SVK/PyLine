#!/usr/bin/env sh
set -e  # Exit on error

# Path configurations
PREFIX="${PREFIX:-/usr/local}"
CONFIG_DIR="$HOME/.pyline"
BIN_DIR="$PREFIX/bin"
LICENSE_DIR="$PREFIX/share/licenses/PyLine"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Privilege escalation function
run_elevated() {
    if command_exists sudo; then
        echo "Using sudo for elevation..."
        sudo "$@"
    else
        echo "Using su for elevation..."
        su root -c "$*"
    fi
}

# Uninstall function
uninstall_pyline() {
    echo "Uninstalling PyLine from $PREFIX..."
    
    # Remove installed files
    for file in "$BIN_DIR/pyline" "$BIN_DIR/license-parts.txt"; do
        if [ -f "$file" ]; then
            if [ -w "$(dirname "$file")" ]; then
                rm -f "$file" && echo "Removed: $file"
            else
                run_elevated rm -f "$file" && echo "Removed: $file (with elevation)"
            fi
        fi
    done
    
    # Remove license directory
    if [ -d "$LICENSE_DIR" ]; then
        if [ -w "$(dirname "$LICENSE_DIR")" ]; then
            rm -rf "$LICENSE_DIR" && echo "Removed: $LICENSE_DIR"
        else
            run_elevated rm -rf "$LICENSE_DIR" && echo "Removed: $LICENSE_DIR (with elevation)"
        fi
    fi
    
    # Remove config directory (never needs elevation)
    if [ -d "$CONFIG_DIR" ]; then
        rm -rf "$CONFIG_DIR" && echo "Removed: $CONFIG_DIR"
    fi
    
    echo "Uninstallation complete"
    exit 0
}

# Handle uninstall flag
if [ "$1" = "-u" ]; then
    uninstall_pyline
fi

# Normal installation process
echo "Installing PyLine..."

# Check for pyinstaller
if ! command_exists pyinstaller; then
    echo "Installing pyinstaller..."
    pip install --user pyinstaller || { 
        echo "Failed to install pyinstaller" >&2; 
        exit 1; 
    }
fi

# Build the binary
cd ./src/ || {
    echo "Error: src/ directory not found" >&2
    exit 1
}

pyinstaller --onefile \
    --add-data "dirops.py:." \
    --add-data "execmode.py:." \
    --add-data "utils.py:." \
    --add-data "text_buffer.py:." \
    editor.py -n pyline

# Verify build succeeded
if [ ! -f "./dist/pyline" ]; then
    echo "Error: PyLine binary not found in ./dist/" >&2
    exit 1
fi

# Create config directory
mkdir -p "$CONFIG_DIR" || {
    echo "Error: Failed to create config directory $CONFIG_DIR" >&2
    exit 1
}

# Install files
if [ -w "$BIN_DIR" ]; then
    cp -v ./dist/pyline ./license-parts.txt "$BIN_DIR/" || {
        echo "Error: Failed to copy files to $BIN_DIR" >&2
        exit 1
    }
else
    echo "Note: Need elevated privileges to install to $BIN_DIR"
    run_elevated cp ./dist/pyline "$BIN_DIR/" && \
    run_elevated cp ./license-parts.txt "$BIN_DIR/" || {
        echo "Error: Failed to install with elevated privileges" >&2
        exit 1
    }
fi

# Install license
run_elevated mkdir -p "$LICENSE_DIR" && \
run_elevated cp ../LICENSE "$LICENSE_DIR/" || {
    echo "Note: License installation failed (non-critical)" >&2
}

# Cleanup
rm -rf ./build ./dist

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║              INSTALLATION COMPLETE             ║"
echo "╠════════════════════════════════════════════════╣"
echo "║                                                ║"
echo "║  PyLine has been successfully installed!       ║"
echo "║                                                ║"
echo "║  • Binary location: $PREFIX/bin/pyline      ║"
echo "║  • Config directory: $CONFIG_DIR         ║"
echo "║                                                ║"
echo "║  To run:                                       ║"
echo "║    $ pyline                                    ║"
echo "║                                                ║"
echo "║  To uninstall:                                 ║"
echo "║    $ ./install.sh -u                           ║"
echo "║                                                ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
exit 0
