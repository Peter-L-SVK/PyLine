#!/usr/bin/env sh

echo "Installing search/replace hook for PyLine..."
echo "This hook provides incremental search, highlighting, and sed-style replace for all matches."

HOOK_DIR="$HOME/.pyline/hooks/event_handlers/search_replace"
HOOK_FILE="search_replace__75.pl"

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


echo "Search/replace hook installed successfully!"
echo "Location: $HOOK_DIR/$HOOK_FILE"
echo ""
echo "Restart PyLine or reload hooks for changes to take effect."
exit 0
