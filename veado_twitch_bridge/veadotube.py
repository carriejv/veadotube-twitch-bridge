import asyncio
import json
import re
import websockets

class VeadotubeConnection:
    """Defines a connection to a Veadotube socket server."""

    def __init__(self, uri, *, reconnect=True, reconnect_attempts=0, reconnect_delay=30):
        self.uri = uri
        self.reconnect = reconnect
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.open_socket = None
        self.state_map = None
        self.should_close = False

    async def __aenter__(self):
        await self.open_connection()
        return self

    async def __aexit__(self):
        await self.close_connection()
        return self

    async def open_connection(self):
        """Opens the Veadotube socket connection. This must be called before using other functions to read/write."""
        self.should_close = False
        self.open_socket = await websockets.connect(self.uri)
        # Spawn a separate task to listen for messages.
        asyncio.create_task(self.init_handler())
        # Peform an initial list on reconnect to build the state map.
        await self.open_socket.send(VeadotubeMessageBuilder.vt_list())

    async def close_connection(self):
        """Closes the veadotube socket."""
        if self.open_socket is None:
            return None
        self.should_close = True
        await self.open_socket.close()
        self.open_socket = None

    async def init_handler(self):
        """Initializes the message handler thread and waits forever for messages."""
        try:
            async for message in self.open_socket:
                await self.handle_message(message)
        except websockets.ConnectionClosed:
            # If the connection closes unexpectedly, try reopening it.
            if self.reconnect:
                asyncio.create_task(self.init_reconnect_loop())

    async def handle_message(self, message):
        """Message handler for incoming socket traffic."""
        msg_json = json.loads(VeadotubeMessageBuilder.from_vt_get_json(message))
        try:
            msg_type = msg_json['type']
        except KeyError:
            print("Got an unknown message format.")
            print(msg_json)
            return
        match msg_type:
            case 'stateEvents':
                msg_payload = msg_json['payload']
                match msg_payload['event']:
                    case 'list':
                        await self.build_state_map(msg_payload)
                    case _:
                        print('Got an unknown stateEvents payload type.')
                        print(msg_json)
            case _:
                print('Got an unknown message type.')
                print(msg_json)

    async def build_state_map(self, state_list_json):
        """Builds a map of available avatar states. Called automatically on o   pen_connection(), but may be subsequently re-called to update the map."""
        print('called build_state_map')

    async def init_reconnect_loop(self):
        """Iniitalizes a loop that attempts to reconnect to the socket server."""
        attempts = 0
        while self.reconnect_attempts == 0 or attempts < self.reconnect_attempts:
            try:
                await self.open_connection()
                return
            except:
                print("Failed to reconnect. Attempting again...")
                attempts += 1
                await asyncio.sleep(self.reconnect_delay)
        # TODO: custom error probably lol
        raise websockets.ConnectionClosed(None, None)

class VeadotubeMessageBuilder:
    """Contains various utility methods for building Veadotube socket messages."""

    def vt_list():
        """Builds a list message for the Veadotube socket."""
        message_contents = json.dumps({
            'event': 'payload',
            'type': 'stateEvents',
            'id': 'mini',
            'payload': {
                'event': 'list'
            }
        })
        return f'nodes:{message_contents}'

    def vt_set(stateid):
        """Builds a set state message for the Veadotube socket."""
        message_contents = json.dumps({
            'event': 'payload',
            'type': 'stateEvents',
            'id': 'mini',
            'payload': {
                'event': 'set',
                'state': stateid
            }
        })
        return f'nodes:{message_contents}'

    def vt_push(stateid):
        """Builds a push state message for the Veadotube socket."""
        message_contents = json.dumps({
            'event': 'payload',
            'type': 'stateEvents',
            'id': 'mini',
            'payload': {
                'event': 'push',
                'state': stateid
            }
        })
        return f'nodes:{message_contents}'

    def vt_pop(stateid):
        """Builds a pop state message for the Veadotube socket."""
        message_contents = json.dumps({
            'event': 'payload',
            'type': 'stateEvents',
            'id': 'mini',
            'payload': {
                'event': 'pop',
                'state': stateid
            }
        })
        return f'nodes:{message_contents}'

    def from_vt_get_json(vt_msg):
        """Extracts plain deserializable JSON from a Veadotube message."""
        # Sometimes these strings come in with a ton of terminating whitespace and/or null bytes.
        # Not sure if this is a Veado or python websockets thing.
        json_contents = re.search(r'^.*?:(?P<json>{.*})[\s,\x00]*?$', vt_msg)
        return json_contents.group('json')
