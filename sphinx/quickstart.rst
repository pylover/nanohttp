Quickstart
==========

Here is a sample for running your application with zero configuration.


``demo.py``

.. code-block:: python

   from nanohttp import Controller, RestController, context, html, json, \
       HTTPFound
   
   
   tips = [
       dict(id=i, title="Tip %s" % i) for i in range(1, 4)
   ]
   
   
   class TipsControllers(RestController):
       @json
       def get(self, tip_id: int = None):
           if tip_id is None:
               return tips
   
           for tip in tips:
               if tip['id'] == int(tip_id):
                   return tip
   
           raise HTTPNotFound(f'Tip: {tip_id} is not found')
   
       @json(prevent_empty_form=True)
       def post(self):
           tip_title = context.form.get('title')
           # Updating the tips global variable
           tip_id = len(tips)+1
           tips.append(dict(id=tip_id, title=tip_title))
           raise HTTPFound('/tips/')
   
   
   class Root(Controller):
       tips = TipsControllers()
   
       @html(prevent_form='400 Form Not Allowed')
       def index(self):
           yield """
           <html><head><title>nanohttp Demo</title></head><body>
           <form method="POST" action="/tips/">
               <input type="text" name="title" />
               <input type="submit" value="Update" />
           </form>
           </body></html>
           """

.. code-block:: bash
    
   $ nanohttp demo

Or

.. code-block:: python
    
   from nanohttp import quickstart, configure

   configure()
   quickstart(Root())


Do you need a ``WSGI`` application?

``wsgi.py``

.. code-block:: python

   from nanohttp import configure, Application

   configure(init_value='<yaml config string>', files=['path/to/config.file', '...'], dirs=['path/to/config/directory', '...'])
   app = Application(root=Root())
   # Pass the ``app`` to any ``WSGI`` server you want.


Serve it by gunicorn:

.. code-block:: bash

   gunicorn --reload wsgi:app


.. note:: ``nanohttp`` CLI command and ``quickstart`` automatically will set 
          your root controller to :doc:`application`.

.. seealso:: If your application is ready to production, read more about 
             :doc:`wsgi` and :doc:`/more/deploy`.

