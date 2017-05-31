"""
Runs command-line operations.
"""

import json
import subprocess
from workers.rmq_worker import Rabbit


class CmdRunner(Rabbit):

    def __init__(self, host, queue):
        super().__init__(host, queue)

    def callback(self, channel, method, properties, body):
        config = json.loads(body.decode())
        executable = config['executable']
        args = ''
        if 'args' in config:
            args = ' '.join(['--%s %r' % (k, v) for k, v in config['args'].items()])
        command = ' '.join(filter(None, [executable, args]))
        self.execute(command)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def execute(self, command):
        """ Executes a command in the shell. """
        self.log.debug('Executing command: %s' % command)
        p = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.log.debug('[stdout] %s' % p.stdout.decode())
        self.log.debug('[stderr] %s' % p.stderr.decode())
