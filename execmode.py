#----------------------------------------------------------------
# PyLine 0.1 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

import os
import dirops
from utils import prompt_continue

def execmode(original_destination):
    os.system('clear')
    choice_exec = None
    while choice_exec != 'q':
        current_dir = dirops.currentdir()
        print('Executable mode\n')
        print(f'Current working directory: {current_dir}\n')
        print('Menu: AF - All files, CWD - Change working directory, CDP - Change default path, MKDIR - Make directory, CLS - Clear screen, Q - Exit from exec mode\n')
        try:
            choice_exec = input('Your choice: ').lower()
            if choice_exec == 'af':
                os.system('clear')
                dirops.contentdir()    
            elif choice_exec == 'cwd':
                while True:
                    try:
                        new_dir = input('Enter the new directory path: ')
                        if new_dir == '0':
                            current_dir = dirops.cd(original_destination)
                        else:
                            try:
                                current_dir = dirops.cd(new_dir)
                            except OSError:
                                print('Invalid path or directory doesn\'t exist!\n')
                                prompt_continue()
                                continue
                            
                            print(f'Current working directory changed to: {current_dir}\n')
                            prompt_continue()
                            break
                        
                    except EOFError:
                        os.system('clear')
                        break
                    
            elif choice_exec == 'cdp':
                answer = None
                while answer != 'y':
                    answer = input('Would you like to change default path? [Y/N]: ').lower()
                    if answer == 'y':
                        try:
                            dirops.change_default_path(original_destination)
                        except OSError:
                            print('Invalid path or directory doesn\'t exist!\n')
                            prompt_continue()
                            continue
                        
                        current_dir = dirops.currentdir()
                        prompt_continue()
                        break
                    
                    elif answer == 'n':
                        print('Ok, won\'t change default path.\n')
                        prompt_continue()
                        break
                    
                    else:
                        print('Only Y/N!\n')
                        
            elif choice_exec == 'mkdir':
                answer = None
                while answer != 'y':
                    answer = input('Would you like to create a directory? [Y/N]: ').lower()
                    if answer == 'y':
                        while True:
                            try:
                                dir_name = input('\nEnter the name of a new directory: ')
                                try:
                                    if dirops.mkdir(dir_name):
                                        continue
                                    
                                except OSError:
                                    print('Error, directory must have a name!')
                                    prompt_continue()
                                    continue
                                
                                prompt_continue()
                                break
                            
                            except EOFError:
                                os.system('clear')
                                break
                            
                    elif answer == 'n':
                        print('Ok, I won\'t create any directory.')
                        prompt_continue()
                        break
                    
                    else:
                        print('Only Y/N!\n')
                        
            elif choice_exec == 'cls':
                os.system('clear')     
            elif choice_exec == 'q':
                os.system('clear')
                print('Returned from exec mode.\n')
                return current_dir

            else:
                os.system('clear')
                print('Only choices from the menu!\n')

        except:
            os.system('clear')
            print('Returned from exec mode.\n')
            return current_dir
