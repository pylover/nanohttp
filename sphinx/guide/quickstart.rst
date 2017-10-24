Quickstart
==========

Here is a sample for running your application with zero configuration.


``demo.py``

..  code-block:: python

    from nanohttp import Controller, RestController, context, html, json, HttpFound


    class TipsControllers(RestController):
        @json
        def get(self, tip_id: int = None):
            if tip_id is None:
                return [dict(id=i, title="Tip %s" % i) for i in range(1, 4)]
            else:
                return dict(
                    id=tip_id,
                    title="Tip %s" % tip_id
                )

        @json
        def post(self, tip_id: int = None):
            tip_title = context.form.get('title')
            print(tip_id, tip_title)

            # Updating the tips title
            # TipStore.get(tip_id).update(tip_title)
            raise HttpFound('/tips/')


    class Root(Controller):
        tips = TipsControllers()

        @html
        def index(self):
            yield """
            <html><head><title>nanohttp Demo</title></head><body>
            <form method="POST" action="/tips/2">
                <input type="text" name="title" />
                <input type="submit" value="Update" />
            </form>
            </body></html>
            """

Now running ``demo.py`` with nanohttp CLI command:

..  code-block:: bash

    $ nanohttp demo

Or through the python:

..  code-block:: python

    from nanohttp import quickstart, configure

    configure()
    quickstart(Root())



.. note:: ``nanohttp`` CLI command and ``quickstart`` automatically will set your
          root controller to :doc:`application`.

.. seealso:: If your application is ready to production, read more about :doc:`wsgi` and :doc:`/more/deploy`.
