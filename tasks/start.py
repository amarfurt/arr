"""
Starts the remote task running system on the given server.
Assumes that RabbitMQ is already running on the server
"""

import paramiko
from tasks.task import Task


class Start(Task):

    def __init__(self, servers):
        self.servers = servers

    def add_parser(self, registry):
        parser = registry.add_parser('start', help='Starts the remote task running system.')
        parser.add_argument('server', choices=self.servers.names(),
                            help='Server to start the system on.')

    def run(self, args):
        """ Runs the remote.py script in the background. """
        server_address = self.servers.address(args.server)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(server_address)
        client.exec_command('python3 code/arr/remote.py &>> logs/remote.log &')
        client.close()
