"""
Assistant for rapid research.
"""

import os
import argparse
import utils.servers
from tasks import control, start, status, stop, tb, train

TASKS = {
    'control': control.Control,
    'start': start.Start,
    'status': status.Status,
    'stop': stop.Stop,
    'tb': tb.Tensorboard,
    'train': train.Train,
}


def parse_args(servers, tasks):
    """ Adds subparsers and parses the arguments. """
    parser = argparse.ArgumentParser(description='Assistant for remote running.')
    parser.add_argument('server', choices=servers.keys(), help='Remote server.')
    subparsers = parser.add_subparsers(dest='task', help='Available commands.')
    for _, task in tasks.items():
        task.add_parser(subparsers)
    return parser.parse_args()


def main():
    # load server config
    base_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(base_dir, 'configs', 'servers.json')
    servers = utils.servers.load_servers(config_path)

    # run task
    args = parse_args(servers, TASKS)
    task = TASKS[args.task](servers[args.server])
    task.run(args)

if __name__ == '__main__':
    main()
