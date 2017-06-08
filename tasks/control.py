"""
Enqueues a control message for the remote system.
"""

import paramiko
from tasks.task import Task


class Control(Task):

    def __init__(self, servers):
        self.servers = servers

    def add_parser(self, registry):
        parser = registry.add_parser('control', help='Sends a control message.')
        parser.add_argument('server', choices=self.servers.names(),
                            help='Server to send control messages to.')
        parser.add_argument('message', nargs='+', help='Message to send.')

    def run(self, args):
        """ Runs the remote.py script in the background. """
        server_address = self.servers.address(args.server)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(server_address)
        client.exec_command('python3 code/arr/enqueue.py --queue control --message "%s"' %
                            ' '.join(args.message))
        client.close()
