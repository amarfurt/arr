"""
Git pulls a branch to its newest version on the server.
"""

import paramiko
from tasks.task import Task


class Pull(Task):

    @staticmethod
    def add_parser(registry):
        parser = registry.add_parser('pull', help='Git pulls a remote branch.')
        parser.add_argument('codedir', help='Path to git repo on server.')
        parser.add_argument('-b', '--branch', default='master', help='Branch to pull.')

    def run(self, args):
        """ Git pulls a remote branch. """
        codedir = args.codedir if args.codedir.startswith('code/') else 'code/' + args.codedir
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(self.server.address)
        _, out, _ = client.exec_command('cd %s; git checkout %s; git pull' % (codedir, args.branch))
        print(out.read().decode().strip())  # read stdout/stderr, git pull hangs otherwise
        client.close()
