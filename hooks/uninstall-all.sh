#!/usr/bin/env bash
# uninstall-all-hooks.sh

set -e

echo "=================================================="
echo "    PyLine Hooks Master Uninstaller"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

HOOK_BASE="$HOME/.pyline/hooks"

# Hook definitions (same as installer but without source dirs for uninstall)
declare -A hooks=(
    ["smart_tab"]="input_handlers/edit_line smart_tab__90.py" 
    ["word_counter"]="event_handlers/word_count word_counter__80.pl"
    ["json_highlight"]="syntax_handlers/highlight json_highlight__60.py"
    ["shell_highlight"]="syntax_handlers/highlight shell_highlight__70.py"
    ["search_replace"]="event_handlers/search_replace search_replace__75.pl"
    ["grammar_checker"]="editing_ops/process_content grammar_checker__70.py"
)

# Config files to remove
declare -A config_files=(
    ["grammar_config"]="editing_ops/process_content grammar_config.json"
)

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

uninstall_hooks() {
    echo "This will remove the following PyLine hooks:"
    echo ""
    for hook_name in "${!hooks[@]}"; do
        IFS=' ' read -r hook_path hook_file <<< "${hooks[$hook_name]}"
        echo "  - $hook_name: $HOOK_BASE/$hook_path/$hook_file"
    done
    for config_name in "${!config_files[@]}"; do
        IFS=' ' read -r config_path config_file <<< "${config_files[$config_name]}"
        echo "  - $config_name: $HOOK_BASE/$config_path/$config_file"
    done
    echo ""
    
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Uninstallation cancelled."
        exit 0
    fi
    
    local removed_count=0
    local total_count=0
    
    # Remove executable hooks
    for hook_name in "${!hooks[@]}"; do
        IFS=' ' read -r hook_path hook_file <<< "${hooks[$hook_name]}"
        local target_file="$HOOK_BASE/$hook_path/$hook_file"
        total_count=$((total_count + 1))
        
        if [ -f "$target_file" ]; then
            if rm "$target_file"; then
                echo -e "  ${GREEN}✓${NC} Removed: $hook_name"
                removed_count=$((removed_count + 1))
                
                # Remove empty directories
                local hook_dir="$HOOK_BASE/$hook_path"
                if [ -d "$hook_dir" ] && [ -z "$(ls -A "$hook_dir")" ]; then
                    rmdir "$hook_dir" 2>/dev/null || true
                fi
            else
                echo -e "  ${RED}✗${NC} Failed to remove: $hook_name"
            fi
        else
            echo -e "  ${YELLOW}⚠${NC} Not found: $hook_name"
        fi
    done
    
    # Remove config files
    for config_name in "${!config_files[@]}"; do
        IFS=' ' read -r config_path config_file <<< "${config_files[$config_name]}"
        local target_file="$HOOK_BASE/$config_path/$config_file"
        total_count=$((total_count + 1))
        
        if [ -f "$target_file" ]; then
            if rm "$target_file"; then
                echo -e "  ${GREEN}✓${NC} Removed: $config_name configuration"
                removed_count=$((removed_count + 1))
                
                # Remove empty directories
                local config_dir="$HOOK_BASE/$config_path"
                if [ -d "$config_dir" ] && [ -z "$(ls -A "$config_dir")" ]; then
                    rmdir "$config_dir" 2>/dev/null || true
                fi
            else
                echo -e "  ${RED}✗${NC} Failed to remove: $config_name configuration"
            fi
        else
            echo -e "  ${YELLOW}⚠${NC} Not found: $config_name configuration"
        fi
    done
    
    echo ""
    echo "=================================================="
    echo "           Uninstallation Summary"
    echo "=================================================="
    echo ""
    echo -e "Hooks removed: ${GREEN}$removed_count/$total_count${NC}"
    echo ""
    echo "PyLine will now use its built-in functionality for:"
    echo "  - Word counting"
    echo "  - Syntax highlighting" 
    echo "  - Search/replace"
    echo "  - Tab handling"
    echo "  - Text transformation"
    echo "  - Grammar checking (will use basic checking if available)"
    echo ""
    print_success "Uninstallation completed!"
}

uninstall_hooks
