import asyncio
import json
import websockets

import veadotube.message_utils as message_utils

class VeadotubeConnection:
    """Defines a connection to a Veadotube socket server."""

    def __init__(self, uri, *, default_duration=30, reconnect=True, reconnect_attempts=0, reconnect_delay=30):
        self.uri = uri
        self.default_duration = default_duration
        self.reconnect = reconnect
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.open_socket = None
        self.open_tasks = []
        self.state_map = None
        self.state_queue = asyncio.queues.Queue()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, *exc):
        await self.close()
        return self

    async def open(self):
        """Opens the Veadotube socket connection. This must be called before using other functions to read/write."""
        if self.open_socket is not None:
            # TOOD: error
            return
        self.open_socket = await websockets.connect(self.uri)
        # Spawn a separate task to listen for messages and queue events.
        self.open_tasks.append(asyncio.create_task(self.message_handler()))
        self.open_tasks.append(asyncio.create_task(self.queue_handler()))
        # Peform an initial list on reconnect to build the state map.
        await self.open_socket.send(message_utils.vt_list())

    async def close(self):
        """Closes the veadotube socket."""
        if self.open_socket is None:
            return None
        for task in self.open_tasks:
            task.cancel()
        await self.open_socket.close()
        self.open_socket = None

    async def message_handler(self):
        """Initializes the message handler thread and waits forever for messages."""
        try:
            async for message in self.open_socket:
                msg_json = json.loads(message_utils.from_vt_get_json(message))
                msg_type = msg_json.get('type', '')
                match msg_type:
                    case 'stateEvents':
                        msg_payload = msg_json['payload']
                        match msg_payload['event']:
                            case 'list':
                                await self.build_state_map(msg_payload)
                            case 'peek':
                                # This is sent back constantly as a success response to everything. We don't really care.
                                pass
                            case _:
                                print('Got an unknown stateEvents payload type.')
                                print(msg_json)
                    case _:
                        print('Got an unknown message type.')
                        print(msg_json)
        except websockets.ConnectionClosed:
            # If the connection closes unexpectedly, try reopening it.
            if self.reconnect:
                asyncio.create_task(self.reconnect_loop())

    async def queue_handler(self):
        while True:
            if self.state_map is None:
                await asyncio.sleep(1)
                continue
            state_event = await self.state_queue.get()
            print('got queue item')
            print(state_event)
            # Keep trying until we send successfully.
            duration = state_event.get('duration', self.default_duration)
            while True:
                try:
                    if state_event.get('revert', False):
                        await self.open_socket.send(message_utils.vt_push(self.state_map[state_event['state']]))
                        await asyncio.sleep(duration)
                        await self.open_socket.send(message_utils.vt_pop(self.state_map[state_event['state']]))
                    else:
                        await self.open_socket.send(message_utils.vt_set(self.state_map[state_event['state']]))
                        await asyncio.sleep(duration)
                    break
                except websockets.ConnectionClosed:
                    # The read loop is responsible for maintaining the connection. This one can just back off and try again.
                    print('Error pushing state change.')
                    pass
            self.state_queue.task_done() 

    async def reconnect_loop(self):
        """Iniitalizes a loop that attempts to reconnect to the socket server."""
        attempts = 0
        while self.reconnect_attempts == 0 or attempts < self.reconnect_attempts:
            try:
                self.open_socket = await websockets.connect(self.uri)
                return
            except:
                print("Failed to reconnect. Attempting again...")
                attempts += 1
                await asyncio.sleep(self.reconnect_delay)
        # TODO: custom error probably lol
        raise websockets.ConnectionClosed(None, None)

    async def enqueue_state_event(self, state_event):
        await self.state_queue.put(state_event)

    async def build_state_map(self, state_list_json):
        """Builds a map of available avatar states. Called automatically on open(), but may be subsequently re-called to update the map."""
        self.state_map = {}
        for state in state_list_json['states']:
            self.state_map[state['name'].lower()] = state['id']
        print('built state map')
        print(self.state_map)
