WSGI
====

| The Web Server Gateway Interface (WSGI) is a specification for simple and universal
  interface between web servers and web applications
  or frameworks for the Python programming language. [#f1]_

So nanohttp application designed with WSGI
(originally specified as `PEP333 <https://www.python.org/dev/peps/pep-0333/>`_) standards,
this sample show you how to use it:

``wsgi.py``

.. code-block:: python

    from nanohttp import Application, Controller, html, configure


    class RootController(Controller):

        @html
        def index(self):
            return '<h1>HelloWorld!</h1>'


    class MyApplication(Application):
        __root__ = RootController()


    configure()
    app = MyApplication()


We need a `WSGI server <https://www.fullstackpython.com/wsgi-servers.html>`_
like `gunicorn <http://gunicorn.org/>`_ or `uWSGI <http://uwsgi-docs.readthedocs.org/en/latest/>`_
to serve application.

for example with gunicorn:

.. code-block:: bash

    $ gunicorn -b :8080 wsgi:app

now application can accessible through the browser in http://localhost:8080.

.. rubric:: ---

.. [#f1] `wikipedia <https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface>`_.
