import shutil
import os
from werkzeug.utils import secure_filename as sf

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

def secure_filename(name):
    return sf(name)

def size(path):
    return os.path.getsize(path)