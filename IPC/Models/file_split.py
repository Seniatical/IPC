from typing import Union
from _io import (
    FileIO, BytesIO
    )
from .file import File

def split(file: Union[bytes, str, File, FileIO, BytesIO], buffer_size: int) -> list:
    if isinstance(file, bytes):
        ## Just send it through BytesIO
        file = BytesIO(file)
    if isinstance(file, str):
        ## Could be file path OR the content
        ## If we can't open the file we just convert it to bytes and BytesIO it
        try:
            file = FileIO(file)
        except OSError:
            file = BytesIO(file.encode('utf-8'), errors='ignore')

    if isinstance(file, File):
        file = file.raw

    file.seek(0)

    parts = []

    contents = file.read()

    buffers, extra = divmod(len(contents), buffer_size)

    for i in range(1, (buffers + (1 if extra == 0 else 2))):
        parts.append(contents[(buffer_size * (i - 1)): (buffer_size * i)])
    return parts
    
