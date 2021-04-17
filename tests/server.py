import IPC

client = IPC.AsyncAppClient('localhost', 5000)

@client.on_call(event_name = 'test')
async def test():
    return 'Hi!'

client.start()
