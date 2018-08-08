Context
=======

nanohttp have one simple concept to working with requests and responses.
Each request will pass into a global object called as ``context`` and response
will generating from that.

.. note:: The ``context`` object is a proxy to an instance of 
          ``nanohttp.Context`` which is ``unique per request``.


