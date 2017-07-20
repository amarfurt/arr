"""
Starts the remote task running system on the given server.
Assumes that RabbitMQ is already running on the server
"""

import paramiko
from tasks.task import Task


class Start(Task):

    @staticmethod
    def add_parser(registry):
        registry.add_parser('start', help='Starts the remote task running system.')

    def run(self, args):
        """ Runs the remote.py script in the background. """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(self.server.address)
        client.exec_command('python3 code/arr/remote.py --loglevel DEBUG &>> logs/remote.log &')
        client.close()
