#!/bin/bash
# Export Keyboard and Text Replacement Data
# This script exports accessible keyboard/autocorrect data for the consciousness engine

OUTPUT_FILE="$HOME/Desktop/artificial mind map/.keyboard_export.json"
TEMP_FILE=$(mktemp)

# Initialize JSON structure
echo '{"text_replacements": {}, "typing_data": {}, "exported_at": "'$(date -Iseconds)'"}' > "$TEMP_FILE"

# Try to extract text replacements from various sources
# Note: Most autocorrect data is stored in protected system databases
# This exports what is accessible

# Export from zsh history (shows user typing patterns)
if [ -f "$HOME/.zsh_history" ]; then
    HISTORY_ENTRIES=$(wc -l < "$HOME/.zsh_history" 2>/dev/null || echo "0")
    echo "{\"zsh_history_entries\": $HISTORY_ENTRIES}" >> "$TEMP_FILE"
fi

# Export from any accessible keyboard preferences
KEYBOARD_PREFS="$HOME/Library/Preferences/com.apple.Keyboard-Settings.extension.plist"
if [ -f "$KEYBOARD_PREFS" ]; then
    plutil -convert json -o - "$KEYBOARD_PREFS" 2>/dev/null >> "$TEMP_FILE" || true
fi

# Try to get text replacements via defaults
DEFAULTS_OUTPUT=$(defaults read com.apple.Keyboard-Settings.extension 2>/dev/null || echo "{}")
echo "$DEFAULTS_OUTPUT" >> "$TEMP_FILE"

# Move to final location
mv "$TEMP_FILE" "$OUTPUT_FILE"

echo "Keyboard data exported to: $OUTPUT_FILE"
cat "$OUTPUT_FILE"
