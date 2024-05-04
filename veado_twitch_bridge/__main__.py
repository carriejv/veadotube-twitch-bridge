import asyncio
import signal

import twitch.twitch
import veadotube
from config.config import get_config

async def main():
    """Initializes config reader and global ticks for Veadotube / Twitch."""
    config = get_config()
    # asyncio.create_task(twitch.twitch.tick(config))
    vtc = veadotube.VeadotubeConnection(config['veadotube']['socket_server'])
    asyncio.create_task(vtc.open_connection())
    try:
        await asyncio.Future()
    except (asyncio.CancelledError, KeyboardInterrupt):
        await vtc.close_connection()

asyncio.run(main())
