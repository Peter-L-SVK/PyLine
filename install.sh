#!/usr/bin/env bash
set -e  # Exit on error

# Path configurations
PREFIX="${PREFIX:-/usr/local}"
CONFIG_DIR="$HOME/.pyline"
BIN_DIR="$PREFIX/bin"
LICENSE_DIR="$PREFIX/share/licenses/PyLine"
HOOKS_DIR="$(pwd)/hooks"

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

# Function to install core util hooks
install_hooks() {
    if [ -d "$HOOKS_DIR" ] && [ -f "$HOOKS_DIR/install-all.sh" ]; then
        echo ""
        echo "Installing core utility hooks..."
        cd "$HOOKS_DIR"
        chmod +x install-all.sh
        if ./install-all.sh; then
            echo "✓ Core utility hooks installed successfully"
        else
            echo "⚠ Core utility hooks installation had issues, but continuing..."
        fi
        cd - > /dev/null
    else
        echo "⚠ Hooks directory or installer not found, skipping hook installation"
    fi
}

# Uninstall function
uninstall_pyline() {
    echo "Uninstalling PyLine from $PREFIX..."
    echo ""
    
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

# Ask about hook installation
echo ""
read -p "Install core utility hooks? [Y/n]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    HOOKS_INSTALL=true
    echo "✓ Will install core utility hooks"
else
    HOOKS_INSTALL=false
    echo "✓ Skipping hook installation"
fi
echo ""

# Check for pyinstaller
if ! command_exists pyinstaller; then
    echo "Installing pyinstaller..."
    pip install --user pyinstaller || { 
        echo "Failed to install pyinstaller" >&2; 
        exit 1; 
    }
fi

# Create config directory
mkdir -p "$CONFIG_DIR" || {
    echo "Error: Failed to create config directory $CONFIG_DIR" >&2
    exit 1
}
# Install themes directory
cp -r ./themes "$CONFIG_DIR/themes"

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
    main.py -n pyline

# Verify build succeeded
if [ ! -f "./dist/pyline" ]; then
    echo "Error: PyLine binary not found in ./dist/" >&2
    exit 1
fi

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

# Install hooks if requested
if [ "$HOOKS_INSTALL" = true ]; then
    install_hooks
fi

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
if [ "$HOOKS_INSTALL" = true ]; then
echo "║  • Core utility hooks: INSTALLED               ║"
else
echo "║  • Core utility hooks: SKIPPED                 ║"
fi
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
