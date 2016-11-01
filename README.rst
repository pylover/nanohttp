nanohttp
========

A very micro HTTP framework.

Features
--------

- Very simple, less-code & fast
- Using object dispatcher instead of regex route dispatcher.
- Url-Encoded & Multipart form parsing.
- No `request` or `response` objects are available, everything is combined in `nanohttp.context`.

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

    from os.path import dirname, abspath
    from nanohttp import Controller, html, context, Static
    
    
    class Root(Controller):
        static = Static(abspath(dirname(__file__)))
    
        @html
        def index(self):
            yield '<img src="/static/cat.jpg" />'
            yield '<ul>'
            yield from ('<li><b>%s:</b> %s</li>' % i for i in context.environ.items())
            yield '</ul>'
    
        @html(methods=['post', 'put'])
        def contact(self):
            yield '<h1>Thanks: %s</h1>' % context.form['name'] if context.form else 'Please send a name.'


..  code-block:: bash
    
    $ nanohttp demo

Or

..  code-block:: python
    
    from nanohttp import quickstart

    quickstart(Root())

Are you need a ``WSGI`` application?

..  code-block:: python
    
    app = Root().load_app()
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
