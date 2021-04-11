# IPC
A simple program which allows you to interact with a web-server and your application

**Usage:**
```py
## Sync version

## In your application
from IPC import AppClient

client = AppClient('host', port, 'secret-key')

client.dispatch(
    "event-type",
    "content-type",
    content
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

If you require an async version
```
from IPC import AIO_AppClient

client = AIO_AppClient('host', port, 'secret-key')

async def dispatch():
    await client.dispatch(
    "event-type",
    "content-type",
    content
    )
    
@client.on_call('event-name')     
async def my_event(*args, **kwargs):
    return args

## Your web app would be the same as before except with async and await infront of each function
```
