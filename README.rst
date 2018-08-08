nanohttp
========

.. image:: http://img.shields.io/pypi/v/nanohttp.svg
   :target: https://pypi.python.org/pypi/nanohttp

.. image:: https://travis-ci.org/Carrene/nanohttp.svg?branch=master
   :target: https://travis-ci.org/Carrene/nanohttp

.. image:: https://coveralls.io/repos/github/Carrene/nanohttp/badge.svg?branch=master
   :target: https://coveralls.io/github/Carrene/nanohttp?branch=master

.. image:: https://badges.gitter.im/Carrene/nanohttp.svg
   :alt: Join the chat at https://gitter.im/Carrene/nanohttp
   :target: https://gitter.im/Carrene/nanohttp?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

A very micro HTTP framework. `documentation <http://nanohttp.org>`_



Cookies
-------

Accessing the request cookies:


.. code-block:: python

   from nanohttp import context

   counter = context.cookies.get('counter')

Setting cookie:

.. code-block:: python

   from nanohttp import context

   context.cookies['dummy-cookie1'] = 'dummy-value'
   context.cookies['dummy-cookie1']['http_only'] = True

For more information on how to use cookies, please check the python builtin's 
`http.cookies <https://docs.python.org/3/library/http.cookies.html>`_.


Trailing slashes
----------------

If the ``Controller.__remove_trailing_slash__`` is ``True``, then all trailing slashes are ignored.

.. code-block:: python

   def test_trailing_slash(self):
       self.assert_get('/users/10/jobs/', expected_response='User: 10\nAttr: jobs\n')


Decorators to indicate http handlers
------------------------------------

Available decorators are: ``action``, ``html``, ``text``, ``json``, ``xml``, ``binary``

Those decorators are useful to encapsulate response preparation such as setting ``Content-Type`` HTTP header.

Take a look at the code of the ``action`` decorator, all other decorators are derived from this:


.. code-block:: python

   def action(*args, verbs: Union[str, list, tuple]='any', encoding: str='utf-8',
              content_type: Union[str, None]=None,
              inner_decorator: Union[callable, None]=None,
              prevent_empty_form=None, prevent_form=None, **kwargs):
       ...



Other decorators are defined using ``functools.partial``:

.. code-block:: python

   html = functools.partial(action, content_type='text/html')
   text = functools.partial(action, content_type='text/plain')
   json = functools.partial(action, content_type='application/json', inner_decorator=jsonify)
   xml = functools.partial(action, content_type='application/xml')
   binary = functools.partial(action, content_type='application/octet-stream', encoding=None)

Of-course, you can set the response content type using:

.. code-block:: python

   context.response_content_type = 'application/pdf'

Of-course, you can define your very own decorator to make your code DRY:

.. code-block:: python

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

.. code-block:: python

   from nanohttp import Controller, Static

   class Root(Controller):
       static = Static('path/to/static/directory', default_document='index.html')


Then you can access static files on ``/static/filename.ext``

A simple way to run server and only serve static files is:

.. code-block:: bash

   cd path/to/static/directory
   nanohttp :Static


Accessing request payload
-------------------------

The `context.form` is a dictionary representing the request payload, supported request formats are ``query-string``,
``multipart/form-data``, ``application/x-www-form-urlencoded`` and ``json``.

.. code-block:: python

   from nanohttp import context, RestController

   class TipsControllers(RestController):

       @json
       def post(self, tip_id: int = None):
           tip_title = context.form.get('title')


Validating request
------------------

A decorator named: `validate` is available to ensure the request parameters.

.. code-block:: python

   from nanohttp import validate

   ...

   @validate(field1=dict(required=True, min=20, max=100, type_=int, ... ))
   def index(self):
       ...


A complete list of validation options is:


- ``required``: Boolean or str, indicates the field is required.
- ``not_none``: Boolean or str, Raise when field is given and it's value is 
                None.
- ``type_``: A callable to pass the received value to it as the only argument 
             and get it in the apprpriate type, Both ``ValueError`` and 
             ``TypeError`` may be raised if the value cannot casted to the 
             specified type. A good example of this callable would be the 
             ``int``.
- ``minimum``: Numeric, Minimum allowed value.
- ``maximum``: Numeric, Maximum allowed value.
- ``pattern``: Regex pattern to match the value.
- ``min_length``: Only for strings, the minumum allowed length of the value.
- ``max_length``: Only for strings, the maximum allowed length of the value.

Values for those options can be a pair of ``criteria, http status``, for example:

.. code-block:: python

   @validate(field1=dict(
       required='400 Bad Request', 
       min=(20, '471 Minimum allowed value is 20'),
       max=(100, '472 Maximum allowed value is 100'),
       type_=(int, '470 Only integers are allowed here')
   )
   def index(self):
       ...



Dispatcher
----------

The requested path will be split-ed by ``/`` and python's ``getattr`` will be used on the ``Root`` controller
recursively to find specific callable to handle request.

.. code-block:: python

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


Hooks
-----

A few hooks are available in ``Controller`` class: ``begin_request``, ``begin_response``,
``end_response``.

For example this how I detect JWT token and refresh it if possible:


.. code-block:: python

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


.. code-block:: python

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

.. code-block:: html

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

