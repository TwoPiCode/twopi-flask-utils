Token Auth
==========

Motivation
~~~~~~~~~~

Building applications that require authentication and protection is common
at TwoPi Code. 

We've found the most practical token exchange implementation exists with 2 
different kinds of tokens and the following authentication flow:


    1. A user performs a ``POST`` to a login endpoint ``/api/v1/login`` with 
       their credentials. 
    2. The API validates these credentials, and begins the token exchange process. 
       The API generates a **refresh token**, and stores it. This token must have 
       all the information required to generate a **shortlived token**. A 
       **shortlived token** is then generated. A possible response from this 
       endpoint could be:

       .. code-block:: json

            {
                "refreshToken": "abcdefg",
                "token": "shortlived-token-could-be-a-jwt"
            }

    3. The client stores both these tokens. (Possibly in ``localstorage``).
    4. Before every request, the client checks if their shortlived token has
       expired. If it hasn't expired, they can just send the shortlived token
       as usual. However, if it is expired, a renewal must occur.
    5. The client performs a ``POST`` to the renew endpoint, providing the 
        ``refresh token`` they recieved at login.
    6. The server checks if the refresh token is still valid (ie, hasn't been 
       revoked, or inactive for too long), and using this returns a new 
       **shortlived token**. A possible response from this endpoint could be:

        .. code-block:: json

            {
                "token": "shortlived-token-could-be-a-jwt"
            }

    7. The user stores the new token. If it was found that the **refresh token**
       had been revoked, then the user will be prompted to log back into the app.
    8. When the user wishes to log out, a ``POST`` request to a logout endpoint
       occurs, sending the user's shortlived token.
    9. The server revokes the shortlived token's associated refresh token, 
       thus, invalidating any further renewals.

There are 4 main advantages to using an authentication flow like this:

    1. Users never have to log in again as long as they stay active.
    2. Tokens are stateless (Unless you need to check for revocation on every 
       request, but this is still a very lightweight operation.)
    3. As long as shortlived tokens have a short enough expiry, a compromised 
       shortlived token can have little impact.
    4. Heavy token renewal/stateful operations can be minimised to happening 
       ONLY when the token has expired.


Thus, this package exposes helpers to assist in implementing such an authentication
workflow. It makes no assumptions about your refresh token objects. It does assume
that your prefered short lived token type is a JWT.

Usage
~~~~~

Within your project, create class for your short lived token. Within this class, 
we need to define a few things. Let's store a user_id, a list
of scopes, and the associated refresh token on the short lived token. We can use
a marshmallow schema for this:

.. literalinclude:: ../../../examples/token_auth/simple.py
   :language: python
   :lines: 2-4, 13-28


I used shortend names like ``rfid`` in the schema to cut down on bytes 
transfered with the token. JWT's are meant to be lightweight.

Finally, we need to define a way to load a ``ShortlivedToken`` from a refresh
token. We define the ``classmethod``, ``from_refresh_token`` to do this:

.. literalinclude:: ../../../examples/token_auth/simple.py
   :language: python
   :lines: 2-4, 13-39
   :emphasize-lines: 19-29


As mentioned above, we use information from the refresh token to build a 
ShortlivedToken. To complete the example, we'll add an in-memory refresh
token store and a basic implementation:

.. literalinclude:: ../../../examples/token_auth/simple.py
   :language: python
   :lines: 5-7,42-53


Finally, we will create a flask app and implement the 3 endpoints for 
authentication. ``/login``, ``/logout``, and ``/renew``. This is now the final
implementation:

.. literalinclude:: ../../../examples/token_auth/simple.py
   :language: python
   :emphasize-lines: 55-134


Using this example, you should be able to exchange credentials for a refresh token,
a shortlived token, and perform subsequent renewalls and revokations. 

In the above example, the functions :func:`.parse_auth_header` and 
:func:`.auth_required` are used on the protected endpoint and logout endpoint.


API
~~~

.. automodule:: twopi_flask_utils.token_auth
    :members:
