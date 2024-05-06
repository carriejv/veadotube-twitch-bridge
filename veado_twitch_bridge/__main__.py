import asyncio
import logging
import traceback

from twitch.event_listener import TwitchEventListener
from veadotube.connection import VeadotubeConnection
from config import get_config

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Initializes config reader and listeners for Veadotube / Twitch."""
    config = get_config()
    async with VeadotubeConnection(config['veadotube']['socket_server'], default_duration=config['veadotube']['default_duration']) as vtc, \
               TwitchEventListener(config['twitch']['client_id'], config['twitch']['client_secret']) as twitch:
        for binding in config['event_binding']:
            await twitch.set_handler(binding['twitch']['event'], await build_handler(binding))
        await asyncio.Future()

async def build_handler(event_binding):
    """Builds a handler function for a specific event binding."""
    async def handler(event):
        if event_binding['twitch'].get('source') is not None and event.source != event_binding['twitch']['source']:
            return
        if event_binding['twitch'].get('name') is not None and event.name != event_binding['twitch']['name']:
            return
        await vtc.enqueue_state_event(binding['veadotube'])
        logger.info(f'Received an {event.event} event and queued the following state change: {binding['veadotube']}.')
    return handler

try:
    asyncio.run(main())
except (asyncio.CancelledError, KeyboardInterrupt):
    print("Exited gracefully.")
except Exception as e:
    traceback.print_exc()