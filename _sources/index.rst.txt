.. nanohttp documentation master file, created by
   sphinx-quickstart on Sat Mar 25 00:12:51 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



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

.. image:: https://img.shields.io/github/forks/pylover/nanohttp.svg?style=social&label=Fork
     :target: https://github.com/pylover/nanohttp/fork

.. image:: https://img.shields.io/github/stars/pylover/nanohttp.svg?style=social&label=Star
     :target: https://github.com/pylover/nanohttp


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
