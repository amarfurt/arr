"""
Script to dequeue a message from the specified RabbitMQ queue.
"""

import pika
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Dequeues a message from a RabbitMQ queue.')
    parser.add_argument('--queue', required=True,
                        help='The name of the RabbitMQ queue to send the message to.')
    parser.add_argument('--host', default='localhost',
                        help='The host where the RabbitMQ server is running.')
    parser.add_argument('--rpc', default=None, help='The correlation ID (only for RPC calls).')
    return parser.parse_args()


def main(args):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=args.host))
    channel = connection.channel()
    queue = channel.queue_declare(queue=args.queue, durable=True)
    method, properties, body = channel.basic_get(queue=args.queue)
    if args.rpc:
        waiting_count = 0
        while (not args.rpc == properties.correlation_id
               and waiting_count < queue.method.message_count):
            method, properties, body = channel.basic_get(queue=args.queue)
            waiting_count += 1
        print(body.decode())
        channel.basic_ack(delivery_tag=method.delivery_tag)
        if waiting_count > 0:
            print('WARNING: %d messages in response queue.' % waiting_count)
    else:
        print(body.decode())
        channel.basic_ack(delivery_tag=method.delivery_tag)
    connection.close()

if __name__ == '__main__':
    main(parse_args())
