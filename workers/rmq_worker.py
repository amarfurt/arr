"""
RabbitMQ worker.
"""

import pika
import logging
import threading
from abc import ABC, abstractmethod


class Rabbit(threading.Thread, ABC):

    def __init__(self, host, queue):
        super().__init__()
        self.connection = None
        self.channel = None
        self.name = '%s-%s' % (host, queue)
        self.host = host
        self.queue = queue
        self.log = logging.getLogger(self.name)

    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue=self.queue)
        while True:
            try:
                self.channel.start_consuming()
            except:
                # TODO: how does it continue after an exception?
                self.log.exception('Unexpected error')

    def stop(self):
        """ Tells this worker to stop consuming messages. """
        self.log.info('Stopping worker...')
        self.channel.stop_consuming()
        self.log.info('Stopped consuming')
        self.connection.close()
        self.log.info('Closed connection')

    @abstractmethod
    def callback(self, channel, method, properties, body):
        """ Process a message from the queue. """
        pass
