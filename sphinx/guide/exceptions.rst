Exceptions
==========

In general, an exception breaks the normal flow of
execution and executes a pre-registered exception handler.
The details of how this is done depends on how the exception is implemented. [#f1]_

There is some exceptions based on `RFC7231 <https://tools.ietf.org/html/rfc7231>`_
and supported in nanohttp:

=====  ==============
Code   Exception Name
=====  ==============
301    HttpMovedPermanently
302    HttpFound
304    HttpNotModified
400    HttpBadRequest
401    HttpUnauthorized
403    HttpForbidden
404    HttpNotFound
405    HttpMethodNotAllowed
409    HttpConflict
410    HttpGone
412    HttpPreconditionFailed
500    HttpInternalServerError
=====  ==============

for using exceptions just raise it! like this:

..  code-block:: python

    from nanohttp import Controller, html, HttpNotFound

    class Root(Controller):

        @html
        def index(self, user_id: str):
            all_users = [12, 13, 14]
            if not user_id in all_users:
                raise HttpNotFound('User not found')
            return '<p>Yes is here</p>'

also you can define your own HTTP exception by using  ``nanohttp.exceptions.HttpStatus``.

.. rubric:: ---

.. [#f1] `wikipedia <https://en.wikipedia.org/wiki/Exception_handling>`_ with some modification.
