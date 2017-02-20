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

    usage: nanohttp [-h] [-c CONFIG_FILE] [-d CONFIG_DIRECTORY] [-b {HOST:}PORT]
                    [-C DIRECTORY] [-V]
                    [{MODULE{.py}}{:CLASS}]

    positional arguments:
      {MODULE{.py}}{:CLASS}
                            The python module and controller class to launch.
                            default is python built-in's : `demo_app`, And the
                            default value for `:CLASS` is `:Root` if omitted.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            This option may be passed multiple times.
      -d CONFIG_DIRECTORY, --config-directory CONFIG_DIRECTORY
                            This option may be passed multiple times.
      -b {HOST:}PORT, --bind {HOST:}PORT
                            Bind Address. default: 8080
      -C DIRECTORY, --directory DIRECTORY
                            Change to this path before starting the server default
                            is: `.`
      -V, --version         Show the version.


Cookies
-------

Accessing the request cookies:


..  code-block:: python

    from nanohttp import context

    counter = context.cookies.get('counter', 0)

Setting cookie:

..  code-block:: python

    from nanohttp import context, HttpCookie

    context.response_cookies.append(HttpCookie('dummy-cookie1', value='dummy', http_only=True))


Trailing slashes
----------------

All trailing slashes are ignored.

..  code-block:: python

    def test_trailing_slash(self):
        self.assert_get('/users/10/jobs/', expected_response='User: 10\nAttr: jobs\n')

Decorators
----------

Available decorators are: ``action``, ``html``, ``text``, ``json``, ``xml``, ``binary``

Those decorators are useful to encapsulate response preparation such as setting ``Content-Type`` HTTP header.

Take a look at the code of the ``action`` decorator, all other decorators are derived from this:


..  code-block:: python

    def action(*verbs, encoding='utf-8', content_type=None, inner_decorator=None):
        def _decorator(func):

            if inner_decorator is not None:
                func = inner_decorator(func)

            func.__http_methods__ = verbs if verbs else 'any'

            func.__response_encoding__ = encoding

            if content_type:
                func.__content_type__ = content_type

            return func

        if verbs and callable(verbs[0]):
            f = verbs[0]
            verbs = tuple()
            return _decorator(f)
        else:
            return _decorator

Other decorators are defined using ``functools.partial``:

..  code-block:: python

    html = functools.partial(action, content_type='text/html')
    text = functools.partial(action, content_type='text/plain')
    json = functools.partial(action, content_type='application/json', inner_decorator=jsonify)
    xml = functools.partial(action, content_type='application/xml')
    binary = functools.partial(action, content_type='application/octet-stream', encoding=None)
