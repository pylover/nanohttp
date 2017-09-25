
import sys
from os import chdir
from os.path import relpath, basename

import nanohttp
from .helpers import quickstart, load_controller_from_file
from .configuration import configure

DEFAULT_CONFIG_FILE = 'nanohttp.yml'
DEFAULT_ADDRESS = '8080'


def parse_arguments(argv=None):
    import argparse

    argv = argv or sys.argv

    parser = argparse.ArgumentParser(prog=basename(argv[0]))
    parser.add_argument('-c', '--config-file', action='append', default=[], help='This option may be passed multiple '
                                                                                 'times.')
    parser.add_argument('-d', '--config-directory', action='append', default=[], help='This option may be passed '
                                                                                      'multiple times.')
    parser.add_argument('-b', '--bind', default=DEFAULT_ADDRESS, metavar='{HOST:}PORT', help='Bind Address. default: '
                                                                                             '%s' % DEFAULT_ADDRESS)
    parser.add_argument('-C', '--directory', default='.', help='Change to this path before starting the server '
                                                               'default is: `.`')
    parser.add_argument('-V', '--version', default=False, action='store_true', help='Show the version.')
    parser.add_argument('controller', nargs='?', metavar='{MODULE{.py}}{:CLASS}',
                        help='The python module and controller class to launch. default is python built-in\'s : '
                             '`demo_app`, And the default value for `:CLASS` is `:Root` if omitted.')

    return parser.parse_args(argv[1:])


def main(argv=None):
    args = parse_arguments(argv=argv)

    if args.version:  # pragma: no cover
        print(nanohttp.__version__)
        return 0

    try:
        host, port = args.bind.split(':') if ':' in args.bind else ('', args.bind)

        # Change dir
        if relpath(args.directory, '.') != '.':
            chdir(args.directory)

        configure(files=args.config_file, dirs=args.config_directory, force=True)

        quickstart(
            controller=load_controller_from_file(args.controller),
            host=host,
            port=int(port)
        )
    except KeyboardInterrupt:  # pragma: no cover
        print('CTRL+C detected.')
        return -1
    else:  # pragma: no cover
        return 0
