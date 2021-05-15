from asyncio import (
    get_running_loop,
    new_event_loop,
    start_server
)

from ...exceptions import (
    ServerStartupError,
    DuplicateCall,
    ServerNotRunningError
)

from ...Models import (
    File, split
)

import inspect
import json
import time


class AsyncAppClient:
    def __init__(self, host, port, **kwargs):
        self.host = host
        self.port = port
        self.secret_key = kwargs.get('secret_key') or kwargs.get('secretkey')
        self.allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        self.calls = {}
        self.BUFFER_SIZE = 1024
        self.server = None
        self.close_on_failure = kwargs.get('close_on_failure')
        self.close_on_completion = kwargs.get('close_on_completion')

        print('\x1b[32m [ + ] Server IP {!r} | Port {!r} - Async Client'.format(self.host, self.port))

        try:
            self.loop = kwargs.get('loop') or get_running_loop()
        except RuntimeError:
            self.loop = new_event_loop()

        if self.loop.is_closed():
            raise RuntimeError('Event loop must be running')

    async def kill(self):
        if not self.server:
            raise ServerNotRunningError('Server is not running')
        print('\x1b[31m [ - ] Server shutting down')

        try:
            serv = await self.server
            self.server = serv
        except Exception:
            pass

        server.close()
        await server.wait_closed()

        print('\x1b[31m [ - ] Server has been closed and is no longer accepting requests')

    def on_call(self, event_name=None, methods=None):

        if methods is None:
            methods = ['GET']

        def register(func):
            event = event_name or func.__name__

            if self.calls.get(event):
                raise DuplicateCall('Event {!r} already exists, rename it to something unique'.format(event))

            if type(methods) not in [tuple, list]:
                raise TypeError('Methods must be a list/tuple not {!r}'.format(methods.__class__.__name__))

            if any([i for i in methods if i not in self.allowed_methods]):
                raise ValueError(
                    'Invalid Method(s) in methods list. Allowed Methods: {!r}'.format(self.allowed_methods))

            if not inspect.iscoroutinefunction(func):
                raise TypeError('Event to call must be a coroutine when using this client')
            self.calls.update({event: [func, methods]})

        return register

    async def dispatch(self, event_name: str, return_value, methods=None) -> None:
        if methods is None:
            methods = ['GET']

        if self.calls.get(event_name):
            raise DuplicateCall('Event {!r} already exists, rename it to something unique'.format(event_name))

        if any([method for method in methods if method not in self.allowed_methods]):
            raise ValueError('Invalid Method(s) in methods list. Allowed Methods: {!r}'.format(self.allowed_methods))

        if not inspect.iscoroutinefunction(return_value):
            raise TypeError('Function to call must a coroutine')

        self.calls.update({event_name: [func, methods]})

    async def sockets(self):
        try:
            serv = await self.server
            self.server = serv
        except Exception:
            pass

        return self.server.sockets

    async def handle_response(self, reader, writer):
        if not writer or not reader:
            return

        while True:
            data = await reader.read(1024)

            if not data:
                return

            sock = writer.get_extra_info('socket')
            address = sock.getsockname()
            ## IPV4/IPV6 is not supported on some OS's so it returns ::1

            print('\x1b[32m [ + ] Recieved request from {!r}'.format(address))

            try:
                packet = json.loads(data.decode('utf-8', errors='ignore'))
            except Exception:
                print('\x1b[31m [ - ] Rejected request from {!r} - Badly formed packet'.format(address))
                if self.close_on_failure:
                    return await writer.close()
                return

            event = packet.get('e') or packet.get('event')
            method = packet.get('t') or packet.get('type') or packet.get('method') or packet.get('m')

            if any([i for i in [event] if not i]):
                print('\x1b[31m [ - ] Rejected request from {!r} - Badly formed packet'.format(address))
                if self.close_on_failure:
                    return await writer.close()
                return

            auth = packet.get('a') or packet.get('auth') or packet.get('authorization')

            if str(auth) != str(self.secret_key):
                print('\x1b[31m [ - ] Rejected request from {!r} - Invalid authorization'.format(address))
                if self.close_on_failure:
                    return await writer.close()
                return

            event = self.calls.get(event)

            if not event:
                print('\x1b[31m [ - ] Rejected request from {!r} - Event request doesn\'t exist'.format(address))
                if self.close_on_failure:
                    return await writer.close()
                return

            coro, methods = event

            if method not in methods:
                print('\x1b[31m [ - ] Rejected request from {!r} - Method {!r} is not allowed'.format(address, method))
                if self.close_on_failure:
                    return await writer.close()
                return

            if packet.get('kwargs') and packet.get('args'):
                res = await coro.__call__(*args, **kwargs)
            elif packet.get('kwargs'):
                res = await coro.__call__(**kwargs)
            elif packet.get('args'):
                res = await coro.__call__(args)
            else:
                res = await coro.__call__()

            if type(res) == File:

                filename = res.filename
                filesize = res.size()

                buffers, remain = divmod(filesize, self.BUFFER_SIZE)

                if remain != 0:
                    buffers += 1
                buffers = (buffers + 1)

                print('\x1b[32m [ + ] Preparing to send {!r} to {!r} with {!r} packets.'.format(filename, address,buffers))

                try:
                    await writer.write('FILE:||{}||{}'.format(filename, buffers).encode('utf-8', errors='ignore'))
                except TypeError:
                    pass

                packets = split(res, self.BUFFER_SIZE)

                for packet in packets:
                    try:
                        await writer.write(packet)
                    except TypeError:
                        pass

                try:
                    await writer.write(b'End')
                except TypeError:
                    pass

                await writer.drain()

                print('\x1b[32m [ + ] Sent {!r} to {!r} using {!r} packets'.format(filename, address, buffers))
                break

            as_string = str(res)

            try:
                await writer.write((as_string[:self.BUFFER_SIZE]).encode('utf-8', errors='ignore'))
            except TypeError:
                pass
            await writer.drain()

            print('\x1b[32m [ + ] Sent result back to {!r}'.format(address))

            break

    def start(self):

        server = start_server(self.handle_response, self.host, self.port, loop=self.loop)
        self.server = server

        self.loop.create_task(server)
        print('\x1b[32m [ + ] Server is now running')

        if not self.loop.is_running():
            self.loop.run_forever()  ## Wouldn't allow any requests to pass without this
        print('\x1b[32m [ + ] Server is now accepting requests')
