## Caclulate the ping of your app server
## Not accurate

from IPC import AppClient

client = AppClient('localhost', 5000, 'mysecretkey')

@client.on_call(event_name='ping')
def get_ping():
    return 'Called!'

client.start()
    
## Web
from IPC import WebClient
from time import perf_counter
from flask import Flask

app = Flask(__name__)
client = WebClient('localhost', 5000, 'mysecretkey')

@app.route('/')
def index():
    start = perf_counter()
    client.get('ping')
    end = perf_counter()
    return 'My Application servers ping is currently - {}ms'.format(round((end - start) * 1000))

if __name__ == '__main__':
    app.run()
