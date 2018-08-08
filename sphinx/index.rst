.. nanohttp documentation master file, created by
   sphinx-quickstart on Sat Mar 25 00:12:51 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



.. image:: http://img.shields.io/pypi/v/nanohttp.svg
     :target: https://pypi.python.org/pypi/nanohttp

.. image:: https://travis-ci.org/Carrene/nanohttp.svg?branch=master
     :target: https://travis-ci.org/Carrene/nanohttp

.. image:: https://coveralls.io/repos/github/Carrene/nanohttp/badge.svg?branch=master
     :target: https://coveralls.io/github/Carrene/nanohttp?branch=master

.. image:: https://img.shields.io/gitter/room/Carrene/nanohttp.svg
     :target: https://gitter.im/Carrene/nanohttp

.. image:: https://img.shields.io/github/forks/Carrene/nanohttp.svg?style=social&label=Fork
     :target: https://github.com/Carrene/nanohttp/fork

.. image:: https://img.shields.io/github/stars/Carrene/nanohttp.svg?style=social&label=Star
     :target: https://github.com/Carrene/nanohttp


########
nanohttp
########

A very micro HTTP framework.

********
Features
********

- Very simple, less-code & fast
- Object/Attribute URL dispatcher
- Regex route dispatcher
- HTTP Method(Verb) dispatcher
- Url-Encoded, Multipart and JSON form parsing
- No ``request`` and or ``response`` objects is available, 
  everything is combined in ``nanohttp.context``
- A very flexible configuration system: 
  `pymlconf <https://github.com/pylover/pymlconf>`_
- Use Python's `keywordonly <https://www.python.org/dev/peps/pep-3102/>`_ 
  arguments for query strings (>= 0.24.0)


*******
Roadmap
*******

The roadmap is to keep it simple with 100% code coverage. no built-in 
template engine and or ORM will be included.


********
Contents
********

.. toctree::
   :maxdepth: 2

   quickstart
   installation
   cli
   guide/index
   api/index
   development/index
   more/index



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
