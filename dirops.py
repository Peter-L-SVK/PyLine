import os

def currentdir():
    #Get the current working directory.
    return os.getcwd()

def contentdir():
    #List the contents of the current directory.
    print('Current directory content is: ')
    current_dir_cont = currentdir()
    for r, d, f in os.walk(current_dir_cont):
        for dirs in d:
            print(dirs, '-dir')
    
    with os.scandir() as i:
        for entry in i:
            if entry.is_file():
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
