#!/usr/bin/env sh
# install-smart-tab.sh

echo "Installing word counter for PyLine..."
echo "This provides multi-language smart indentation with input"

HOOK_DIR="$HOME/.pyline/hooks/event_handlers/word_count"
HOOK_FILE="word_counter__80.pl"

# Create directory structure
mkdir -p "$HOOK_DIR"

# Copy the handler
cp "$HOOK_FILE" "$HOOK_DIR/"

# Set execute permissions
chmod +x "$HOOK_DIR/$HOOK_FILE"

echo "Word counter handler installed successfully!"
echo "Location: $HOOK_DIR/$HOOK_FILE"
echo ""
echo "PyLine will now use word count hook instead of built-in one."
