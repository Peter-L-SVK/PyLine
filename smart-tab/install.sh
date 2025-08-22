#!/usr/bin/env bash
# install-smart-tab.sh

echo "Installing Smart Tab Handler for PyLine..."
echo "This provides multi-language smart indentation with input"

HOOK_DIR="$HOME/.pyline/hooks/input_handlers/edit_line"
HOOK_FILE="smart_tab__90.py"

# Create directory structure
mkdir -p "$HOOK_DIR"

# Copy the handler
cp "$HOOK_FILE" "$HOOK_DIR/"

# Set execute permissions
chmod +x "$HOOK_DIR/$HOOK_FILE"

echo "Smart tab handler installed successfully!"
echo "Location: $HOOK_DIR/$HOOK_FILE"
echo ""
echo "PyLine will now use auto indentation based on suffix of file."
