"""
Starts the remote control worker.
"""

import os
import logging
import argparse
from workers.controller import Controller


def parse_args():
    parser = argparse.ArgumentParser(description='Starts the remote control worker.')
    parser.add_argument('--logpath', default=os.path.expanduser('~/logs/arr.log'),
                        help='Path to logfile.')
    parser.add_argument('--loglevel', default='INFO', help='Logging level.')
    return parser.parse_args()


def main(args):
    # configure logging
    logformat = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
    loglevel = logging.getLevelName(args.loglevel)
    logging.basicConfig(filename=args.logpath, format=logformat,level=loglevel)
    log = logging.getLogger('main')
    log.info('Starting system...')

    # start control worker
    log.info('Starting control worker...')
    c = Controller('localhost', 'control')
    c.start()
    c.add_cpu()
    log.info('System started')
    c.join()
    log.info('System stopped')

if __name__ == '__main__':
    main(parse_args())
