"""
Train a model on a remote server.
"""

from tasks.task import Task


class Train(Task):

    def __init__(self, servers):
        self.servers = servers

    def add_parser(self, registry):
        parser = registry.add_parser('train', help='Train a model on a remote server.')
        parser.add_argument('server', choices=self.servers.names(),
                            help='Remote server to train on.')
        parser.add_argument('config', help='Path to config file.')

    def run(self, args):
        """ Run tensorboard on remote server and connect to it. """
        pass
