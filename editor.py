#!/usr/bin/env python3

# PyLine 0.1 - Line editor (GPLv3)
# Copyright (C) 2018 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.

import signal
import time
import sys
import os
import dirops
import execmode
import info
from textbuffer import TextBuffer

def main():
    # Register signal handler (for OS-level interrupts)
    signal.signal(signal.SIGINT, handle_sigint)

    os.system('clear')
    original_dir = dirops.currentdir()
    dirops.original_path(original_dir)
    original_destination = dirops.original_destination()
    dirops.default_path(original_destination)
    current_dir = dirops.currentdir()
    
    print('PyLine 0.1 - (GPLv3) for Linux/BSD  Copyright (C) 2018  Peter Leukanič')
    print('This program comes with ABSOLUTELY NO WARRANTY; for details type \'i\'.\n')
    
    try:
        choice = None
        while choice != 'q':
            buffer = TextBuffer()
            print(f'Current working directory: {current_dir}\n')
            print('Menu: 1 - Existing file, 2 - New file, 3 - Truncate or new file, '
                  'CLS - Clear screen, CW - Count words, X - Exec mode, I - Info, Q - Quit\n')
            
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
                    show_info(original_destination)
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
        pass
        
    clean_exit()

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

                num_of_words = dirops. count_words_in_file(name_of_file)
                if not num_of_words == 0:
                    print('************************************************************')
                    print(name_of_file,'contains exactly', num_of_words,'words.')
                    print('************************************************************\n')
                    break
                else:
                    break
                
        elif answer == 'n':
            print('Ok, won\'t count anything.\n')
            prompt_continue()
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
                    prompt_continue()
                    break
                else:
                    print(f'No file with name: {name_of_file}!\n')
                    continue                   
        elif answer == 'n':
            print('Ok, won\'t edit anything.\n')
            prompt_continue()
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

                prompt_continue()
                break
                
        elif answer == 'n':
            print('Ok, won\'t create anything.\n')
            prompt_continue()
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

                prompt_continue()
                break
            
        elif answer == 'n':
            print('Ok, won\'t create anything.\n')
            prompt_continue()
            break        
        else:
            print('Only Y/N!\n')

def show_info(original_destination):
    os.system('clear')
    info.print_info()
    info.print_license_parts(original_destination)
    print('\n')

def prompt_continue():
    os.system('read -p "Press enter to continue..."')
    os.system('clear')

def handle_sigint(signum, frame):
    sys.stdout.write('\nProgram interrupted. Exiting gracefully...\n')
    sys.stdout.flush()
    sys.exit(128 + signum)
    
def clean_exit():
    os.system('clear')
    print('\nProgram closed.\n')
    prompt_continue()
    sys.exit(0)

if __name__ == "__main__":
    main()
