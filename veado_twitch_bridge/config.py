config = {
    'twitch': {
        'client_id': 'foo',
        'api_key': 'bar'
    },
    'veadotube': {
        # 'socket_server': 'ws://127.0.0.1:39731?n=veado_twitch_bridge'
        'socket_server': 'ws://127.0.0.1:63640?n=veado_twitch_bridge'
    },
    'veadotube_binding': [{
        
    }]
}

def get_config():
    return config
