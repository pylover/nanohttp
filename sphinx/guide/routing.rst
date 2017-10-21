Routing
=======
nanohttp is using object-dispatching style to route the application.
it can help you to have a pythonic, beautiful, meaningful
structure with the best performance.

.. _routing-controller:

Controller
----------
The requested path will be split-ed by ``/`` and python's ``getattr`` will be used on the ``Root`` controller
recursively to find specific callable to handle request.

..  code-block:: python

    from nanohttp import Controller, html

    class ChildController(Controller):

        @html
        def index(self):
            return '<h1>This is child controller</h1>'

        @html
        def name(self):
            return '<h1>children controller</h1>'

    class Root(Controller):
        children = ChildController()

        @html
        def index(self):
            return '<h1>i am root</h1>'

Final path can be like:

.. code-block:: text

    /                   -> Root.index()
    /children           -> Root.children.index()
    /children/name      -> Root.children.name()


.. _routing-rest_controller:

Trailing slashes
~~~~~~~~~~~~~~~~

If the ``Controller.__remove_trailing_slash__`` is ``True``, then all trailing slashes are ignored.

..  code-block:: python

    def test_trailing_slash(self):
        self.assert_get('/users/10/jobs/', expected_response='User: 10\nAttr: jobs\n')

Rest Controller
---------------
For using nanohttp with `RESTful <https://en.wikipedia.org/wiki/Representational_state_transfer>`_ rules
we have a ``RestController``, it's behavior same as basic :ref:`routing-controller`
but dispatcher tries to dispatch request using HTTP method(verb) at first.

..  code-block:: python

    from nanohttp import RestController, html

    class Root(RestController):

        @html
        def say_hello(self):
            return '<h1>Hello!</h1>'

        @html
        def get(self, some_id: int):
            return '<h1>You called GET Method. (some_id=%s)</h1>' % some_id

        @html
        def delete(self):
            return '<h1>You called DELETE Method</h1>'

        @html
        def post(self):
            return '<h1>You called POST Method</h1>'

        @html
        def patch(self):
            return '<h1>You called PATCH Method</h1>'
