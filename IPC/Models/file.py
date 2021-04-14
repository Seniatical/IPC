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

'''
class File:
    def __init__(self, raw, filename=None):
        self.raw = raw
        self.path = raw if type(raw) == str else filename if filename else None

        if isinstance(raw, IOBase):
            
            if not (raw.seekable() and raw.readable()):
                raise ValueError('The file buffer should be readable/seekable')
            
            self.raw = raw
            self.__original_position = raw.tell()

        elif isinstance(raw, bytes):
            io = BytesIO(raw)
            self.raw = io
            self.__original_position = io.tell()
            
        else:
            self.raw = open(raw, 'rb')  ## We want the raw binary because thats what were sending across the stream
            self.__original_position = 0

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

        self.as_io = BytesIO(self.raw.read())

    def reset(self, seek=True):
        if seek:
            self.raw.seek(self._original_pos)
        else:
            self.raw = b''

    def size(self):
        return len(BytesIO(self.raw.read()).getbuffer())

    def close(self):
        self.raw.close()

    def raw_data(self):
        return self.raw.read()

    def raw_buffer(self):
        return self.raw
'''
