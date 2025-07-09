#!/usr/bin/env python3

#----------------------------------------------------------------
# PyLine 0.7 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

# Standard library imports
import os
import signal
import sys

# Local application imports
import dirops
import execmode
import utils
from text_buffer import TextBuffer

def main():
    # Register signal handler (for OS-level interrupts)
    signal.signal(signal.SIGINT, utils.handle_sigint)

    os.system('clear')
    original_dir = dirops.currentdir()
    dirops.original_path(original_dir)
    original_destination = dirops.original_destination()
    dirops.default_path(original_destination)
    current_dir = dirops.currentdir()

    args = utils.parse_arguments()
    buffer = TextBuffer()

    print('PyLine 0.7 - (GPLv3) for Linux/BSD  Copyright (C) 2018-2025  Peter Leukanič')
    print('This program comes with ABSOLUTELY NO WARRANTY; for details type \'i\'.\n')
        
    try:
        if args.info:
            utils.show_info(original_destination)
            return
            
        if args.filename:  # File specified via command line
            filepath = os.path.abspath(args.filename)
            
            if os.path.exists(filepath):
                if buffer.load_file(filepath):
                    buffer.edit_interactive()
                else:
                    print(f"Error: Could not load {filepath}")
            else:
                # Create directory structure if needed
                if dirops.ensure_directory_exists(filepath):
                    print(f"Creating new file: {filepath}")
                    buffer.filename = filepath
                    buffer.edit_interactive()
                else:
                    print("Failed to create directory structure")
            utils.clean_exit()
            
        
        choice = None
        while choice != 'q':
            buffer = TextBuffer()
            print(f'Current working directory: {current_dir}\n')
            print('Menu: 1 - Existing file, 2 - New file, 3 - Truncate or new file,\n '
                  '     CLS - Clear screen, CW - Count words, X - Exec mode, I - Info, Q - Quit\n')
            
            try:
                choice = input('Your choice: ').lower()
                
                if choice == '1':
                    handle_existing_file(buffer)
                elif choice == '2':
                    handle_new_file(buffer)
                elif choice == '3':
                    handle_truncate_file(buffer)
                elif choice == 'cw':
                    count_words()
                elif choice == 'x':
                    current_dir = execmode.execmode(original_destination)
                elif choice == 'cls':
                    os.system('clear')
                elif choice == 'i':
                    utils.show_info(original_destination)
                elif choice == 'q':
                    break
                else:
                    os.system('clear')
                    print('Only choices from the menu!\n')
                    
            except EOFError:
                os.system('clear')
                print('\nTo quit, enter Q !\n')
                continue
                
    except KeyboardInterrupt:
        pass # Passing the interupt signal
        
    utils.clean_exit()

def count_words():
    os.system('clear')
    answer = None
    while answer != 'y':
        answer = input('Would you like to count words in the file? [Y/N]: ').lower()
        if answer == 'y':
            while True:
                dirops.contentdir()
                name_of_file = input('\nEnter the name of file to count words: ')
                if not name_of_file:
                    os.system('clear')
                    print('Error, file must have a name!\n')
                    continue

                num_of_words, num_of_lines, num_of_chars = dirops.count_words_in_file(name_of_file)
                if not num_of_words == 'error':                    
                    print('************************************************************')
                    print(f"{name_of_file} contains:")
                    print(f"- {num_of_words} words")
                    print(f"- {num_of_lines} lines") 
                    print(f"- {num_of_chars} characters")
                    print('************************************************************\n')
                    break
                
                else:
                    print('\n')
                    break
                
        elif answer == 'n':
            print('Ok, won\'t count anything.\n')
            utils.prompt_continue()
            break
        
        else:
            print('Only Y/N!\n')

def handle_existing_file(buffer):
    os.system('clear')
    answer = None
    while answer != 'y':
        answer = input('Would you like to edit the file? [Y/N]: ').lower()
        if answer == 'y':
            while True:
                dirops.contentdir()
                name_of_file = input('\nEnter the name of file to edit: ')
                if not name_of_file:
                    os.system('clear')
                    print('Error, file must have a name!\n')
                    continue
                
                if buffer.load_file(name_of_file):
                    buffer.edit_interactive()
                    utils.prompt_continue()
                    break

                else:
                    os.system('clear')
                    print(f'No file with name: {name_of_file}!\n')
                    continue                   

        elif answer == 'n':
            print('Ok, won\'t edit anything.\n')
            utils.prompt_continue()
            break

        else:
            print('Only Y/N!\n')

def handle_new_file(buffer):
    os.system('clear')
    answer = None
    while answer != 'y':
        answer = input('Would you like to create the new file? [Y/N]: ').lower()
        if answer == 'y':
            while True:
                dirops.contentdir()
                name_of_file = input('Enter the name of file to create: ')
                os.system('clear')
                if not name_of_file:
                    print('Error, file must have a name!\n')
                    continue
                
                buffer.filename = name_of_file
                 # Get save status from editor
                save_status = buffer.edit_interactive()
                
                # Only show additional message if editor didn't handle saving
                if save_status is None and buffer.dirty:
                    if buffer.save():
                        print('File edited and saved.')
                    else:
                        print('Error: Failed to save file!')
                elif save_status is None:
                    print('No changes made to file.')

                utils.prompt_continue()
                break
                
        elif answer == 'n':
            print('Ok, won\'t create anything.\n')
            utils.prompt_continue()
            break      

        else:
            print('Only Y/N!\n')

def handle_truncate_file(buffer):
    os.system('clear')
    answer = None
    while answer != 'y':
        answer = input('Would you like to create/truncate the file? [Y/N]: ').lower()
        if answer == 'y':
            while True:
                dirops.contentdir()
                name_of_file = input('Enter the name of file to create or to truncate: ')
                if not name_of_file:
                    os.system('clear')
                    print('Error, file must have a name!\n')
                    continue
                
                buffer.filename = name_of_file
                buffer.lines = []  # Truncate by clearing buffer
                buffer.dirty = True  # Mark as dirty immediately after truncation
                
                # Get save status from editor
                save_status = buffer.edit_interactive()
                
                # Only show additional message if editor didn't handle saving
                if save_status is None and buffer.dirty:
                    if buffer.save():
                        print('File truncated/edited and saved.')
                    else:
                        print('Error: Failed to save file!')
                elif save_status is None:
                    print('No changes made to file.')

                utils.prompt_continue()
                break
            
        elif answer == 'n':
            print('Ok, won\'t create anything.\n')
            utils.prompt_continue()
            break        

        else:
            print('Only Y/N!\n')

if __name__ == "__main__":
    main()
