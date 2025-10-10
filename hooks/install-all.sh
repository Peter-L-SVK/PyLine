#!/usr/bin/env bash
# install-all-hooks.sh

set -e  # Exit on any error

echo "=================================================="
echo "    PyLine Hooks Master Installer"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Hook definitions with source directories
declare -A hooks=(
    ["smart_tab"]="input_handlers/edit_line smart_tab__90.py smart-tab" 
    ["word_counter"]="event_handlers/word_count word_counter__80.pl word-count"
    ["json_highlight"]="syntax_handlers/highlight json_highlight__60.py highlighters"
    ["shell_highlight"]="syntax_handlers/highlight shell_highlight__70.py highlighters"
    ["search_replace"]="event_handlers/search_replace search_replace__75.pl search_replace"
    ["grammar_checker"]="editing_ops/search_replace grammar_checker__70.py AI-grammar-check"
)

# Additional config files to install (non-executable)
declare -A config_files=(
    ["grammar_config"]="editing_ops/search_replace grammar_config.json AI-grammar-check"
)

# Base directories
HOOK_BASE="$HOME/.pyline/hooks"
BACKUP_DIR="$HOME/.pyline/hooks_backup_$(date +%Y%m%d_%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to backup existing hooks
backup_existing_hooks() {
    if [ -d "$HOOK_BASE" ]; then
        print_status "Backing up existing hooks to $BACKUP_DIR..."
        mkdir -p "$BACKUP_DIR"
        cp -r "$HOOK_BASE"/* "$BACKUP_DIR/" 2>/dev/null || true
        print_success "Backup completed"
    fi
}

# Function to install a single hook
install_hook() {
    local hook_name="$1"
    local hook_path="$2"
    local hook_file="$3"
    local source_dir="$4"
    
    local source_file="$SCRIPT_DIR/$source_dir/$hook_file"
    local target_dir="$HOOK_BASE/$hook_path"
    local target_file="$target_dir/$hook_file"
    
    print_status "Installing $hook_name..."
    
    # Check if source file exists
    if [ ! -f "$source_file" ]; then
        print_error "Source file $source_file not found for $hook_name"
        return 1
    fi
    
    # Create target directory
    if ! mkdir -p "$target_dir"; then
        print_error "Could not create directory $target_dir"
        return 1
    fi
    
    # Copy hook file
    if ! cp "$source_file" "$target_file"; then
        print_error "Could not copy $source_file to $target_dir"
        return 1
    fi
    
    # Set execute permissions
    if [[ "$hook_file" == *.pl || "$hook_file" == *.py || "$hook_file" == *.sh ]]; then
        if ! chmod +x "$target_file"; then
            print_error "Could not set execute permissions on $target_file"
            return 1
        fi
    fi
    
    print_success "$hook_name installed to $target_file"
    return 0
}

# Function to install config files (non-executable)
install_config_file() {
    local config_name="$1"
    local config_path="$2"
    local config_file="$3"
    local source_dir="$4"
    
    local source_file="$SCRIPT_DIR/$source_dir/$config_file"
    local target_dir="$HOOK_BASE/$config_path"
    local target_file="$target_dir/$config_file"
    
    print_status "Installing $config_name configuration..."
    
    # Check if source file exists
    if [ ! -f "$source_file" ]; then
        print_error "Source file $source_file not found for $config_name"
        return 1
    fi
    
    # Create target directory
    if ! mkdir -p "$target_dir"; then
        print_error "Could not create directory $target_dir"
        return 1
    fi
    
    # Copy config file
    if ! cp "$source_file" "$target_file"; then
        print_error "Could not copy $source_file to $target_dir"
        return 1
    fi
    
    print_success "$config_name configuration installed to $target_file"
    return 0
}

# Function to verify hook installation
verify_installation() {
    print_status "Verifying installations..."
    
    local all_ok=true
    
    # Verify executable hooks
    for hook_name in "${!hooks[@]}"; do
        IFS=' ' read -r hook_path hook_file source_dir <<< "${hooks[$hook_name]}"
        local target_file="$HOOK_BASE/$hook_path/$hook_file"
        
        if [ -f "$target_file" ]; then
            if [[ "$hook_file" == *.pl || "$hook_file" == *.py || "$hook_file" == *.sh ]]; then
                if [ -x "$target_file" ]; then
                    echo -e "  ${GREEN}✓${NC} $hook_name: installed and executable"
                else
                    echo -e "  ${RED}✗${NC} $hook_name: installed but not executable"
                    all_ok=false
                fi
            else
                echo -e "  ${GREEN}✓${NC} $hook_name: installed"
            fi
        else
            echo -e "  ${RED}✗${NC} $hook_name: NOT installed"
            all_ok=false
        fi
    done
    
    # Verify config files
    for config_name in "${!config_files[@]}"; do
        IFS=' ' read -r config_path config_file source_dir <<< "${config_files[$config_name]}"
        local target_file="$HOOK_BASE/$config_path/$config_file"
        
        if [ -f "$target_file" ]; then
            echo -e "  ${GREEN}✓${NC} $config_name: configuration installed"
        else
            echo -e "  ${RED}✗${NC} $config_name: configuration NOT installed"
            all_ok=false
        fi
    done
    
    if $all_ok; then
        print_success "All hooks and configurations verified successfully!"
    else
        print_warning "Some hooks or configurations may have installation issues"
    fi
}

# Function to test hooks
test_hooks() {
    print_status "Testing hooks functionality..."
    
    # Test word counter
    if [ -f "$SCRIPT_DIR/word-count/word_counter__80.pl" ]; then
        echo '{"action":"count_words","filename":"test.txt","file_content":"Hello world\nThis is a test"}' | perl "$SCRIPT_DIR/word-count/word_counter__80.pl" >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓${NC} Word counter: functional"
        else
            echo -e "  ${YELLOW}⚠${NC} Word counter: test failed"
        fi
    fi
    
    # Test JSON highlighter
    if [ -f "$SCRIPT_DIR/highlighters/json_highlight__60.py" ]; then
        python3 -c "import json; print('JSON highlighter imports OK')" >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓${NC} JSON highlighter: Python environment OK"
        else
            echo -e "  ${YELLOW}⚠${NC} JSON highlighter: Python check failed"
        fi
    fi
    
    # Test Grammar Checker dependencies
    if [ -f "$SCRIPT_DIR/AI-grammar-check/grammar_checker__70.py" ]; then
        python3 -c "import language_tool_python, pandas, numpy; print('Grammar checker dependencies OK')" >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓${NC} Grammar checker: All dependencies available"
        else
            echo -e "  ${YELLOW}⚠${NC} Grammar checker: Some dependencies missing"
            echo -e "     Run: pip install language-tool-python pandas numpy"
        fi
    fi
    
    # Test Perl availability
    if command -v perl >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Perl: available"
    else
        echo -e "  ${RED}✗${NC} Perl: NOT available (required for some hooks)"
    fi
    
    # Test Python availability
    if command -v python3 >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Python 3: available"
    else
        echo -e "  ${RED}✗${NC} Python 3: NOT available (required for some hooks)"
    fi
}

# Check if hook directories exist
check_directories_exist() {
    local missing_dirs=()
    
    for hook_name in "${!hooks[@]}"; do
        IFS=' ' read -r hook_path hook_file source_dir <<< "${hooks[$hook_name]}"
        local source_dir_path="$SCRIPT_DIR/$source_dir"
        if [ ! -d "$source_dir_path" ]; then
            missing_dirs+=("$source_dir")
        fi
    done
    
    for config_name in "${!config_files[@]}"; do
        IFS=' ' read -r config_path config_file source_dir <<< "${config_files[$config_name]}"
        local source_dir_path="$SCRIPT_DIR/$source_dir"
        if [ ! -d "$source_dir_path" ]; then
            missing_dirs+=("$source_dir")
        fi
    done
    
    if [ ${#missing_dirs[@]} -gt 0 ]; then
        print_error "Missing hook directories:"
        for dir in "${missing_dirs[@]}"; do
            echo "  - $dir"
        done
        echo ""
        echo "Expected directory structure:"
        echo "  $(pwd)/"
        echo "  ├── AI-grammar-check/"
        echo "  ├── highlighters/"
        echo "  ├── lower-to-upper/" 
        echo "  ├── search_replace/"
        echo "  ├── smart-tab/"
        echo "  └── word-count/"
        exit 1
    fi
}

# Check if hook files exist
check_files_exist() {
    local missing_files=()
    
    for hook_name in "${!hooks[@]}"; do
        IFS=' ' read -r hook_path hook_file source_dir <<< "${hooks[$hook_name]}"
        local source_file="$SCRIPT_DIR/$source_dir/$hook_file"
        if [ ! -f "$source_file" ]; then
            missing_files+=("$source_dir/$hook_file")
        fi
    done
    
    for config_name in "${!config_files[@]}"; do
        IFS=' ' read -r config_path config_file source_dir <<< "${config_files[$config_name]}"
        local source_file="$SCRIPT_DIR/$source_dir/$config_file"
        if [ ! -f "$source_file" ]; then
            missing_files+=("$source_dir/$config_file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_error "Missing hook files:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        echo ""
        echo "Please ensure all hook files are in their respective directories."
        exit 1
    fi
}

# Main installation function
main() {
    echo "This will install the following PyLine hooks:"
    echo ""
    for hook_name in "${!hooks[@]}"; do
        IFS=' ' read -r hook_path hook_file source_dir <<< "${hooks[$hook_name]}"
        echo "  - $hook_name: $source_dir/$hook_file → $HOOK_BASE/$hook_path/"
    done
    for config_name in "${!config_files[@]}"; do
        IFS=' ' read -r config_path config_file source_dir <<< "${config_files[$config_name]}"
        echo "  - $config_name: $source_dir/$config_file → $HOOK_BASE/$config_path/"
    done
    echo ""
    
    # Confirm installation
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    # Backup existing hooks
    backup_existing_hooks
    
    # Install all hooks
    local installed_count=0
    local total_count=0
    
    for hook_name in "${!hooks[@]}"; do
        IFS=' ' read -r hook_path hook_file source_dir <<< "${hooks[$hook_name]}"
        total_count=$((total_count + 1))
        
        if install_hook "$hook_name" "$hook_path" "$hook_file" "$source_dir"; then
            installed_count=$((installed_count + 1))
        fi
    done
    
    # Install all config files
    for config_name in "${!config_files[@]}"; do
        IFS=' ' read -r config_path config_file source_dir <<< "${config_files[$config_name]}"
        total_count=$((total_count + 1))
        
        if install_config_file "$config_name" "$config_path" "$config_file" "$source_dir"; then
            installed_count=$((installed_count + 1))
        fi
    done
    
    echo ""
    echo "=================================================="
    echo "           Installation Summary"
    echo "=================================================="
    echo ""
    echo -e "Hooks installed: ${GREEN}$installed_count/$total_count${NC}"
    echo ""
    
    # Verify installation
    verify_installation
    echo ""
    
    # Test functionality
    test_hooks
    echo ""
    
    # Final instructions
    echo "=================================================="
    echo "           Next Steps"
    echo "=================================================="
    echo ""
    echo "1. Restart PyLine or reload hooks for changes to take effect"
    echo "2. Test the hooks in PyLine:"
    echo "   - Use 'cw' command for word counting"
    echo "   - Edit .json files for JSON highlighting"
    echo "   - Edit .sh files for shell highlighting"
    echo "   - Use search/replace functionality"
    echo "   - Press Tab in edit mode for smart indentation"
    echo "   - Open any text file for AI grammar checking"
    echo ""
    echo "3. For AI Grammar Checker, install dependencies:"
    echo "   - pip install language-tool-python pandas numpy"
    echo ""
    echo "4. If you encounter issues:"
    echo "   - Check that all hook files are executable"
    echo "   - Verify Perl and Python are installed"
    echo "   - Review the backup in: $BACKUP_DIR"
    echo ""
    
    if [ $installed_count -eq $total_count ]; then
        print_success "All hooks installed successfully! Enjoy using PyLine with enhanced functionality."
    else
        print_warning "Some hooks may not be installed correctly. Check the output above."
    fi
}

# Run pre-flight checks
print_status "Running pre-flight checks..."
check_directories_exist
check_files_exist

# Start installation
main
