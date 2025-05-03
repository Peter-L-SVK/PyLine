#----------------------------------------------------------------
# PyLine 0.1 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

import os

def currentdir():
    #Get the current working directory.
    return os.getcwd()

def contentdir():
    #List the contents of the current directory.
    print('Current directory content is: ')
    
    with os.scandir() as entries:
        # Create list of entries and sort with dirs first then alphabetical
        sorted_entries = sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower()))
        for entry in sorted_entries:
            if entry.is_dir():
                print(entry.name, '-dir')
            elif entry.is_file():
                print(entry.name)
    print('\n')

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
        print('Directory or file named', dir_name, 'already exists!\n')
        return 1

def original_path(original_dir):
    #Save the original directory path to a file.
    with open('defaultpath.dat', 'w') as f:
        f.write(original_dir)

def original_destination():
    #Retrieve the original directory path from a file.
    with open('defaultpath.dat', 'r') as f:
        original_destination = f.readline().strip()
    return original_destination

def safe_path(original_destination):
    #Save the current directory path to a file.
    cd(original_destination)
    with open('path.dat', 'w') as f:
        f.write(original_destination)

def default_path(original_destination):
    #Set the default directory path.
    try:
        with open('path.dat', 'r') as f:
            default_destination = f.readline().strip()
    except OSError:
        with open('defaultpath.dat', 'r') as f:
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
    #Change the default directory path.
    try:
        new_default_path = input('Enter the new path: ')
        if new_default_path != '0':
            cd(new_default_path)
        else:
            cd(original_destination)
    
            new_current_path = currentdir()
            with open('path.dat', 'w') as f:
                f.write(new_current_path)
                print('Default path set to:', new_current_path, '\n')
    except EOFError:
        os.system('clear')

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
