#!/usr/bin/env python3

import sys
import os
import dirops
import execmode
import info
from textbuffer import TextBuffer

def main():
    os.system('clear')
    original_dir = dirops.currentdir()
    dirops.original_path(original_dir)
    original_destination = dirops.original_destination()
    dirops.default_path(original_destination)
    current_dir = dirops.currentdir()
    print('PyLine 0.1 for Linux/BSD  Copyright (C) 2018  Peter Leukanič')
    print('This program comes with ABSOLUTELY NO WARRANTY; for details type \'i\'.\n')
    
    choice = None
    while choice != 'q':
        buffer = TextBuffer()
        print('Current working directory: ', current_dir, '\n')
        print('Menu: 1 - Existing file, 2 - New file, 3 - Trunkate or new file, CLS - Clear screen, X - Exec mode, I - Info, Q - Quit\n')
        try:
            choice = input('Your choice: ').lower()
            
            if choice == '1':
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
                                os.system('clear')
                                break
                            else:
                                print('No file with name:', name_of_file, '!\n')
                                continue
                            
                    elif answer == 'n':
                        print('Ok, won\'t edit anything.\n')
                        os.system('read -p "Press enter to continue..."')
                        os.system('clear')
                        break
                    
                    else:
                        print('Only Y/N!\n')
                        
            elif choice == '2':
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
                            buffer.edit()
                            if buffer.dirty:
                                if buffer.save():
                                    print('File created and saved.')
                                else:
                                    print('Error creating file!')
                                    os.system('read -p "Press enter to continue..."')
                                    os.system('clear')
                                    break
                                
                            elif answer == 'n':
                                print('Ok, won\'t create anything.\n')
                                os.system('read -p "Press enter to continue..."')
                                os.system('clear')
                                break
                            
                            else:
                                print('Only Y/N!\n')
                                
            elif choice == '3':
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
                            buffer.edit()
                            if buffer.save():
                                print('File', name_of_file, 'created / truncated.')
                            else:
                                print('Error saving file!')
                                os.system('read -p "Press enter to continue..."')
                                os.system('clear')
                                break
                            
                    elif answer == 'n':
                        print('Ok, won\'t create/truncate anything.\n')
                        os.system('read -p "Press enter to continue..."')
                        os.system('clear')
                        break
                    
                    else:
                        print('Only Y/N!\n')
                                
            elif choice == 'x':
                current_dir = execmode.execmode(original_destination)
                
            elif choice == 'cls':
                os.system('clear')
                
            elif choice == 'i':
                os.system('clear')
                info.print_info()
                info.print_license_parts(original_destination)
                print('\n')
                
            elif choice == 'q':
                break
            
            else:
                os.system('clear')
                print('Only choices from the menu!\n')

        except EOFError:
            os.system('clear')
            print('\nTo quit, enter Q !\n')
            continue

    os.system('clear')
    print('\nProgram closed.\n')
    os.system('read -p "Press enter to continue..."')
    os.system('clear')
    sys.exit(0)

if __name__ == "__main__":
    main()
