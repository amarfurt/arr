"""
Assistant for rapid research.
"""

import os
import argparse
from tasks import tb, train, status
from utils.servers import Servers


def init_tasks():
    """ Initialize tasks. """
    base_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(base_dir, 'configs', 'servers.json')
    servers = Servers(config_path)
    return {
        'status': status.Status(servers),
        'train': train.Train(servers),
        'tb': tb.Tensorboard(servers)
    }


def parse_args(tasks):
    """ Adds subparsers and parses the arguments. """
    parser = argparse.ArgumentParser(description='Assistant for remote running.')
    subparsers = parser.add_subparsers(dest='task', help='Available commands.')
    for _, task in tasks.items():
        task.add_parser(subparsers)
    return parser.parse_args()


def main():
    tasks = init_tasks()
    args = parse_args(tasks)
    tasks[args.task].run(args)

if __name__ == '__main__':
    main()
