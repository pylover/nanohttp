nanohttp
========

A very micro HTTP framework.

Install
-------

PyPI
^^^^

..  code-block:: bash

    $ pip install nanohttp


Source
^^^^^^

..  code-block:: bash

    $ cd path/to/nanohttp
    $ pip install -e .


Quick Start
-----------

``demo.py``

..  code-block:: python

    from nanohttp import Controller, action, context
    
    class Root(Controller):
    
        @action()
        def index(self):
            yield from ('%s: %s\n' % i for i in context.environ.items())


..  code-block:: bash
    
    $ nanohttp demo

Or

..  code-block:: python
    
    from nanohttp import quickstart

    quickstart(Root())


Command Line Interface
----------------------

..  code-block:: bash

    $ nanohttp -h

    usage: nanohttp [-h] [-c CONFIG_FILE] [-b {HOST:}PORT] [-d DIRECTORY] [-V]
                    [MODULE{:CLASS}]
    
    positional arguments:
      MODULE{:CLASS}        The python module and controller class to launch.
                            default: `nanohttp:Demo`, And the default value for
                            `:CLASS` is `:Root` if omitted.
    
    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            Default: nanohttp.yaml
      -b {HOST:}PORT, --bind {HOST:}PORT
                            Bind Address. default: 8080
      -d DIRECTORY, --directory DIRECTORY
                            The path to search for the python module, which
                            contains the controller class. default is: `.`
      -V, --version         Show the version.
