"""
Stops the remote task running system.
"""

import paramiko
from tasks.task import Task


class Stop(Task):

    @staticmethod
    def add_parser(registry):
        registry.add_parser('stop', help='Stops the remote task running system.')

    def run(self, args):
        """ Runs the remote.py script in the background. """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(self.server.address)
        client.exec_command('pkill -f remote.py')
        client.close()
