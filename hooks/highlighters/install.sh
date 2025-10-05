#!/usr/bin/env sh
# install-highlighters

echo "Installing syntax highlighters for PyLine..."
echo "This provides properly colored syntax."

HOOK_DIR="$HOME/.pyline/hooks/syntax_handlers/highlight"
HOOK_FILE_1="json_highlight__60.py" 
HOOK_FILE_2="shell_highlight__70.py"

# Create directory structure
mkdir -p "$HOOK_DIR"

# Copy the handler
cp "$HOOK_FILE_1" "$HOOK_FILE_2" "$HOOK_DIR/"

# Set execute permissions
chmod +x "$HOOK_DIR/$HOOK_FILE_1" "$HOOK_DIR/$HOOK_FILE_2"

echo "Highlighters installed successfully!"
echo "Location:
$HOOK_DIR/$HOOK_FILE_1
$HOOK_DIR/$HOOK_FILE_2" 
echo ""
echo "PyLine will now use highlighting based on suffix of file."
exit 0
