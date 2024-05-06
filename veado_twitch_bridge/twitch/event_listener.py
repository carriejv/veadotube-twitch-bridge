import asyncio
import logging
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object.eventsub import ChannelPointsCustomRewardRedemptionAddEvent
from twitchAPI.helper import first

OAUTH_SCOPES = [
    AuthScope.CHANNEL_READ_GOALS,
    AuthScope.CHANNEL_READ_HYPE_TRAIN,
    AuthScope.CHANNEL_READ_REDEMPTIONS,
    AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
    # There is no specific scope for reading these on only your own channel, for some reason, but you're always a mod of your own channel.
    AuthScope.MODERATOR_READ_FOLLOWERS,
    AuthScope.MODERATOR_READ_SHOUTOUTS
]

SUPPORTED_EVENTS = (
    'follow',
    'sub',
    'raid_in',
    'raid_out',
    'shoutout',
    'hype_train_start',
    'follow_goal_complete',
    'sub_goal_complete',
    'plus_goal_complete',
    'channel_point_redeem'
)

logger = logging.getLogger(__name__)

class TwitchEventListener:
    """Listens for events on twitch channel(s) via the EventSub API."""

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.twitch = None
        self.oauth_authenticator = None
        self.userid = None
        self.handler_map = {}

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, *exc):
        await self.close()
        return self

    async def open(self):
        """Opens a new connection to Twitch."""
        self.twitch = await Twitch(self.client_id, self.client_secret)
        self.oauth_authenticator = UserAuthenticator(self.twitch, OAUTH_SCOPES, force_verify=False)
        self.oauth_authenticator.document = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>OAuth Succeeded!/title>
        </head>
        <body>
        You may now close this page.
        </body>
        </html>"""
        token, refresh_token = await self.oauth_authenticator.authenticate()
        await self.twitch.set_user_authentication(token, OAUTH_SCOPES, refresh_token)
        self.userid = (await first(self.twitch.get_users())).id
        self.eventsub = EventSubWebsocket(self.twitch)
        self.eventsub.start()
        logger.info(f'Successfully opened Twitch EventSub websocket.')

    async def close(self):
        """Closes the Twitch session and EventSub websocket."""
        await self.eventsub.close()
        await self.twitch.close()

    async def set_handler(self, event, handler):
        """Sets a handler for a specific event."""
        if event not in SUPPORTED_EVENTS:
            raise Exception(f'Attempted to create a handler for an unknown event type: {event}.')
        if self.handler_map.get(event) is None:
            self.handler_map[event] = []
            await self._init_internal_handler(event)
        self.handler_map[event].append(handler)
        logger.info(f'Successfully registered handler for {event} events.')
    
    async def _init_internal_handler(self, event):
        """Initializes a low-level handler that listen to topics on the EventSub websocket."""
        match event:
            case 'channel_point_redeem':
                await self.eventsub.listen_channel_points_custom_reward_redemption_add(self.userid, self._channel_point_handler)
        logger.info(f'Successfully initialzed subscription to {event} events.')

    async def _channel_point_handler(data: ChannelPointsCustomRewardRedemptionAddEvent):
        """Internal low-level handler for channel point rewards that runs high-level handlers added by set_handler."""
        async for handler in self.handler_map['channel_point_redeem']:
            handler({
                'event': 'channel_point_redeem',
                'source': data.event.user_name,
                'name': data.event.reward.title
            })
