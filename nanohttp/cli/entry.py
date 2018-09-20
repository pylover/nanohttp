import sys
from os import chdir
from os.path import relpath, isdir, join
from importlib.util import spec_from_file_location, module_from_spec

import yaml

import nanohttp
from ..configuration import configure, settings
from ..helpers import quickstart
from .parser import parse_arguments


def load_controller_from_file(specifier):
    controller = None

    if specifier:
        module_name, class_name = specifier.split(':') \
            if ':' in specifier else (specifier, 'Root')

        if module_name:

            if isdir(module_name):
                location = join(module_name, '__init__.py')
            elif module_name.endswith('.py'):
                location = module_name
                module_name = module_name[:-3]
            else:
                location = '%s.py' % module_name

            spec = spec_from_file_location(module_name, location=location)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            controller = getattr(module, class_name)()

        elif class_name == 'Static':
            from ..controllers import Static
            controller = Static()
        else:  # pragma: no cover
            controller = globals()[class_name]()

    return controller


def main(argv=None):
    args = parse_arguments(argv=argv)

    if args.version:  # pragma: no cover
        print(nanohttp.__version__)
        return 0

    try:
        host, port = args.bind.split(':')\
            if ':' in args.bind else ('', args.bind)

        # Change dir
        if relpath(args.directory, '.') != '.':
            chdir(args.directory)

        configure(force=True)

        for f in args.config_files:
            settings.load_file(f)


        try:
            for option in args.options:
                key, value = option.split('=')
                value = yaml.load(value)
                if isinstance(value, str):
                    value = f'"{value}"'

                exec(f'settings.{key} = {value}')
        except AttributeError:
            print(f'Invalid configuration option: {key}', file=sys.stderr)
            return 1

        quickstart(
            controller=load_controller_from_file(args.controller),
            host=host,
            port=int(port)
        )
    except KeyboardInterrupt:  # pragma: no cover
        print('CTRL+C detected.')
        return 15
    else:  # pragma: no cover
        return 0

