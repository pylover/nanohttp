
Payload
-------
Request payload will representing in ``context.form``, and supported request 
formats are ``query``, ``multipart/form-data``, 
``application/x-www-form-urlencoded`` and ``json``.


.. code-block:: python

   from nanohttp import context, Controller, text

   class TipsControllers(Controller):

       @text
       def tip(self, tip_id: int = None):
           tip_title = context.form.get('title')
           return 'Tip: %s' % tip_title


.. note:: Query strings always directly can accessible with ``context.query``.

