"""
Runs a Tensorflow program on a CPU from the command line.
"""

from workers.cmd_runner import CmdRunner


class CPUCmdRunner(CmdRunner):

    def execute(self, command):
        # explicitly set GPUs to be invisible
        command = 'export CUDA_VISIBLE_DEVICES=""; %s' % command
        super().execute(command)
