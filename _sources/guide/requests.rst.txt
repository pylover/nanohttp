Requests
========

nanohttp have one simple concept to working with requests and responses.
Each request will pass into a global object called as ``context`` and response
will generating from that.

.. note:: The ``context`` object is a proxy to an instance of ``nanohttp.Context`` which is ``unique per request``.

.. _requests-payload:

Payload
-------
Request payload will representing in ``context.form``, and supported request formats are
``query-string``, ``multipart/form-data``, ``application/x-www-form-urlencoded``
and ``json``.


..  code-block:: python

    from nanohttp import context, Controller, text

    class TipsControllers(Controller):

        @text
        def tip(self, tip_id: int = None):
            tip_title = context.form.get('title')
            return 'Tip: %s' % tip_title

.. note:: Query strings always directly can accessible with ``context.query_string``.


Decorators
----------
Decorators are useful to encapsulate response preparation such as setting ``Content-Type`` HTTP header.

Available decorators are: ``action``, ``html``, ``text``, ``json``, ``xml``, ``binary``

Of-course, you can set the response content type using:

..  code-block:: python

    context.response_content_type = 'application/pdf'

In Deep
~~~~~~~
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

Of-course, you can define your very own decorator to make your code
`DRY <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_:

..  code-block:: python

    import functools
    from nanohttp import action, RestController

    pdf = functools.partial(action, content_type='application/pdf')

    class MyController(RestController)

        @pdf
        def get(index):
            .......
