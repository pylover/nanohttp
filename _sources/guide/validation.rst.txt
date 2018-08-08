Validating requests
===================


A decorator named: `validate` is available to ensure the request parameters.

.. code-block:: python

   from nanohttp import validate

   ...

   @validate(field1=dict(required=True, min=20, max=100, type_=int, ... ))
   def index(self):
       ...


A complete list of validation options can be found here :func:`.validate`.


Values for those options can be a pair of ``criteria, http status``, for example:

.. code-block:: python

   @validate(field1=dict(
       required='400 Bad Request', 
       type_=(int, '470 Only integers are allowed here')
   )
   def index(self):
       ...


