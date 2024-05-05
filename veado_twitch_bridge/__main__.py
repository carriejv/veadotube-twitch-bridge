import asyncio
import logging

import twitch.twitch
from veadotube.connection import VeadotubeConnection
from config import get_config

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s : %(message)s', level=logging.INFO)

async def main():
    """Initializes config reader and global ticks for Veadotube / Twitch."""
    config = get_config()
    # asyncio.create_task(twitch.twitch.tick(config))
    async with VeadotubeConnection(config['veadotube']['socket_server'], default_duration=config['veadotube']['default_duration']) as vtc:
        for binding in config['event_binding']:
            await vtc.enqueue_state_event(binding['veadotube'])
            await asyncio.sleep(30)
        await asyncio.Future()

try:
    asyncio.run(main())
except (asyncio.CancelledError, KeyboardInterrupt):
    print("Exited gracefully.")
