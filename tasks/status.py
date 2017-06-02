"""
Queries the status of the remote resources.
"""

import time
import paramiko
from tasks.task import Task


class Status(Task):

    def __init__(self, servers):
        self.servers = servers

    def add_parser(self, registry):
        parser = registry.add_parser('status', help='Queries the resource status.')
        parser.add_argument('server', choices=self.servers.names(), help='Remote server to query.')

    def run(self, args):
        """ Adds a 'status' request to the 'control' queue. """
        server_address = self.servers.address(args.server)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(server_address)

        # enqueue a 'status' message on the 'control' queue
        corr_id = int(time.time())  # correlation id is current timestamp
        client.exec_command('python3 code/arr/enqueue.py --queue control --message status '
                            '--rpc %d' % corr_id)

        # wait and read the response from the 'rpc_response' queue
        time.sleep(1)
        _, stdout, stderr = client.exec_command('python3 code/arr/dequeue.py --queue rpc_response '
                                                '--rpc %d' % corr_id)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if out:
            print(out)
        if err:
            print('[stderr] %s' % err)
        client.close()
