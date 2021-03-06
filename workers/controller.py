"""
Control process for workers. Takes commands from the 'control' queue.
"""

import pika
from workers.rmq_worker import Rabbit
from workers.cpu_cmd_runner import CPUCmdRunner
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
            self.status(channel, properties)
        elif msg.startswith('add cpu'):
            self.add_cpu()
        elif msg.startswith('remove cpu'):
            self.remove_cpu()
        elif msg.startswith('add gpu'):
            gpus = list(map(int, msg.split()[2].split(',')))
            for gpu in gpus:
                self.add_gpu(gpu)
        elif msg.startswith('remove gpu'):
            gpus = list(map(int, msg.split()[2].split(',')))
            for gpu in gpus:
                self.remove_gpu(gpu)
        else:
            self.log.warn('Unknown message: %s' % msg)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def status(self, channel, properties):
        """ Reports the current status. """
        lines = ['%d CPU workers' % len(self.cpu_workers)]
        lines.extend([w.status() for w in self.cpu_workers])
        lines.append('%d GPU workers' % len(self.gpu_workers))
        lines.extend(['GPU %d: %s' % (gpu, w.status()) for (gpu, w) in self.gpu_workers.items()])
        message = '\n'.join(lines)
        channel.basic_publish(exchange='', routing_key=properties.reply_to, body=message,
                              properties=pika.BasicProperties(
                                  correlation_id=properties.correlation_id))

    def add_cpu(self):
        """ Adds a CPU worker. """
        cpu_worker = CPUCmdRunner(self.host, 'cpu')
        self.cpu_workers.append(cpu_worker)
        cpu_worker.start()
        self.log.info('CPU worker added')

    def remove_cpu(self):
        """ Removes a CPU worker. """
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
        if gpu in self.gpu_workers:
            self.gpu_workers[gpu].stop()
            del self.gpu_workers[gpu]
            self.log.info('GPU worker %d stopped' % gpu)
