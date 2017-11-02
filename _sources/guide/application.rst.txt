Application
===========

Everything in nanohttp start from an application.
You should define your root controller in application.
for more information and samples see :doc:`wsgi`.


Life cycle
----------
.. image:: application-life-cycle.png
    :alt: nanohttp life cycle
    :target: https://www.websequencediagrams.com/?lz=dGl0bGUgbmFub2h0dHAKCkFwcC0-KkNvbnRleHQ6IG5ldwANBgAJCWVudGVyACIFLT5BcHA6IGJlZ2luIHJlcXVlc3QKbm90ZSByaWdodCBvZiAAHAVob29rAFIGAAkGYW5kbGUgdHJhaWxpbmcgc2xhc2gAFQtzcGxpdCBwYXRoAEcGbGVmAEIKU3BsaXR0aW5nIHRoZQAgBSBieQA9BiBgL2AKCmFsdCB0cnkKICAgIACBMAlyb2xsZXI6IGNhbGwAFQUACwoAEw5kaXNwYXRjaAAIHXNlcnZlAIFAB3IKZWxzZSBleGNlcHQAaworAIFeDAAXBmlvbgCBDAktPi0AgjYFAIIuB19lcnJvcgCBLgUAgicYZW5kAIMWBgCCZg9zcG9uc2UAglMjcHJvY2VzcyBjb29raWVzAIMFC2VuY29kZQBCCgCDUAtlbmQAPiYAhBQMeGl0CmRlc3Ryb3kAgmMFZXh0CgoKCgo&s=napkin

Hooks
-----

Hooks is part of your application life-cycle and calling when they are need.

A few hooks are available:

- ``app_init``: After application initialized.
- ``begin_request``: Before start to processing request.
- ``begin_response``: After processing request and preparing the response.
- ``end_response``: Response is ready to send to client.

..  code-block:: python

    from nanohttp import Application, Controller, context

    class JwtApplication(Application):
        token_key = 'HTTP_AUTHORIZATION'
        refresh_token_cookie_key = 'refresh-token'

        def begin_request(self):
            if self.token_key in context.environ:
                encoded_token = context.environ[self.token_key]
                try:
                    context.identity = JwtPrincipal.decode(encoded_token)
                except itsdangerous.SignatureExpired as ex:
                    refresh_token_encoded = context.cookies.get(self.refresh_token_cookie_key)
                    if refresh_token_encoded:
                        # Extracting session_id
                        session_id = ex.payload.get('sessionId')
                        if session_id:
                            context.identity = new_token = self.refresh_jwt_token(refresh_token_encoded, session_id)
                            if new_token:
                                context.response_headers.add_header('X-New-JWT-Token', new_token.encode().decode())

                except itsdangerous.BadData:
                    pass

            if not hasattr(context, 'identity'):
                context.identity = None

.. note:: [Pro-tip] in some cases, you can override ``Application._handle_exception`` to
          handle exception for all requests.
