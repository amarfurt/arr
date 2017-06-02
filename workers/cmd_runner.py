"""
Runs command-line operations.
"""

import time
import json
import datetime
import subprocess
from workers.rmq_worker import Rabbit


class CmdRunner(Rabbit):

    def __init__(self, host, queue):
        super().__init__(host, queue)
        self.start_time = time.time()
        self.last_job_time = None
        self.cur_job_time = None

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
        self.cur_job_time = time.time()
        p = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.log.debug('[stdout] %s' % p.stdout.decode())
        self.log.debug('[stderr] %s' % p.stderr.decode())
        self.last_job_time = time.time() - self.cur_job_time
        self.cur_job_time = None

    def status(self):
        """ Returns the current status of this worker. """
        durations = [('Uptime', time.time() - self.start_time)]
        if self.last_job_time:
            durations.append(('last job', self.last_job_time))
        if self.cur_job_time:
            durations.append(('current job', time.time() - self.cur_job_time))
        else:
            durations.append(('currently idle', 0))
        return ', '.join(['%s: %s' % (k, datetime.timedelta(seconds=int(v))) for k, v in durations])
