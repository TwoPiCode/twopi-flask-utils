from functools import wraps
import re
import datetime
from flask import current_app, request, g


class TokenMixin(object):
    def get_scopes(self):
        """Returns a list of scope strings that are authorised for the token."""
        raise NotImplementedError()

    def has_scope(self, scope):
        return scope in self.get_scopes()

    def serialize(self):
        """Serialize the token into a string.

        Your token class should implement this.
        """
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, app, token_str):
        """Deserialize a token into a token object.

        Your token class should implement this."""
        raise NotImplementedError


class JWTFactory(object):
    def __init__(self, signing_secret, expiry):
        self._signing_secret = signing_secret
        self._expiry = expiry

    def __call__(self):
        import jwt

        _scopes = self.scopes
        _expiry = self._expiry
        _signing_secret = self._signing_secret

        class JSONWebToken(TokenMixin):
            def __init__(self, scopes=None):
                self.scopes = scopes

            def get_scopes(self):
                """Returns a list of scope strings that are authorised for the token."""
                return self.scopes

            def deserialize_data(self, data):
                raise NotImplementedError()

            def serialize_data(self):
                raise NotImplementedError()

            def serialize():
                payload = {
                    'scopes': _scopes,
                    'exp': datetime.datetime.utcnow() + _expiry,
                    'data': self.serialize()
                }

                return jwt.encode(payload, _signing_secret).decode('UTF-8')

            @classmethod
            def deserialize(Cls, app, token_str):
                """Converts a JWT payload into a"""
                try:
                    decoded = jwt.decode(token_str, self._signing_secret)
                except jwt.InvalidTokenError:
                    raise LookupError("The provided JWT payload was invalid.")

                token = Cls(scopes=decoded.get('scopes', []))
                token.deserialize(data=decoded.get('data', {}))
                return token


bearer_re = re.compile(r'Bearer (.+)')

class TokenAuth():
    def __init__(self, app, token_cls):
        self._token_cls = token_cls
        self._app = app
        app.token_auth = self

    def _inject_token(self, _request):
        token = self._parse_request(_request)
        if token is None:
            raise Exception("The provided token was invalid.")

        try:
            g.token = self._token_cls.deserialize(self._app, token)
        except LookupError as e:
            raise Exception("The provided token was invalid. {}".format(e))

        return token

    def _scopes_accepted(self, _request, scopes, orig, fargs, fkwargs):
        """Given a flask request and list of accepted scopes, perform auth 
        and access control."""
        try:
            self._inject_token(_request)
        except Exception as e:
            return str(e), 403

        allowed_scopes = g.token.get_scopes()
        for scope in scopes:
            if scope in allowed_scopes:
                return orig(*fargs, **fkwargs)

        return "The provided token does not have an accepted scope. It needs "\
               "one of [{}], but only has [{}]".format(
                ', '.join(scopes),
                ', '.join(allowed_scopes))

    def _scopes_required(self, _request, scopes, orig, fargs, fkwargs):
        """Given a flask request and list of required scopes, perform 
        authentication and access control."""
        try:
            self._inject_token(_request)
        except Exception as e:
            return str(e), 403

        allowed_scopes = g.token.get_scopes()
        for scope in scopes:
            if scope not in allowed_scopes:
                return "The provided token does not have the required scopes "\
                       "[{}]. It has [{}]".format(
                        ', '.join(scopes),
                        ', '.join(allowed_scopes)), 403

        return orig(*fargs, **fkwargs)

    def _parse_request(self, _request):
        """Extract a token from a passed flask request"""
        auth_header = _request.headers.get('Authorization', None)
        if auth_header is not None:
            # Loading from the Auth header. Expect `Bearer <token>` format.
            if len(auth_header) > 0:
                result = bearer_re.search(auth_header)
                if result is not None:
                    return result.group(1)
        else:
            # Attempt to load from GET params
            return _request.args.get('token')


def scopes_required(*scopes):
    def _inner(f):
        @wraps(f)
        def _wrapped(*args, **kwargs):
            return current_app.token_auth._scopes_required(request, scopes, f, args, kwargs)
        return _wrapped
    return _inner

def scopes_accepted(*scopes):
    def _inner(f):
        @wraps(f)
        def _wrapped(*args, **kwargs):
            return current_app.token_auth._scopes_required(request, scopes, f, args, kwargs)
        return _wrapped
    return _inner
