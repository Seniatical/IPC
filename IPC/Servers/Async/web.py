from asyncio import (
    get_running_loop,
    new_event_loop,
    open_connection,
    wait_for,
    TimeoutError
)

from ...exceptions import (
    ServerStartupError,
    DuplicateCall,
    ServerNotRunningError
)

from json import dumps
from re import compile
from io import BytesIO
from aiofiles import open
from os import remove

class AsyncWebClient:
    def __init__(self, host, port, secret_key=None, **kwargs) -> None:
        self.host = host
        self.port = port
        self.key = secret_key
        self.BUFFER_SIZE = 1024
        self.allowed = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

        self.close_on_failure = kwargs.get('close_on_failure')
        self.close_on_completion = kwargs.get('close_on_completion')

        self.timeout = kwargs.get('timeout') or 10

        int(self.timeout); bool(self.close_on_failure); bool(self.close_on_completion)
        ## Just to check if they are of the right datatype

        self.packet_transfer_pattern = compile(r'FILE?:\|\|(?:[a-z]{1, 50})?.+\|\|[0-9]+')

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
            limit=self.BUFFER_SIZE if self.BUFFER_SIZE != 0 else None,  ## Sets the asyncio default limit of 64KiB
            ## If you set the BUFFER_SIZE to 0
        )
        self.connection = (reader, writer)

        print('\x1b[32m [ + ] Connected to {!r}'.format((self.host, self.port)))

        return reader, writer

    async def fetch(self, event: str, *args, **kwargs) -> str:

        method = kwargs.get('method')
        if method:
            kwargs.pop('method')

        path = kwargs.get('path')
        if method:
            kwargs.pop('path')

            if method not in self.allowed:
                raise TypeError(
                    'Method {!r} is not recognised; use one of {!r}'.format(method.__class__.__name__, self.allowed))

        raw_json = {
            't': method or 'GET',
            'e': event,
            'a': str(self.key),
            'args': args,
            'kwargs': kwargs
        }
        decoded_packet = dumps(raw_json)
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

            decoded_recv = recv.decode('utf-8', errors='ignore')

            is_file = self.packet_transfer_pattern.match(decoded_recv)
            if is_file:
                actual_find = is_file.group()

                parted = actual_find.split('||')
                filename = parted[1]
                packets = int(parted[-1])

                path = path or filename

                if path != filename:
                    path += f'/{filename}'

                print('\x1b[32m [ + ] Preparing to save {!r} with a total of {!r} packets'.format(filename, packets))

                try:
                    async with open(path, 'wb') as f:

                        while True:

                            try:
                                raw_data = await wait_for(reader.read(self.BUFFER_SIZE), self.timeout)
                            except TimeoutError:
                                break

                            if not raw_data:
                                break

                            await f.write(raw_data)

                    async with open(path, 'rb') as f:
                        file_data = await f.read()

                    if not file_data:
                        remove(filename)
                        print('\x1b[31m [ - ] Failed to transfer file')
                        break

                except OSError as error:
                    print('\x1b[31m [ - ] Failed to open/write to file - {!r}'.format(error))
                    break

                print('\n\x1b[32m [ + ] Saved file {!r}'.format(filename))

                if self.close_on_completion:
                    await writer.close()
                    print('\x1b[32m [ + ] Closed connection with {!r}'.format((self.host, self.port)))

                return BytesIO(file_data)

            print('\x1b[32m [ + ] Recieved valid response from {!r} - Data returned'.format((self.host, self.port)))

            if self.close_on_completion:
                await writer.close()
                print('\x1b[32m [ + ] Closed connection with {!r}'.format((self.host, self.port)))

            return decoded_recv
