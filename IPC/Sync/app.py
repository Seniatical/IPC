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
from ..exceptions import (ServerStartupError,
                          ServerNotRunningError,
                          DuplicateCall,
                          SendingError
                          )
from ..Models import (
    File, split
    )
import sys
import json
import inspect

class AppClient:

    def __init__(self, host, port, secret_key = None, close_on_rejection = False, close_on_completion = True):
        ## If your secret_key is None anybody can make a request to the running server without any auth
        ## close_on_rejection shuts down the connection if any of requests made are invalid
        ## I will add a configurable option soon
        
        self.server = None
        
        self.host = host
        self.port = port
        self.as_tuple = (host, port)
        self.key = str(secret_key)
        self.close_on_rejection = close_on_rejection
        self.close_on_completion = close_on_completion
        self.BUFFER_SIZE = 1024

        self.calls = {}
        self.__allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

        print('\x1b[32m [ + ] Server IP {!r} | Port {!r} - Sync Client'.format(self.host, self.port))

    @property
    def get_info(self):
        return {
            'host': self.host,
            'port': self.port,
            'secret-key': self.key
            }

    @property
    def kill(self):
        server = self.server
        if not server:
            raise ServerNotRunningError('Server is not running')
        server.shutdown(socket.SHUT_RDWR)
        
        print('\x1b[31m [ - ] Killed Running Process')

    def start_server(self):
        ## Start your app server
        ## Your web app will both recieve and send requests to here
        try:
            server = socket.create_server(self.as_tuple, family=socket.AF_INET)
            print('\x1b[32m [ + ] Started up server')
        except OSError as error:
            raise ServerStartupError() from error
        self.server = server
        return server

    def monitor(self):
        server = self.server
        if not server:
            raise ServerNotRunningError('Server is not running')

        print('\x1b[32m [ + ] Server is now accepting requests')
        
        while True:
            server.listen(1)
            ## Because this is just a web-server and an application we only listen for 1 client

            conn, address = server.accept()

            print('\x1b[32m [ + ] Accepted connection from {!r}'.format(address))

            data = conn.recv(1024).decode()
            
            if not data:
                print('\x1b[31m [ - ] Rejected Request from {!r} - No Data Supplied'.format(address))
                if self.close_on_rejection:
                    conn.close()
                continue

            try:
                real_data = json.loads(data)
            except Exception:
                ## Failed to parse the data into a dict
                print('\x1b[31m [ - ] Rejected Request from {!r} - Invalid Formatting'.format(address))
                if self.close_on_rejection:
                    conn.close()
                continue

            if ('a' not in real_data or not real_data.get('a')) and self.key:
                print('\x1b[31m [ - ] Rejected Request from {!r} - No authorization provided for the request'.format(address))
                if self.close_on_rejection:
                    conn.close()
                continue
            if real_data.get('a') != self.key:
                print('\x1b[31m [ - ] Rejected Request from {!r} - Incorrect Authorization'.format(address))
                if self.close_on_rejection:
                    conn.close()
                continue

            request_type = real_data.get('t')
            if not request_type:
                request_type = 'GET'
                ## Benefit of the doubt

            event_to_call = real_data.get('e')
            if not event_to_call:
                print('\x1b[31m [ - ] Rejected Request from {!r} - Event to call wasn\'t provided'.format(address))
                if self.close_on_rejection:
                    conn.close()
                continue

            raw_event = self.calls.get(event_to_call)
            if not raw_event:
                print('\x1b[31m [ - ] Rejected Request from {!r} - Event to call cannot be found'.format(address))
                if self.close_on_rejection:
                    conn.close()
                continue

            function = raw_event[0]
            methods = raw_event[1]

            if request_type not in methods:
                print('\x1b[31m [ - ] Rejected Request from {!r} - Incorrect Method'.format(address))
                if self.close_on_rejection:
                    conn.close()
                continue

            args = real_data.get('args')
            kwargs = real_data.get('kwargs')
        
            if args and kwargs:
                to_return = function.__call__(*args, **kwargs)
            elif args:
                to_return = function.__call__(*args)
            elif kwargs:
                to_return = function.__call__(**kwargs)
            else:
                to_return = function.__call__()

            if type(to_return) == File:
                print('\x1b[32m [ + ] Attempting to send the file {!r}'.format(to_return.filename))
                filesize = to_return.size()
                buffers, remain = divmod(filesize, self.BUFFER_SIZE)
                if remain != 0:
                    buffers += 1
                buffers = 1 if buffers == 0 else buffers
                
                conn.sendall('FILE:||{}||{}'.format(to_return.filename, buffers).encode('utf-8'))
                print('\x1b[32m [ + ] Attempting to send the file {!r}'.format(to_return.filename))

                packets = split(to_return.raw, self.BUFFER_SIZE)
                for packet in packets:
                    conn.sendall(packet)

                print('\x1b[32m [ + ] Sent {!r} using {!r} packets'.format(to_return.filename, buffers))

            else:
                conn.sendall(str(to_return).encode('utf-8'))
            print('\x1b[32m [ + ] Returned request result to {!r}'.format(address))

            if self.close_on_completion:
                conn.close()
                print('\x1b[32m [ + ] Closed connection with {!r}'.format(address))
            else:
                print('\x1b[32m [ + ] Connection still open with {!r}'.format(address))
            
        return self.kill

    def start(self):
        self.start_server()

        self.monitor()

    def on_call(self, event_name = None, methods = ['GET']):

        def register(func):
            event = event_name or func.__name__
                
            if self.calls.get(event):
                ## Preventing overwriting different calls and causing madness within your code
                raise DuplicateCall('Event {!r} already exists, rename it to something unique'.format(event))

            if type(methods) != list:
                raise TypeError('Methods must be a list not {!r}'.format(methods.__class__.__name__))

            if any([i for i in methods if i not in self.__allowed_methods]):
                raise ValueError('Invalid Method(s) in methods list. Allowed Methods: {!r}'.format(self.__allowed_methods))

            if inspect.isawaitable(func):
                raise TypeError('Event to call cannot be a coroutine, use the async client instead of this one')
            self.calls.update({event: [func, methods]})

        return register

    def dispatch(self, event_name: str, return_value, methods = ['GET']) -> None:
        ## Alternative to the decorator
        
        if self.calls.get(event):
            raise DuplicateCall('Event {!r} already exists, rename it to something unique'.format(event))

        if type(methods) != list:
            raise TypeError('Methods must be a list not {!r}'.format(methods.__class__.__name__))

        if any([i for i in methods if i not in self.__allowed_methods]):
            raise ValueError('Invalid Method(s) in methods list. Allowed Methods: {!r}'.format(self.__allowed_methods))

        if inspect.isawaitable(func):
            raise TypeError('Event to call cannot be a coroutine, use the async client instead of this one')
        self.calls.update({event: [func, methods]})
