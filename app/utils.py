import os

def join(path, name):
    return os.path.join(path, name)

def path_exists(path):
    return os.path.exists(path)
