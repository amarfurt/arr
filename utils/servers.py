"""
Helper class that holds information about the server environment.
Loads a json config file in the format: { <name>: { <properties> }}
"""

import json


class Servers:

    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.servers = json.load(f)

    def names(self):
        return self.servers.keys()

    def address(self, name):
        if self.servers.get(name):
            return self.servers[name].get('address')
        else:
            return None
