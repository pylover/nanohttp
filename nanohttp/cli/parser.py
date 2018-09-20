import sys
from os.path import basename


DEFAULT_CONFIG_FILE = 'nanohttp.yml'
DEFAULT_ADDRESS = '8080'


def parse_arguments(argv=None):
    import argparse

    argv = argv or sys.argv

    parser = argparse.ArgumentParser(prog=basename(argv[0]))
    parser.add_argument(
        '-c',
        '--config-file',
        action='append',
        default=[],
        dest='config_files',
        help='This option may be passed multiple times.'
    )

    parser.add_argument(
        '-b',
        '--bind',
        default=DEFAULT_ADDRESS,
        metavar='{HOST:}PORT',
        help='Bind Address. default: %s' % DEFAULT_ADDRESS
    )

    parser.add_argument(
        '-C',
        '--directory',
        default='.',
        help='Change to this path before starting the server default is: `.`'
    )

    parser.add_argument(
        '-V',
        '--version',
        default=False,
        action='store_true',
        help='Show the version.'
    )

    parser.add_argument(
        'controller',
        nargs='?',
        metavar='{MODULE{.py}}{:CLASS}',
        help='The python module and controller class to launch. default is '
             'python built-in\'s : `demo_app`, And the default value for '
             '`:CLASS` is `:Root` if omitted.'
    )

    parser.add_argument(
        '-o', '--option',
        action='append',
        metavar='key1.key2=value',
        dest='options',
        default=[],
        help= \
            'Configuration value to override. this option could be passed ' \
            'multiple times.'
    )

    return parser.parse_args(argv[1:])


