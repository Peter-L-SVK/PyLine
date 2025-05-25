#----------------------------------------------------------------
# PyLine 0.5 - Line editor (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

import os

def print_info():
    print('\n        ####################################################################')
    print('        # PyLine 0.5 for Linux/BSD - Command-line text editor in Python3.  #')
    print('        #                Created by Peter Leukanič 2018-2025.              #')
    print('        #               This program is under GNU GPL v3 License.          #')
    print('        #                  Feel free to distribute and modify.             #')
    print('        ####################################################################\n')

def print_license_parts(original_destination):
    print("\n        For full license details, see the LICENSE file in:")
    print(f"        {original_destination}/LICENSE")
    print("\n        Brief excerpt:")
    total_path = os.path.join(original_destination, 'license-parts.txt')
    try:
        with open(total_path, 'r') as f:
            for line in f:
                print(line, end='')
    except OSError:
        print('License file not found.\n')
