"""
Script to enqueue a persistent message on the specified RabbitMQ queue.
"""

import pika
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Enqueues a message on a RabbitMQ queue.')
    parser.add_argument('--message', required=True, help='The message to enqueue.')
    parser.add_argument('--queue', required=True,
                        help='The name of the RabbitMQ queue to send the message to.')
    parser.add_argument('--host', default='localhost',
                        help='The host where the RabbitMQ server is running.')
    parser.add_argument('--rpc', default=None, help='The correlation ID (only for RPC calls).')
    return parser.parse_args()


def main(args):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=args.host))
    channel = connection.channel()
    channel.queue_declare(queue=args.queue, durable=True)
    properties = pika.BasicProperties(delivery_mode=2)
    if args.rpc:
        properties.reply_to = 'rpc_response'
        properties.correlation_id = args.rpc
    channel.basic_publish(exchange='', routing_key=args.queue, body=args.message,
                          properties=properties)
    connection.close()

if __name__ == '__main__':
    main(parse_args())
