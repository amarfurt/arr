"""
RabbitMQ worker.
"""

import pika
import pika.exceptions
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
        while True:
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(self.callback, queue=self.queue)
                self.channel.start_consuming()
            except pika.exceptions.ConnectionClosed:
                # reconnect after timeout
                self.log.debug('Connection closed. Reconnecting...')
                pass
            except:
                # something is wrong, exiting
                self.log.exception('Unexpected error')
                self.stop()
                break

    def stop(self):
        """ Tells this worker to stop consuming messages. """
        try:
            self.log.info('Stopping worker...')
            # TODO: is this blocking?
            self.channel.stop_consuming()
            self.log.info('Stopped consuming')
            self.connection.close()
            self.log.info('Closed connection')
        except pika.exceptions.ConnectionClosed:
            # connection already closed, exiting
            self.log.debug('Connection already closed when stopping the worker.')
            pass

    @abstractmethod
    def callback(self, channel, method, properties, body):
        """ Process a message from the queue. """
        pass
