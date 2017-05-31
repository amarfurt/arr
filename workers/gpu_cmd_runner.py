"""
Runs a Tensorflow program on a GPU from the command line.
"""

import time
import logging
import subprocess
from workers.cmd_runner import CmdRunner


class GPUCmdRunner(CmdRunner):

    def __init__(self, host, queue, gpu):
        super().__init__(host, queue)
        self.name = '%s-%s-%d' % (host, queue, gpu)
        self.gpu = gpu
        self.log = logging.getLogger(self.name)

    def is_busy(self):
        """ Returns whether the assigned GPU is currently busy. """
        p = subprocess.run('nvidia-smi -i %d' % self.gpu,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL)
        output = p.stdout.decode()
        return 'No running processes found' not in output

    def run(self):
        # only start consuming when GPU is free
        self.log.debug('Checking whether GPU %d is free...' % self.gpu)
        while self.is_busy():
            time.sleep(10)
        self.log.debug('Starting work on GPU %d' % self.gpu)
        super().run()

    def execute(self, command):
        command = 'export CUDA_VISIBLE_DEVICES=%d; %s' % (self.gpu, command)
        super().execute(command)
