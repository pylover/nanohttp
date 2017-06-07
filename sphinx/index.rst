.. nanohttp documentation master file, created by
   sphinx-quickstart on Sat Mar 25 00:12:51 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

nanohttp
========

``hello.py``

.. code-block:: python

   from nanohttp import Controller, text

   class Root(Controller):
       @text
       def index(self):
           yield 'Hello World!'

.. code-block:: shell

   nanohttp hello


Features
--------

- Very simple, less-code & fast
- Using object dispatcher instead of regex route dispatcher.
- Url-Encoded, Multipart and JSON form parsing.
- No ``request`` and or ``response`` objects is available, everything is combined in ``nanohttp.context``.
- A very flexible configuration system: `pymlconf <https://github.com/pylover/pymlconf>`_
- Dispatching arguments using the `obj.__annonations__ <https://docs.python.org/3/library/typing.html>`_
- Method(verb) dispatcher.

Contents
--------

.. toctree::
   :maxdepth: 2

   quickstart
   tutorials/index
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
