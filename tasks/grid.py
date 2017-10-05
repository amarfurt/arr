"""
Grid search over a set of parameters.
"""

import json
import paramiko
import argparse
import itertools
from tasks.task import Task

PREFIX = '$'


class Grid(Task):

    @staticmethod
    def add_parser(registry):
        parser = registry.add_parser('grid', help='Run a grid search over a set of parameters.')
        parser.add_argument('config', help='Path to base config file with placeholders '
                                           '(prefixed with %s).' % PREFIX)
        parser.add_argument('args', nargs=argparse.REMAINDER,
                            help='List of parameters to do the grid search over. '
                                 'Format: --name value1,value2')
        # The --cpu argument will only be recognized if it appears in the first position.
        # We handle it either way when parsing args below.
        parser.add_argument('--cpu', action='store_true', help='Run on CPU instead of GPU.')

    def run(self, args):
        """ Adds a run configuration to the 'gpu' or 'cpu' queue. """
        # parse arguments
        use_cpu = args.cpu
        params = {}
        key = None
        for arg in args.args:
            if arg == '--cpu':
                use_cpu = True
            elif arg.startswith('--'):
                key = arg[2:]
            else:
                values = arg.split(',')
                params[key] = values

        # build all combinations of params for grid search
        settings = []
        value_combinations = itertools.product(*params.values())
        for vc in value_combinations:
            settings.append(dict(zip(params.keys(), vc)))

        # read the config file with placeholders
        with open(args.config, 'r') as f:
            raw_config = f.read()

        # replace the placeholders
        config_strings = []
        for s in settings:
            config_string = raw_config
            for param in s:
                config_string = config_string.replace(PREFIX + param, s[param])
            config_strings.append(config_string)

        # parse to make sure the config is well-formed json
        configs = []
        for cs in config_strings:
            try:
                configs.append(json.loads(cs))
            except json.decoder.JSONDecodeError:
                print('Invalid json: %s' % cs)

        # enqueue the valid config files on the respective queue
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(self.server.address)
        queue = 'cpu' if use_cpu else 'gpu'
        for config in configs:
            client.exec_command("python3 code/arr/enqueue.py --queue %s --message '%s'"
                                % (queue, json.dumps(config)))
        client.close()
