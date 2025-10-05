#!/usr/bin/env sh

echo "Installing Lowercase To Uppercase changer for PyLine..."
echo "This hook script will convert all lower-case letters to upper-case in opened files"

HOOK_DIR="$HOME/.pyline/hooks/event_handlers/pre_load"
HOOK_FILE="lowercase_to_uppercase__80.pl"

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

echo "Lowercase to uppercase handler installed successfully!"
echo "Location: $HOOK_DIR/$HOOK_FILE"
echo ""
echo "PyLine will now convert all lower-case letters to upper-case in opened files"
exit 0
