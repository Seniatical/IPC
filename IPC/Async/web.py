from asyncio import (
    get_running_loop,
    new_event_loop,
    open_connection
    )

from ..exceptions import (
    ServerStartupError,
    DuplicateCall,
    ServerNotRunningError
    )

import inspect
import json

class AsyncWebClient:
    def __init__(self, host, port, secret_key = None, **kwargs) -> None:
        self.host = host
        self.port = port
        self.key = secret_key
        self.BUFFER_SIZE = 1024
        self.allowed = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        self.close_on_failure = kwargs.get('close_on_failure')
        self.close_on_completion = kwargs.get('close_on_completion')

        try:
            self.loop = kwargs.get('loop') or get_running_loop()
        except RuntimeError:
            self.loop = new_event_loop()

        if self.loop.is_closed():
            raise RuntimeError('Event loop must be running')

        self.connection = None

    async def open_connection(self) -> tuple:
        reader, writer = await open_connection(
            self.host, self.port,
            limit=self.BUFFER_SIZE if self.BUFFER_SIZE != 0 else None,      ## Sets the asyncio default limit of 64KiB
                                                                                                                     ## If you set the BUFFER_SIZE to 0
            )
        self.connection = (reader, writer)

        print('\x1b[32m [ + ] Connected to {!r}'.format((self.host, self.port)))
        
        return reader, writer

    async def fetch(self, event: str, *args, **kwargs) -> str:

        method = kwargs.get('method')
        if method:
            kwargs.pop('method')

            if method not in self.allowed:
                raise TypeError('Method {!r} is not recognised; use one of {!r}'.format(method.__class__.__name__, self.allowed))
        
        raw_json = {
            't': method or 'GET',
            'e': event,
            'a': str(self.key),
            'args': args,
            'kwargs': kwargs
            }
        decoded_packet = json.dumps(raw_json)
        encoded = decoded_packet.encode('utf-8', errors='ignore')

        if not self.connection:
            reader, writer = await self.open_connection()
        else:
            reader, writer = self.connection

        writer.write(encoded)
        await writer.drain()

        print('\x1b[32m [ + ] Sent request to {!r}'.format((self.host, self.port)))

        while True:

            recv = await reader.read(self.BUFFER_SIZE)

            if not recv:
                print('\x1b[31m [ - ] Rejected response from {!r} - No data provided'.format((self.host, self.port)))
                if self.close_on_failure:
                    return await writer.close()
                return

            print('\x1b[32m [ + ] Recieved valid response from {!r} - Data returned'.format((self.host, self.port)))

            if self.close_on_completion:
                await writer.close()
                print('\x1b[32m [ + ] Closed connection with {!r}'.format((self.host, self.port)))
            
            return recv.decode('utf-8', errors='ignore')
            
