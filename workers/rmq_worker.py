"""
RabbitMQ worker.
"""

import pika
import pika.exceptions
import logging
import threading
from abc import ABC, abstractmethod

TIMEOUT = 1  # in seconds


class Rabbit(threading.Thread, ABC):

    def __init__(self, host, queue):
        super().__init__()
        self.connection = None
        self.channel = None
        self.name = '%s-%s' % (host, queue)
        self.host = host
        self.queue = queue
        self.log = logging.getLogger(self.name)
        self.stopped = False

    def run(self):
        while not self.stopped:
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(self.callback, queue=self.queue)
                self.log.debug('Starting to consume...')
                self.check_alive()
                self.channel.start_consuming()
                self.log.debug('Stopped consuming')
            except pika.exceptions.ConnectionClosed:
                # reconnect after timeout
                self.log.debug('Connection closed. Reconnecting...')
            except:
                # something is wrong, exiting
                self.log.exception('Unexpected error')
                self.stop()

    def check_alive(self):
        """ Checks whether this worker is still active, otherwise shuts it down. """
        if not self.stopped:
            self.connection.add_timeout(TIMEOUT, self.check_alive)
        else:
            try:
                self.connection.close()
                self.log.info('Closed connection')
            except pika.exceptions.ConnectionClosed:
                self.log.debug('Connection already closed when stopping the worker.')

    def stop(self):
        """ Tells this worker to stop consuming messages. """
        self.stopped = True
        self.log.info('Stopping worker...')
        self.channel.stop_consuming()

    @abstractmethod
    def callback(self, channel, method, properties, body):
        """ Process a message from the queue. """
        pass
