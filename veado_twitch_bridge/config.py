config = {
    'twitch': {
        'client_id': 'foo',
        'api_key': 'bar'
    },
    'veadotube': {
        # 'socket_server': 'ws://127.0.0.1:39731?n=veado_twitch_bridge'
        'socket_server': 'ws://127.0.0.1:63640?n=veado_twitch_bridge',
        'default_duration': 30
    },
    'event_binding': [{
        'veadotube': {
            'state': 'confused',
            'duration': 15,
            'revert': True
        }
    },
    {
        'veadotube': {
            'state': 'laugh',
            'duration': 10,
        }
    },
    {
        'veadotube': {
            'state': 'sad',
            'duration': 10
        }
    },
    {
        'veadotube': {
            'state': 'shy',
            'revert': True
        }
    }]
}

def get_config():
    return config
