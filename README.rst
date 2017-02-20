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
- Dispatching arguments using the `obj.__annonations__ <https://docs.python.org/3/library/typing.html>`_


Roadmap
-------

The road map is to keep it simple with 100% code coverage. no built-in template engine and or ORM will be included.


Install
-------

PyPI
^^^^

..  code-block:: bash

    $ pip install nanohttp


From Source
^^^^^^^^^^^

..  code-block:: bash

    $ cd path/to/nanohttp
    $ pip install -e .


Quick Start
-----------

``demo.py``

..  code-block:: python

    from nanohttp import Controller, RestController, context, html, json, HttpFound


    class TipsControllers(RestController):
        @json
        def get(self, tip_id: int = None):
            if tip_id is None:
                return [dict(id=i, title="Tip %s" % i) for i in range(1, 4)]
            else:
                return dict(
                    id=tip_id,
                    title="Tip %s" % tip_id
                )

        @json
        def post(self, tip_id: int = None):
            tip_title = context.form.get('title')
            print(tip_id, tip_title)

            # Updating the tips title
            # TipStore.get(tip_id).update(tip_title)
            raise HttpFound('/tips/')


    class Root(Controller):
        tips = TipsControllers()

        @html
        def index(self):
            yield """
            <html><head><title>nanohttp Demo</title></head><body>
            <form method="POST" action="/tips/2">
                <input type="text" name="title" />
                <input type="submit" value="Update" />
            </form>
            </body></html>
            """


..  code-block:: bash
    
    $ nanohttp demo

Or

..  code-block:: python
    
    from nanohttp import quickstart

    quickstart(Root())


WSGI
----

Do you need a ``WSGI`` application?

``wsgi.py``

..  code-block:: python

    from nanohttp import configure

    configure(config='<yaml config string>', config_files='path/to/config.file')
    app = Root().load_app()
    # Pass the ``app`` to any ``WSGI`` server you want.


Serve it by gunicorn:

..  code-block:: bash

    gunicorn --reload wsgi:app


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
