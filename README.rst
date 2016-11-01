nanohttp
========

A very micro HTTP framework.

Features
--------

- Very simple, less-code & fast
- Using object dispatcher instead of regex route dispatcher.
- Url-Encoded & Multipart form parsing.

Roadmap
-------

The road map is to keep it simple. no built-in template engine and or ORM will be included.


Install
-------

PyPI
^^^^

..  code-block:: bash

    $ pip install --pre nanohttp


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

Are you need a ``WSGI`` application?

..  code-block:: python
    
    wsgi_app = Root().load_app()
    # Pass the ``app`` to every ``WSGI`` server you want.

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
