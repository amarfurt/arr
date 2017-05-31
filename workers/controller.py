"""
Control process for workers. Takes commands from the 'control' queue.
"""

from workers.rmq_worker import Rabbit
from workers.cmd_runner import CmdRunner
from workers.gpu_cmd_runner import GPUCmdRunner


class Controller(Rabbit):

    def __init__(self, host, queue):
        super().__init__(host, queue)
        self.cpu_workers = []
        self.gpu_workers = {}

    def callback(self, channel, method, properties, body):
        """ Process control requests. """
        msg = body.decode()
        if msg.startswith('status'):
            self.status()
        elif msg.startswith('add cpu'):
            self.add_cpu()
        elif msg.startswith('remove cpu'):
            self.remove_cpu()
        elif msg.startswith('add gpu'):
            gpu = int(msg.split()[2])
            self.add_gpu(gpu)
        elif msg.startswith('remove gpu'):
            gpu = int(msg.split()[2])
            self.remove_gpu(gpu)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def status(self):
        """ Reports the current status. """
        # TODO: enqueue result in status queue / RPC pattern?
        pass

    def add_cpu(self):
        """ Adds a CPU worker. """
        cpu_worker = CmdRunner(self.host, 'cpu')
        self.cpu_workers.append(cpu_worker)
        cpu_worker.start()
        self.log.info('CPU worker added')

    def remove_cpu(self):
        """ Removes a CPU worker. """
        # TODO: remove an idle worker, for now removes the last in the list
        worker = self.cpu_workers.pop()
        worker.stop()
        self.log.info('CPU worker stopped')

    def add_gpu(self, gpu):
        """ Adds a GPU worker. """
        gpu_worker = GPUCmdRunner(self.host, 'gpu', gpu)
        self.gpu_workers[gpu] = gpu_worker
        gpu_worker.start()
        self.log.info('GPU worker %d added' % gpu)

    def remove_gpu(self, gpu):
        """ Removes a GPU worker. """
        # TODO
        self.gpu_workers[gpu].stop()
        del self.gpu_workers[gpu]
        self.log.info('GPU worker %d stopped' % gpu)
