#----------------------------------------------------------------
# PyLine 0.1 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

import os
import sys
import signal
import time
import info

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
    sys.exit(128 + signum) #In case of Ctrl+C, 128+2 as defined by POSIX
    
def clean_exit():
    os.system('clear')
    print('\nProgram closed.\n')
    prompt_continue()
    sys.exit(0)
