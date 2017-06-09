"""
Helper class that holds information about the server environment.
Loads a json config file in the format: { <name>: { <properties> }}
"""

import json


class Server:

    def __init__(self, name, address):
        self.name = name
        self.address = address


def load_servers(config_path):
    """ Loads the server configuration. """
    servers = {}
    with open(config_path, 'r') as f:
        server_properties = json.load(f)
    for name, properties in server_properties.items():
        servers[name] = Server(name, properties['address'])
    return servers
