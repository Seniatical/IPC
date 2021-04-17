"""
MIT License

Copyright (c) 2021 Seniatical

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
    
