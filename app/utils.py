import shutil
import os

def join(path, name):
    return os.path.join(path, name)

def path_exists(path):
    return os.path.exists(path)

def move(path, destination):
    return shutil.move(path, destination)

def remove(path):
    os.remove(path)

# Removes directory and all children
def remove_directory(path):
    shutil.rmtree(path)

# Removes empty directory
def remove_dir(path):
    os.rmdir(path)