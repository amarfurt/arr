"""
Stops the remote task running system.
"""

import paramiko
from tasks.task import Task


class Stop(Task):

    def __init__(self, servers):
        self.servers = servers

    def add_parser(self, registry):
        parser = registry.add_parser('stop', help='Stops the remote task running system.')
        parser.add_argument('server', choices=self.servers.names(),
                            help='On which server to stop the remote system.')

    def run(self, args):
        """ Runs the remote.py script in the background. """
        server_address = self.servers.address(args.server)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(server_address)
        client.exec_command('pkill -f remote.py')
        client.close()
