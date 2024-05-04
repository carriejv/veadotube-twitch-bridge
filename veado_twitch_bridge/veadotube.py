import asyncio
import json
import websockets

class VeadotubeConnection:
    """Defines a connection to a Veadotube socket server."""

    def __init__(self, uri):
        self.uri = uri
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
        # Automatically reopens connection on error.
        async for websocket in websockets.connect(self.uri):
            try:
                self.open_socket = websocket
                async for message in websocket:
                    await self.handle_message(message)
                # Send an initial request for a state list.
                await self.open_socket.send(VeadotubeMessageBuilder.vt_list())
                # await websocket.send(VeadotubeMessageBuilder.vt_set('5A'))
                
            except websockets.ConnectionClosed:
                if not self.should_close:
                    continue

    async def close_connection(self):
        """Closes the veadotube socket."""
        if self.open_socket is None:
            return None
        self.should_close = True
        await open_socket.close()
        self.open_socket = None

    async def build_state_map(self, state_list_json):
        """Builds a map of available avatar states. Called automatically on open_connection(), but may be subsequently re-called to update the map."""
        print(state_list_json)

    async def handle_message(self, message):
        """Message handler for incoming socket traffic."""
        msg_json = VeadotubeMessageBuilder.from_vt_get_json(message)
        print(message)
        print(msg_json)
        match msg_json['type']:
            case 'list':
                await self.build_state_map(msg_json)
            case _:
                print('Got an unknown message type.')

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
        """Converts a Veadotube message into plain deserializable JSON."""
        # This isn't super robust but it doesn't really need to be right now.
        return vt_msg[vt_msg.index('{'):]
