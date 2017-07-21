"""
Run a script on a remote server.
"""

import json
import paramiko
from tasks.task import Task


class Run(Task):

    @staticmethod
    def add_parser(registry):
        parser = registry.add_parser('run', help='Run a script on a remote server.')
        parser.add_argument('config', help='Path to config file.')
        parser.add_argument('--cpu', action='store_true', help='Run on CPU instead of GPU.')

    def run(self, args):
        """ Adds a run configuration to the 'gpu' or 'cpu' queue. """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(self.server.address)

        # read the config file
        with open(args.config, 'r') as f:
            config = json.load(f)

        # enqueue the contents of the config file on the respective queue
        queue = 'cpu' if args.cpu else 'gpu'
        client.exec_command("python3 code/arr/enqueue.py --queue %s --message '%s'"
                            % (queue, json.dumps(config)))
        client.close()
