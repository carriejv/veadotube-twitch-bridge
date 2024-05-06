import json
import re

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