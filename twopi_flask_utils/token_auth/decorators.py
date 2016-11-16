from flask import g, request
from functools import wraps
import re

bearer_re = re.compile(r'Bearer (.+)')

def parse_auth_header(token_cls, auth_header=True, query_string=True, secret=None):
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
                    return "The provided token was invalid.", 401

                g.token = token
                g.raw_token = raw_token

            return f(*args, **kwargs)

        return wrapped
    return wrapper


def auth_required():
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if g.token is None:
                return "A valid token is required to access this resource", 401

            return f(*args, **kwargs)
        
        return wrapped
    return wrapper
