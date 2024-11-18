import uuid
from io import BytesIO

from PIL import Image


def get_pic_type(file_stream):
    try:
        img = Image.open(BytesIO(file_stream))
        return img.format if img.format else "jpeg"
    except IOError:
        return "unknown"

def send_file_name():
    return uuid.uuid4().hex