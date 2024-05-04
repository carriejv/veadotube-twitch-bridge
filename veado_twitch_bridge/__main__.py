import asyncio
import signal

import twitch.twitch
import veadotube
from config.config import get_config

vtc = None

async def main():
    """Initializes config reader and global ticks for Veadotube / Twitch."""
    config = get_config()
    # asyncio.create_task(twitch.twitch.tick(config))
    vtc = veadotube.VeadotubeConnection(config['veadotube']['socket_server'])
    asyncio.create_task(vtc.open_connection())
    await asyncio.Future()

async def close():
    await vtc.close_connection()

try:
    asyncio.run(main())
except (asyncio.CancelledError, KeyboardInterrupt):
    asyncio.run(close())
