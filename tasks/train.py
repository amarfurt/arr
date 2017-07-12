"""
Train a model on a remote server.
"""

import json
import paramiko
from tasks.task import Task


class Train(Task):

    @staticmethod
    def add_parser(registry):
        parser = registry.add_parser('train', help='Train a model on a remote server.')
        parser.add_argument('config', help='Path to config file.')

    def run(self, args):
        """ Adds a run configuration to the 'gpu' queue. """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(self.server.address)

        # read the config file
        with open(args.config, 'r') as f:
            config = json.load(f)

        # enqueue the contents of the config file on the 'gpu' queue
        client.exec_command('python3 code/arr/enqueue.py --queue gpu --message \'%s\''
                            % json.dumps(config))
        client.close()
