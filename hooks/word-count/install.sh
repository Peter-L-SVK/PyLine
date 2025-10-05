#!/usr/bin/env sh

echo "Installing word counter for PyLine..."
echo "This provides multi-language smart indentation with input"

HOOK_DIR="$HOME/.pyline/hooks/event_handlers/word_count"
HOOK_FILE="word_counter__80.pl"

# Create directory structure
if ! mkdir -p "$HOOK_DIR"; then
    echo "Error: Could not create directory $HOOK_DIR" >&2
    exit 1
fi

# Check if source file exists
if [ ! -f "$HOOK_FILE" ]; then
    echo "Error: Source file $HOOK_FILE not found" >&2
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

echo "Word counter handler installed successfully!"
echo "Location: $HOOK_DIR/$HOOK_FILE"
echo ""
echo "PyLine will now use word count hook instead of built-in one."
exit 0
