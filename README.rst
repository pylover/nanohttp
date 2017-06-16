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

.. image:: https://img.shields.io/gitter/room/pylover/nanohttp.svg
     :target: https://gitter.im/pylover/nanohttp

A very micro HTTP framework.

Features
--------

- Very simple, less-code & fast
- Using object dispatcher instead of regex route dispatcher.
- Url-Encoded, Multipart and JSON form parsing.
- No ``request`` and or ``response`` objects is available, everything is combined in ``nanohttp.context``.
- A very flexible configuration system: `pymlconf <https://github.com/pylover/pymlconf>`_
- Dispatching arguments using the `obj.__annonations__ <https://docs.python.org/3/library/typing.html>`_
- Method(verb) dispatcher.

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

    from nanohttp import configure, Application

    configure(init_value='<yaml config string>', files=['path/to/config.file', '...'], dirs=['path/to/config/directory', '...'])
    app = Application(root=Root())
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

    quickstart(Root(), config='<YAML config string>')


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

    counter = context.cookies.get('counter')

Setting cookie:

..  code-block:: python

    from nanohttp import context, HttpCookie

    context.cookies['dummy-cookie1'] = 'dummy-value'
    context.cookies['dummy-cookie1']['http_only'] = True

For more information on how to use cookies, please check the python builtin's `http.cookies<https://docs.python.org/3/library/http.cookies.html>`_.


Trailing slashes
----------------

If the ``Controller.__remove_trailing_slash__`` is ``True``, then all trailing slashes are ignored.

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

Of-course, you can set the response content type using:

..  code-block:: python

    context.response_content_type = 'application/pdf'

Of-course, you can define your very own decorator to make your code DRY:

..  code-block:: python

    import functools
    from nanohttp import action, RestController

    pdf = functools.partial(action, content_type='application/pdf')

    class MyController(RestController)

        @pdf
        def get(index):
            .......


Serving Static file(s)
----------------------

The ``nanohttp.Static`` class is responsible to serve static files:

..  code-block:: python

    from nanohttp import Controller, Static

    class Root(Controller):
        static = Static('path/to/static/directory', default_document='index.html')

Then you can access static files on ``/static/filename.ext``

A simple way to run server and only serve static files is:

..  code-block:: bash

    cd path/to/static/directory
    nanohttp :Static


Accessing request payload
-------------------------

The `context.form` is a dictionary representing the request payload, supported request formats are ``query-string``,
``multipart/form-data``, ``application/x-www-form-urlencoded`` and ``json``.

..  code-block:: python

    from nanohttp import context, RestController

    class TipsControllers(RestController):

        @json
        def post(self, tip_id: int = None):
            tip_title = context.form.get('title')


Dispatcher
----------

The requested path will be split-ed by ``/`` and python's ``getattr`` will be used on the ``Root`` controller
recursively to find specific callable to handle request.

..  code-block:: python

    from nanohttp import RestController

    class Nested(RestController):
        pass

    class Root()
        children = Nested()

Then you can access methods on nested controller using: ``http://host:port/children``

On the ``RestController`` dispatcher tries to dispatch request using HTTP method(verb) at first.


Context
-------

The ``context`` object is a proxy to an instance of ``nanohttp.Context`` which is ``unique per request``.

.. TODO: ADD link to documentation

Hooks
-----

A few hooks are available in ``Controller`` class: ``begin_request``, ``begin_response``,
``end_response``.

For example this how I detect JWT token and refresh it if possible:


..  code-block:: python

    from nanohttp import Application, Controller, context

    class JwtApplication(Application):
        token_key = 'HTTP_AUTHORIZATION'
        refresh_token_cookie_key = 'refresh-token'

        def begin_request(self):
            if self.token_key in context.environ:
                encoded_token = context.environ[self.token_key]
                try:
                    context.identity = JwtPrincipal.decode(encoded_token)
                except itsdangerous.SignatureExpired as ex:
                    refresh_token_encoded = context.cookies.get(self.refresh_token_cookie_key)
                    if refresh_token_encoded:
                        # Extracting session_id
                        session_id = ex.payload.get('sessionId')
                        if session_id:
                            context.identity = new_token = self.refresh_jwt_token(refresh_token_encoded, session_id)
                            if new_token:
                                context.response_headers.add_header('X-New-JWT-Token', new_token.encode().decode())

                except itsdangerous.BadData:
                    pass

            if not hasattr(context, 'identity'):
                context.identity = None

Rendering templates
-------------------

This is how to use mako template engine with the nanohttp:


main.py


..  code-block:: python

    import functools
    from os.path import dirname, abspath, join

    from mako.lookup import TemplateLookup

    from nanohttp import Controller, context, Static, settings, action


    here = abspath(dirname(__file__))
    lookup = TemplateLookup(directories=[join(here, 'templates')])


    def render_template(func, template_name):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            result = func(*args, **kwargs)
            if hasattr(result, 'to_dict'):
                result = result.to_dict()
            elif not isinstance(result, dict):
                raise ValueError('The result must be an instance of dict, not: %s' % type(result))

            template_ = lookup.get_template(template_name)
            return template_.render(**result)

        return wrapper


    template = functools.partial(action, content_type='text/html', inner_decorator=render_template)


    class Root(Controller):
        static = Static(here)

        @template('index.mak')
        def index(self):
            return dict(
                settings=settings,
                environ=context.environ
            )



templates/index.html

..  code-block:: html

    <html>
    <head>
        <title>nanohttp mako example</title>
    </head>
    <body>
        <h1>WSGI environ</h1>
        <ul>
        %for key, value in environ.items():
          <li><b>${key}:</b> ${value}</li>
        %endfor
        </ul>
    </body>
    </html>

