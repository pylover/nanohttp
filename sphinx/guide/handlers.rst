
http handlers
-------------

Available decorators are: ``action``, ``html``, ``text``, ``json``, ``xml``, 
``binary``.

Those decorators are useful to encapsulate response preparation such as 
setting ``Content-Type`` HTTP header.

Take a look at the code of the ``action`` decorator, all other decorators are 
derived from this:


.. code-block:: python

   def action(*args, verbs: Union[str, list, tuple]='any', encoding: str='utf-8',
              content_type: Union[str, None]=None,
              inner_decorator: Union[callable, None]=None,
              prevent_empty_form=None, prevent_form=None, **kwargs):
       ...



Other decorators are defined using ``functools.partial``:

.. code-block:: python

   html = functools.partial(action, content_type='text/html')
   text = functools.partial(action, content_type='text/plain')
   json = functools.partial(action, content_type='application/json', inner_decorator=jsonify)
   xml = functools.partial(action, content_type='application/xml')
   binary = functools.partial(action, content_type='application/octet-stream', encoding=None)

Of-course, you can set the response content type using:

.. code-block:: python

   context.response_content_type = 'application/pdf'

Of-course, you can define your very own decorator to make your code DRY:

.. code-block:: python

   import functools
   from nanohttp import action, RestController

   pdf = functools.partial(action, content_type='application/pdf')

   class MyController(RestController)

       @pdf
       def get(index):
           .......


