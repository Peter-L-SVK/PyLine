#----------------------------------------------------------------
# PyLine 0.9.7 - Info Screen (GPLv3)
# Copyright (C) 2018-2025 Peter Leukanič
# License: GNU GPL v3+ <https://www.gnu.org/licenses/gpl-3.0.txt>
# This is free software with NO WARRANTY.
#----------------------------------------------------------------

import os

def print_info():
    print('\n        #####################################################################')
    print('        # PyLine 0.9.7 for Linux/BSD - Command-line text editor in Python3. #')
    print('        #                Created by Peter Leukanič 2018-2025.               #')
    print('        #               This program is under GNU GPL v3 License.           #')
    print('        #                  Feel free to distribute and modify.              #')
    print('        #####################################################################\n')

def print_license_parts(original_destination):
    install_path = "/usr/local/bin"
    install_license = "/usr/share/licenses/PyLine"
    print("\n        For full license details, see the LICENSE file in:")
    
    # Check if LICENSE exists in install_path
    license_path = os.path.join(install_license, "LICENSE")
    if os.path.exists(license_path):
        print(f"        {license_path}")
    else:
        os.chdir(original_destination + '/..')
        new_path = os.getcwd()
        print(f"        {os.path.join(new_path, 'LICENSE')}")
    
    print("\n        Brief excerpt:")
    # Check license-parts.txt in install_path first
    parts_path = os.path.join(install_path, "license-parts.txt")
    if os.path.exists(parts_path):
        try:
            with open(parts_path, 'r') as f:
                print(f.read())
        except OSError:
            print("License excerpt not found in installation directory.\n")
    else:
        # Fallback to original_destination/src/license-parts.txt
        fallback_path = os.path.join(original_destination, "license-parts.txt")
        try:
            with open(fallback_path, 'r') as f:
                print(f.read())
        except OSError:
            print("License excerpt not found in source directory.\n")
