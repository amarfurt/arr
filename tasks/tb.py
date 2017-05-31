"""
Tensorboard task.
"""

import sys
import time
import paramiko
import subprocess
import webbrowser
from tasks.task import Task
from utils.timeout import Timeout, TimeoutException


class Tensorboard(Task):

    def __init__(self, servers):
        self.servers = servers

    def add_parser(self, registry):
        parser = registry.add_parser('tb', help='Open tensorboard on remote server.')
        parser.add_argument('server', choices=self.servers.names(),
                            help='On which server to start tensorboard.')
        parser.add_argument('logdir', help='Remote logdir (path from home directory).')

    def run(self, args):
        """ Run tensorboard on remote server and connect to it. """
        server_address = self.servers.address(args.server)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(server_address)

        # start tensorboard on remote server
        # try port different from the standard 6006 to avoid conflicts with other users
        remote_port = 6060
        while True:
            stdin, stdout, stderr = client.exec_command(
                'python3 -m tensorflow.tensorboard --logdir %s --port %d' %
                (args.logdir, remote_port), get_pty=True
            )

            # check if port already occupied
            try:
                with Timeout(2):
                    out = stdout.read().decode()
                    if 'address is in use' in out:
                        remote_port += 1
                    else:
                        print('Unexpected response:', out)
                        sys.exit(1)
            except TimeoutException:
                break

        # tunnel remote port to local machine
        local_port = 6006
        while True:
            tunnel = subprocess.Popen(
                'ssh -nNT -o ExitOnForwardFailure=yes -L %d:localhost:%d %s' %
                (local_port, remote_port, server_address),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            try:
                ret = tunnel.wait(1)
                if ret == 255:
                    local_port += 1
                else:
                    print('Unexpected returncode for tunneling:', ret)
                    print('[Stdout]:', tunnel.stdout)
                    print('[Stderr]:', tunnel.stderr)
                    sys.exit(2)
            except subprocess.TimeoutExpired:
                break
        print('Running tensorboard on port %d.' % local_port)
        webbrowser.open_new_tab('http://localhost:%d' % local_port)
        input('Press Enter to terminate...')
        tunnel.terminate()
        stdin.write('\x03')
        time.sleep(1)
        client.close()
