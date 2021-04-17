# IPC
A small lightweight networking module

## Version Updates:
- Sending files is now possible (SYNC ONLY)
- Async client is here | No file sending as of now
- May add a category offering SSL soon

## Sync
```py
## In your application
from IPC import AppClient

client = AppClient('host', port, 'secret-key')

## Manually add an event to your servers cache
client.dispatch(
    methods = ['GET'],   ## This is the default option so it isn't always required
    return_value = ## Can be a function or class. Class must be callable else it will raise an error
                   ## Can also be anything of `str, int, float, dict, set [Might be buggy], tuple, list etc...`
                   ## Everything thats returned at the end will be casted as a string so it can be encoded - WARNING
    event_name = 'Something Unique',    ## This is used to find your return value and send it to your web app
)


## If your using a function
@client.on_call('event-name')     ## If no name for the even is supplied the function's name becomes the event name
def my_event(*args, **kwargs):
    return args     ## What ever is returned is sent to your website
    
## In your web app
from IPC import WebClient
from flask import Flask

client = Webclient('host', port, 'secret-key')
## Note: port and secret-key must be the same as the Application
app = Flask(__name__)

@app.route('/')
def index():
    return client.fetch('my_event')   ## Returns the data which was sent from your application
```

## Need to send files?
```py
from IPC import File, AppClient

client = AppClient('host', port, 'secret-key')

@client.on_call('event-name')  
def my_event(*args, **kwargs):
    return File('./path/to/file', 'filename.txt')
    
    ## What if i dont have the file saved?
    return File(raw=bytes, filename='filename.txt')
    
    ## Base format is
    ## `filepath, filename`
    ## If a filepath is supplied and the file path leads to the file itself the filename wont be required
```

## Async

```py
from IPC import AsyncAppClient

client = AsyncAppClient('host', port, 'secret-key')

async def dispatch():
    await client.dispatch(
    ## Same args and kwargs as the sync version
    )
    
@client.on_call('event-name')     
async def my_event(*args, **kwargs):
    return args

client.start()

## Your web app would be the same as before except with async and await infront of each function
## Your import would be
from IPC import AsyncWebClient
```

## FAQ:

Q: Can I increase the buffer size?\
A: Yes you can, as shown below
```py
## Example
import IPC

client = IPC.AppClient(*args, **kwargs)
client.BUFFER_SIZE = your-buffer-size ## Default is set to 1024
                                      ## Setting it to None or 0 on the Async client would mean there is a 64 KiB limit
                                      ## Not recomended ^
```
