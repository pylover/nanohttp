nanohttp
========

.. image:: http://img.shields.io/pypi/v/nanohttp.svg
     :target: https://pypi.python.org/pypi/nanohttp

.. image:: https://requires.io/github/pylover/nanohttp/requirements.svg?branch=master
     :target: https://requires.io/github/pylover/nanohttp/requirements/?branch=master
     :alt: Requirements Status

.. image:: https://travis-ci.org/pylover/nanohttp.svg?branch=master
     :target: https://travis-ci.org/pylover/nanohttp

.. image:: https://coveralls.io/repos/github/pylover/nanohttp/badge.svg?branch=master
     :target: https://coveralls.io/github/pylover/nanohttp?branch=master


A very micro HTTP framework.

Features
--------

- Very simple, less-code & fast
- Using object dispatcher instead of regex route dispatcher.
- Url-Encoded & Multipart form parsing.
- No ``request`` and or ``response`` objects is available, everything is combined in ``nanohttp.context``.
- You can use `maryjane <https://github.com/pylover/maryjane>`_ to observe the changes in your project directory and reload
  the development server if desired.
- A very flexible configuration system: `pymlconf <https://github.com/pylover/pymlconf>`_


Roadmap
-------

The road map is to keep it simple with 100% code coverage. no built-in template engine and or ORM will be included.


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
    from nanohttp import Controller, html, context, Static, HttpFound, settings

    class Root(Controller):
        static = Static(abspath(dirname(__file__)))

        @html
        def index(self):
            yield '<html><head><title>nanohttp demo</title></head><body>'
            yield '<h1>nanohttp demo page</h1>'
            yield '<h2>debug flag is: %s</h2>' % settings.debug
            yield '<img src="/static/cat.jpg" />'
            yield '<ul>'
            yield from ('<li><b>%s:</b> %s</li>' % i for i in context.environ.items())
            yield '</ul>'
            yield '</body></html>'

        @html(methods=['post', 'put'])
        def contact(self):
            yield '<h1>Thanks: %s</h1>' % context.form['name'] if context.form else 'Please send a name.'

        @html
        def google(self):
            raise HttpFound('http://google.com')

        @html
        def error(self):
            raise Exception()


..  code-block:: bash
    
    $ nanohttp demo

Or

..  code-block:: python
    
    from nanohttp import quickstart

    quickstart(Root())


WSGI
----

Do you need a ``WSGI`` application?

..  code-block:: python

    from nanohttp import configure

    configure(config='<yaml config string>', config_files='path/to/config.file')
    app = Root().load_app()
    # Pass the ``app`` to any ``WSGI`` server you want.


Watch
-----

Create a ``maryjane.yml`` file:

..  code-block:: yml

    port: 8080
    module: demo.py
    controller: Root
    config_file: demo.yml

    # Storing the pid of current running server into the `pid` variable.
    SHELL-INTO: pid netstat -lnpt 2>/dev/null | grep {port} | awk '{{split($7,a,"/"); printf a[1]}}'
    ECHO: Old pid: {pid}

    SHELL:
      - if [ -n "{pid}" ]; then  kill -9 {pid}; fi
      - while [ -n "{pid}" -a -e /proc/{pid} ]; do sleep .6; done
      - nanohttp -b {port} -c {config_file} {module}:{controller} & echo New pid: $!

    WATCH-ALL:
      - !^{here}[a-z0-9\.-_/]+\.(css|py|yml|js|html)$


..  code-block:: bash

    $ pip3.6 install "maryjane>=4.4.0"
    $ maryjane -w


Config File
-----------

Create a ``demo.yml`` file. The file below is same as the default configuration.

..  code-block:: yml

    debug: true

    domain:

    cookie:
      http_only: false
      secure: false


You may use ``nanohttp.settings`` anywhere to access the config values.

..  code-block:: python

    from nanohttp import Controller, html, settings

    class Root(Controller):

        @html
        def index(self):
            yield '<html><head><title>nanohttp demo</title></head><body>'
            yield '<h2>debug flag is: %s</h2>' % settings.debug
            yield '</body></html>'

Passing the config file(s) using command line:

..  code-block:: bash

    $ nanohttp -c demo.yml [-c another.yml] demo


Passing the config file(s) Using python:

..  code-block:: bash

    from nanohttp import quickstart

    quickstart(Root(), config_files=['file1', 'file2'])


Command Line Interface
----------------------

..  code-block:: bash

    $ nanohttp -h

    usage: nanohttp [-h] [-c CONFIG_FILE] [-b {HOST:}PORT] [-d DIRECTORY] [-V]
                    [MODULE{.py}{:CLASS}]

    positional arguments:
      MODULE{.py}{:CLASS}   The python module and controller class to launch.
                            default is python built-in's : `demo_app`, And the
                            default value for `:CLASS` is `:Root` if omitted.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            This option may be passed multiple times.
      -b {HOST:}PORT, --bind {HOST:}PORT
                            Bind Address. default: 8080
      -d DIRECTORY, --directory DIRECTORY
                            The path to search for the python module, which
                            contains the controller class. default is: `.`
      -V, --version         Show the version.
