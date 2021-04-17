import IPC
import asyncio

client = IPC.AsyncWebClient('localhost', 5000, None)

async def get_reponse():
    res = await client.fetch('test')
    print(res)

asyncio.run(get_reponse())
