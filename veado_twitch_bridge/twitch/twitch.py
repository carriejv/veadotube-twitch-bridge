import asyncio

async def tick(config):
    while True:
        await asyncio.sleep(config['twitch_poll_rate'])