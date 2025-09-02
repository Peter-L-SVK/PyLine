#!/usr/bin/env sh

echo "Installing Lowercase To Uppercase changer for PyLine..."
echo "This hook script will convert all lower-case letters to upper-case in opened files"

HOOK_DIR="$HOME/.pyline/hooks/event_handlers/pre_load"
HOOK_FILE="lowercase_to_uppercase__80.pl"

# Create directory structure
mkdir -p "$HOOK_DIR"

# Copy the handler
cp "$HOOK_FILE" "$HOOK_DIR/"

# Set execute permissions
chmod +x "$HOOK_DIR/$HOOK_FILE"

echo "Lowercase to uppercase handler installed successfully!"
echo "Location: $HOOK_DIR/$HOOK_FILE"
echo ""
echo "PyLine will now convert all lower-case letters to upper-case in opened files"
exit 0
