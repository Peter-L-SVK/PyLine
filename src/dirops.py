#----------------------------------------------------------------
# PyLine 0.6 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

# Standard Library imports
import os
from shutil import rmtree
from pathlib import Path

path_to_config = Path.home() / ".pyline"
path_to_config.mkdir(exist_ok=True) 

def currentdir():
    #Get the current working directory.
    return os.getcwd()

def contentdir():
    """List directory contents with enhanced formatting and colored output"""
    print('\nCurrent directory contents:\n')
    
    # ANSI color codes (keeping your requested colors)
    DIR_COLOR = '\033[1;94m'         #Bold Blue for directories
    EXEC_COLOR = '\033[38;5;28m'   # Dark Green for executables
    SYM_COLOR = '\033[95m'         # Magenta for symlinks
    RESET_COLOR = '\033[0m'
    
    # Column formatting
    COLUMN_WIDTH = 28
    ITEMS_PER_ROW = 3
    
    with os.scandir() as entries:
        # Sort directories first, then alphabetically
        sorted_entries = sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower()))
        
        entries_with_length = []
        for entry in sorted_entries:
            name = entry.name
            if entry.is_symlink():
                target = os.readlink(entry.path)
                colored = f"{SYM_COLOR}{name} → {target}{RESET_COLOR}"
                raw_length = len(name) + len(target) + 2  # +2 for arrow/spaces
            elif entry.is_dir():
                colored = f"{DIR_COLOR}{name}{RESET_COLOR}"
                raw_length = len(name)
            elif os.access(entry.path, os.X_OK):
                colored = f"{EXEC_COLOR}{name}{RESET_COLOR}"
                raw_length = len(name)
            else:
                colored = name
                raw_length = len(name)
            
            entries_with_length.append((colored, raw_length))
        
        # Calculate padding for each entry
        formatted_entries = []
        for text, length in entries_with_length:
            padding = ' ' * (COLUMN_WIDTH - length) if length < COLUMN_WIDTH else ''
            formatted_entries.append(f"{text}{padding}")
        
        # Print in columns
        for i in range(0, len(formatted_entries), ITEMS_PER_ROW):
            row = formatted_entries[i:i+ITEMS_PER_ROW]
            print('  '.join(row))
    
    print()  # Extra newline for spacing

def cd(new_dir):
    #Change the current working directory.
    os.chdir(new_dir)
    return currentdir()
    
def mkdir(dir_name):
    #Create a new directory.
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
        print('Directory', dir_name, 'created.\n')
    else:
        print('Directory named', dir_name, 'already exists!\n')
        return 1

def rmfile(file_name):
    #Remove a file.
    if os.path.isfile(file_name):
        os.remove(file_name)
        print('File', file_name, 'deleted.\n')
    else:
        print('File', file_name, 'doesn\'t exists!\n')
        return 1
        
def rmdir(dir_name):
    #Remove a directory.
    if os.path.isdir(dir_name):
        rmtree(dir_name)
        print('Directory', dir_name, 'deleted.\n')
    else:
        print('Directory named', dir_name, 'doesn\'t exists!\n')
        return 1
    
def original_path(original_dir):
    """Save the original directory path to a file."""
    try:
        with open(path_to_config / 'defaultpath.dat', 'w') as f:
            f.write(original_dir)
    except IOError as e:
        print(f"Error saving path: {e}")
        return 1

def original_destination():
    """Retrieve the original directory path from a file."""
    try:
        with open(path_to_config / 'defaultpath.dat', 'r') as f:
            return f.readline().strip()
    except FileNotFoundError:
        return os.getcwd()  # Return current dir if file doesn't exist
    except IOError as e:
        print(f"Error reading path: {e}")
        return os.getcwd()

def safe_path(original_destination):
    #Save the current directory path to a file.
    cd(original_destination)
    with open(path_to_config / 'path.dat', 'w') as f:
        f.write(original_destination)

def default_path(original_destination):
    #Set the default directory path.
    try:
        with open(path_to_config / 'path.dat', 'r') as f:
            default_destination = f.readline().strip()
    except OSError:
        with open(path_to_config / 'defaultpath.dat', 'r') as f:
            default_destination = f.readline().strip()

    if default_destination == original_destination:
        cd(original_destination)
    elif default_destination is None:
        safe_path(original_destination)
    else:
        try:
            cd(default_destination)
        except OSError:
            safe_path(original_destination)

def change_default_path(original_destination):
    """Change the default directory path."""
    try:
        new_default_path = input('Enter the new path (or 0 to reset): ').strip()
        target_path = original_destination if new_default_path == '0' else new_default_path
        
        if not os.path.exists(target_path):
            print(f"Error: Path '{target_path}' doesn't exist")
            return 1
            
        os.chdir(target_path)
        with open(path_to_config / 'path.dat', 'w') as f:
            f.write(target_path)
        print(f'Default path set to: {target_path}\n')
        
    except EOFError:
        os.system('clear')
    except Exception as e:
        print(f"Error changing path: {e}")
        return 1

def count_words_in_file(filename):
    """
    Count the number of words in a text file with improved punctuation handling.
    
    Args:
        filename (str): Path to the file to be read.
        
    Returns:
        tuple: (word_count, line_count, char_count) or (error, 0, 0) on error
    """
    try:
        with open(filename, 'r') as file:
            line_count = 0
            word_count = 0
            char_count = 0
            
            for line in file:
                line_count += 1
                char_count += len(line)
                # Split on whitespace and filter out empty strings
                words = [word.strip(",.!?;:\"\'()[]") for word in line.split() if word]
                word_count += len(words)
            os.system('clear')
            return word_count, line_count, char_count
            
    except FileNotFoundError:
        os.system('clear')
        print(f"Error: File '{filename}' not found.")
        return 'error', 0, 0

    except Exception as e:
        os.system('clear')
        print(f"An error occurred: {e}")
        return 'error', 0, 0
