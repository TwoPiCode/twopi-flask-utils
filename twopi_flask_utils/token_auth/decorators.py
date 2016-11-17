from flask import g, request, jsonify
from functools import wraps
from twopi_flask_utils.restful import format_error
import re

bearer_re = re.compile(r'Bearer (.+)')

def parse_auth_header(token_cls, auth_header=True, query_string=True, secret=None):
    """
    A decorator to extract a token from either the ``Authorization`` header OR
    the query string parameter ``?token=``.

    :param token_cls: An instance of :class:`ShortlivedTokenMixin` OR a class which
                      implements the classmethod ``load(token_string, secret)``. 
                      An instance will be available on `g.token`.
    :param auth_header:  (optional, ``bool``) Extract the token from the auth 
                          header (Default: ``True``)
    :param query_string: (optional, ``bool``) Extract the token from the query 
                          string (Default: ``True``)
    :param secret: (optional) A secret to pass to ``token_cls.load(raw, secret)``

    Any wrapped function will be able to access both ``g.token`` and ``g.raw_token``
    to read the ``token_cls`` instance and raw token string respectively.

    Authorization header expects tokens in the format of ``Bearer <token string>``

    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            g.token = None
            g.raw_token = None
            raw_token = None

            if query_string and 'token' in request.args:
                # Try fetch the token from the QS
                raw_token = request.args['token']

            if auth_header and 'Authorization' in request.headers:
                token_res = bearer_re.match(request.headers['Authorization'])
                if token_res is not None:
                    raw_token = token_res.group(1)

            if raw_token is not None:
                token = token_cls.load(raw_token, secret)
                if token is None:
                    return jsonify(format_error("The provided token was invalid.")), 401

                g.token = token
                g.raw_token = raw_token

            return f(*args, **kwargs)

        return wrapped
    return wrapper


def auth_required():
    """
    Force authentication on an endpoint. Checks if ``g.token`` is not None, 
    and returns a ``401`` if it is.

    Example:

    .. code::

        @app.route('/auth-required')
        @auth_required()
        def my_endpoint():
            return "Hello World"

    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if g.token is None:
                return jsonify(
                    format_error("A valid token is required to access this resource")), 401

            return f(*args, **kwargs)
        
        return wrapped
    return wrapper
