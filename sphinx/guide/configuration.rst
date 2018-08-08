Configuration
=============

nanohttp have a great human-friendly configuration system with help of
`YAML <https://en.wikipedia.org/wiki/YAML>`_ and `pymlconf <https://github.com/pylover/pymlconf>`_.

Create a ``demo.yml`` file. The file below is same as the default configuration.

.. code-block:: yaml

   debug: true

   domain:

   cookie:
     http_only: false
     secure: false


You may use ``nanohttp.settings`` anywhere to access the config values.

.. code-block:: python

   from nanohttp import Controller, html, settings

   class Root(Controller):

       @html
       def index(self):
           yield '<html><head><title>nanohttp demo</title></head><body>'
           yield '<h2>debug flag is: %s</h2>' % settings.debug
           yield '</body></html>'

Passing the config file(s) using command line:

.. code-block:: bash

   $ nanohttp -c demo.yml [-c another.yml] demo


Passing the config file(s) Using python:

.. code-block:: bash

   from nanohttp import quickstart

   quickstart(Root(), config='<YAML config string>')



