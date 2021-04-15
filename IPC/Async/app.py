from json import (
    loads, dumps
    )

from asyncio import (
    get_running_loop,
    new_event_loop,
    start_server
    )

from ..exceptions import (
    ServerStartupError,
    DuplicateCall
    )

from inspect import iscoroutine

class AsyncAppClient:
    __slots__ = ('host', 'port', 'secret_key', 'loop', '__allowed_methods', '__calls', 'tasks')
    
    def __init__(self, host, port, **kwargs):
        self.host = host
        self.port = port
        self.secret_key = kwargs.get('secret_key') or kwargs.get('secretkey')
        self.__allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        self.__calls = {}
        self.tasks = {}

        try:
            self.loop = kwargs.get('loop') or get_running_loop()
        except RuntimeError:
            self.loop = new_event_loop()

        if self.loop.is_closed():
            raise RuntimeError('Event loop must be running')

    def on_call(self, event_name: str = None, methods = ['GET']):

        def register(func):
            if not event_name:
                event_name = func.__name__
                
            if self.__calls.get(event_name):
                raise DuplicateCall('Event {!r} already exists, rename it to something unique'.format(event_name))

            if any([method for method in methods if method not in self.__allowed_methods]):
                raise ValueError('Invalid Method(s) in methods list. Allowed Methods: {!r}'.format(self.__allowed_methods))

            if not iscoroutine(func):
                raise TypeError('Function to call must a coroutine')

            self.__calls.update({event_name: [func, methods]})
            
        return register

    async def dispatch(self, event_name: str, return_value, methods = ['GET']) -> None:
        if self.__calls.get(event_name):
            raise DuplicateCall('Event {!r} already exists, rename it to something unique'.format(event_name))

        if any([method for method in methods if method not in self.__allowed_methods]):
            raise ValueError('Invalid Method(s) in methods list. Allowed Methods: {!r}'.format(self.__allowed_methods))

        if not iscoroutine(return_value):
            raise TypeError('Function to call must a coroutine')

        self.__calls.update({event_name: [func, methods]})

    def client_connection_callback(self, cli_reader, cli_writer):
        client_id = cli_writer.get_extra_info("peername")
        print(client_id)

        def client_cleanup(future):
            try:
                future.result()
            except Exception:
                pass
        
            ## del self.clients[client_id]
        
        task = asyncio.ensure_future(self.client_task(cli_reader, cli_writer))
        task.add_done_callback(client_cleanup)
        
        ## self.clients[client_id] = task
    
    async def client_task(self, reader, writer):
        while True:
            data = await reader.read(1024)
            
            if not data:
                continue

            data = data.decode()
            parsed_json = json.loads(data)
            
            headers = parsed_json.get("headers")
            
            if not headers or not headers.get("Authentication"):
                response = {"error": "No authentication provided.", "status": 403}
            
            token = headers.get("Authentication")
            
            if token != self.secret_key:
                response = {"error": "Invalid authorization token provided.", "status": 403}
            else:
                endpoint = parsed_json.get("endpoint")
                
                if not endpoint or not self.endpoints.get(endpoint):
                    response = {"error": 'No endpoint matching {} was found.'.format(endpoint), "status": 404}
                else:
                    server_response = IpcServerResponse(parsed_json)
                    response = await self.endpoints[endpoint](server_response)
            
            writer.write(json.dumps(response).encode("utf-8"))
            await writer.drain()
            
            break

    def start(self):
        server = start_server(client_connection_callback, self.host, self.port, loop=self.loop)
        self.loop.run_until_complete(server)

        
