import socket
from ..exceptions import (ServerStartupError,
                          ServerNotRunningError,
                          SendingError
                          )
import json


class WebClient:
    def __init__(self, host, port, secret_key = None):
        self.port = port
        self.host = host
        self.key = secret_key

        try:
            self.sock = socket.create_connection((self.host, self.port))
            print('\033[90m [ + ] Connected to server')
        except Exception as error:
            ## Only ever raised when your app isn't running
            raise ServerNotRunningError() from error

    def get(self, event_name: str, *args, **kwargs):
        ## Used to get a recourse from your application
        ## Allows some extra information to be passed on
        
        raw_json = {
            't': 'GET',
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
            self.sock.sendall(json.dumps(raw_json).encode('utf-8'))
            print('\033[90m [ + ] Sent request to server')
        except Exception as error:
            raise SendingError() from error

        while True:

            try:
                data = self.sock.recv(1024).decode()
            except Exception:
                print('\033[93m [ - ] Target server rejected response')
                continue

            if not data:
                print('\033[93m [ - ] Rejected response - No data sent with packet')
                continue
                
            print('\033[90m [ + ] Accepted connection from {!r}'.format(address))

            if address != (self.host, self.port):
                print('\033[93m [ - ] Rejected response from {!r} - Incorrect address'.format(address))
                continue

            print('\033[90m [ + ] Recieved response from server')
            return data
