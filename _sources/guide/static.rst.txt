Serving Static files
====================

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


