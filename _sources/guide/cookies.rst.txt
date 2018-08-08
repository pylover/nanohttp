Cookies
=======

Accessing the request cookies:

..  code-block:: python

    from nanohttp import context

    counter = context.cookies.get('counter')

Setting cookie:

..  code-block:: python

    from nanohttp import context

    context.cookies['dummy-cookie1'] = 'dummy-value'
    context.cookies['dummy-cookie1']['http_only'] = True

For more information on how to use cookies,
please check the python builtin's `http.cookies <https://docs.python.org/3
/library/http.cookies.html>`_.

