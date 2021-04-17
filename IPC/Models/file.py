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

from os import path
from io import(
    IOBase, BytesIO
    )
from typing import Union

class File:
    def __init__(self, raw: Union[bytes, str, IOBase], filename: str = None):
        self.raw = raw
        self.path = raw if type(raw) == str else filename if filename else None

        if isinstance(raw, IOBase):
            if not (raw.seekable() and raw.readable()):
                raise ValueError('The file buffer should be readable/seekable')

            self.data = raw.read()
            self.raw = raw
            self.__original_position = raw.tell()

        elif isinstance(raw, bytes):
            io = BytesIO(raw)
            self.raw = io
            self.data = raw
            self.__original_position = io.tell()

        else:
            file = open(raw, 'rb')
            self.__original_postion = 0
            self.data = file.read()
            self.raw = file

        if filename is None:
            
            if isinstance(raw, str):
                raw_path, self.filename = path.split(raw)
                self.path = raw
                
            else:
                self.filename = getattr(raw, 'name', None)
                if not self.filename:
                    raise ValueError('The file buffer is missing a filename')
                    
        else:
            self.filename = filename

    def size(self):
        return len(BytesIO(self.raw.read()).getbuffer())
