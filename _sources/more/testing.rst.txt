Testing
=======

Like any WSGI application, you can write tests in
`existing tools <http://wsgi.readthedocs.io/en/latest/testing.html>`_.

Here is an example with `webtest <https://docs.pylonsproject.org/projects/webtest/en/latest/>`_:

``my_app.py``

.. code-block:: python

   from nanohttp import Application, Controller, html, configure


   class RootController(Controller):

       @html
       def index(self):
           return '<h1>HelloWorld!</h1>'


   configure()
   app = Application(root=RootController())


``test.py``

.. code-block:: python

   import unittest
   from my_app import app
   from webtest import TestApp


   class SampleTestCase(unittest.TestCase):
       app = None

       @classmethod
       def setUpClass(cls):
           cls.app = TestApp(app)

       def test_unit_one(self):
           resp = self.app.get('/')
           self.assertEqual(resp.text, '<h1>HelloWorld!</h1>')


   if __name__ == '__main__':  # pragma: no cover
       unittest.main()
