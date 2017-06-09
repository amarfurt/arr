"""
Enqueues a control message for the remote system.
"""

import paramiko
from tasks.task import Task


class Control(Task):

    @staticmethod
    def add_parser(registry):
        parser = registry.add_parser('control', help='Sends a control message.')
        parser.add_argument('message', nargs='+', help='Message to send.')

    def run(self, args):
        """ Runs the remote.py script in the background. """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(self.server.address)
        client.exec_command('python3 code/arr/enqueue.py --queue control --message "%s"' %
                            ' '.join(args.message))
        client.close()
