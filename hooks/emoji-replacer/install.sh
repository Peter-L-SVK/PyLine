#!/usr/bin/env sh

echo "Installing Emoji Replacer for PyLine..."
echo "This hook will replace letters with emojis during text editing"

HOOK_DIR="$HOME/.pyline/hooks/editing_ops/post_edit"
HOOK_FILE="emoji_replacer__80.pl"

# Create directory structure
if ! mkdir -p "$HOOK_DIR"; then
    echo "Error: Could not create directory $HOOK_DIR" >&2
    exit 1
fi

# Check if source file exists
if [ ! -f "$HOOK_FILE" ]; then
    echo "Error: Source file $HOOK_FILE not found" >&2
    echo "Make sure you're running this script from the directory containing $HOOK_FILE" >&2
    exit 1
fi

# Copy the handler
if ! cp "$HOOK_FILE" "$HOOK_DIR/"; then
    echo "Error: Could not copy $HOOK_FILE to $HOOK_DIR" >&2
    exit 1
fi

# Set execute permissions
if ! chmod +x "$HOOK_DIR/$HOOK_FILE"; then
    echo "Error: Could not set execute permissions on $HOOK_DIR/$HOOK_FILE" >&2
    exit 1
fi

echo "Emoji replacer hook installed successfully!"
echo "Location: $HOOK_DIR/$HOOK_FILE"
echo ""
echo "PyLine will now automatically replace:"
echo "  - 'g' and 'G' with 🦒 (giraffe)"
echo "  - 'h' and 'H' with 🐹 (hamster)"
echo ""
echo "To use: Edit any line in PyLine and the replacements will happen automatically!"

exit 0
