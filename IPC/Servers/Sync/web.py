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

import socket
from ...exceptions import (ServerStartupError,
                           ServerNotRunningError,
                           SendingError
                           )
from os import remove
import json
import re
from io import BytesIO


class WebClient:
    def __init__(self, host, port, secret_key=None):
        self.port = port
        self.host = host
        self.key = secret_key
        self.BUFFER_SIZE = 1024

        self.packet_transfer_pattern = re.compile(r'FILE?:\|\|(?:[a-z]{1, 50})?.+\|\|[0-9]+')
        ## Recognises that a file is about to be transferred

        try:
            self.sock = socket.create_connection((self.host, self.port))
            print('\x1b[32m [ + ] Connected to server')
        except Exception as error:
            ## Only ever raised when your app isn't running
            raise ServerNotRunningError() from error

    def fetch(self, event_name: str, *args, **kwargs):
        ## Used to get a recourse from your application
        ## Allows some extra information to be passed on
        method = kwargs.get('method')

        if type(method) != str and method != None:
            raise TypeError('Request method must be a string not {!r}'.format(method.__class__.__name__))

        if method:
            kwargs.pop('method')

        path = kwargs.get('path')
        if path:
            kwargs.pop('path')

        raw_json = {
            't': method or 'GET',
            'a': str(self.key),
            'e': event_name,
            'args': args,
            'kwargs': kwargs
        }
        ## Helps reduce the packet size
        ## Orientation
        r"""
        t -> Type of request
        a -> authorization
        e -> event to call
        """
        address = (self.host, self.port)

        try:
            try:
                self.sock.sendall(json.dumps(raw_json).encode('utf-8'))
            except OSError:
                ## Socket get put down for some reason
                self.sock = socket.create_connection((self.host, self.port))
                self.sock.sendall(json.dumps(raw_json).encode('utf-8'))

            print('\x1b[32m [ + ] Sent request to server')
        except Exception as error:
            raise SendingError() from error

        while True:

            try:
                data = self.sock.recv(self.BUFFER_SIZE).decode()
            except Exception:
                print('\x1b[31m [ - ] Target server rejected response')
                break

            if not data:
                print('\x1b[31m [ - ] Rejected response - No data sent with packet')
                break

            print('\x1b[32m [ + ] Accepted connection from {!r}'.format(address))

            if address != (self.host, self.port):
                print('\x1b[31m [ - ] Rejected response from {!r} - Incorrect address'.format(address))
                break

            is_file = self.packet_transfer_pattern.match(data)
            if is_file:
                ## File format should be - FILE:||Filename||number-of-packets
                ## Filename can include the directory but the file should be at the end of the directory

                actual_find = is_file.group()
                parted = actual_find.split('||')
                filename = parted[1]
                packets = int(parted[-1])

                path = path or filename

                print('\x1b[32m [ + ] Preparing to save {!r} with a total of {!r} packets'.format(filename, packets))

                try:
                    with open(path, 'wb') as f:

                        while True:
                            file = self.sock.recv(self.BUFFER_SIZE)

                            if not file:
                                break
                            f.write(file)

                    file_data = open(path, 'rb').read()

                    if not file_data:
                        remove(filename)
                        print('\x1b[31m [ - ] Failed to transfer file')
                        break

                except OSError as error:
                    print('\x1b[31m [ - ] Failed to open/write to file - {!r}'.format(error))
                    break

                print('\n\x1b[32m [ + ] Saved file {!r}'.format(filename))

                return BytesIO(file_data)

            else:
                return data
