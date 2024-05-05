import asyncio
import logging
import os
import platformdirs
import tomlkit

logger = logging.getLogger(__name__)

CONFIG_FILE_NAME = 'config.toml'

def get_config():
    cfg_path = find_config_file()
    if cfg_path is None:
        raise Execption('Unable to find a config file. Without one, this app will do nothing.')
    file = open(cfg_path, 'r')
    toml_contents = file.read()
    return tomlkit.parse(toml_contents)

def find_config_file():
    user_cfg_dir = platformdirs.user_config_dir('veado-twitch-bridge')
    for path in [CONFIG_FILE_NAME, os.path.join(user_cfg_dir, CONFIG_FILE_NAME)]:
        if os.path.isfile(path):
            logger.info(f'Found config file at {path}.')
            return path
    return None
