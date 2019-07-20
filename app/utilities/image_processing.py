import os
from PIL import Image

## FIX WITH CONFIG FILE
BASEPATH = "data/"

def process_image(image):
    # with Image.open(image) as im:
        # format = im.format
    format = ""
    size = 0
    # image.seek(0, os.SEEK_END)
    # size = image.tell()
    return size, format

def save_image(f, image):
    full_filepath = os.path.join(BASEPATH, image.filepath)
    if os.path.exists(full_filepath):
        raise Exception("Cannot save image. The filepath already exists")
    os.makedirs(os.path.dirname(full_filepath), exist_ok=True)
    f.save(full_filepath)
    
