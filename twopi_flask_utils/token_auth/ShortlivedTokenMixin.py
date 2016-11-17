import pytz
import datetime
import jwt
from marshmallow import fields, Schema, post_dump
from flask import current_app
import logging

log = logging.getLogger(__name__)

EPOCH_DT = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)

class UnixTimestamp(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return None

        return int((value - EPOCH_DT).total_seconds())

    def _deserialize(self, value, attr, data):
        if value is None:
            return None

        return datetime.datetime.fromtimestamp(value, pytz.UTC)


class ShortlivedTokenMixin(object):
    """
    A base class for implementing a short-lived token using JWTs

    :param expiry: ``datetime``: The expiry of this token
    :param issuer: ``string``
    :param subject: ``string``
    :param audience: ``string``
    :param not_before: ``datetime``: A datetime of when the token becomes 
                                     valid for use
    :param issued_at: ``datetime``: When the token was issued. This value is 
                                    overwritten during ``dump()``
    """
    class TokenSchema(Schema):
        """
        The schema to use to serialize/de-serialize JWT's with.
        """
        SKIPPABLE = ['exp', 'iss', 'sub', 'aud', 'nbf', 'iat']

        exp = UnixTimestamp(attribute='expiry')
        iss = fields.String(attribute='issuer')
        sub = fields.String(attribute='subject')
        aud = fields.String(attribute='audience')
        nbf = UnixTimestamp(attribute='not_before')
        iat = UnixTimestamp(attribute='issued_at')

        @post_dump
        def remove_skippable(self, data):
            return {key: value for key, value in data.items() 
                    if key not in self.SKIPPABLE or value is not None}

    def __init__(self, expiry=None, issuer=None, subject=None, audience=None, 
                 not_before=None, issued_at=None):
        self.expiry = expiry
        self.issuer = issuer
        self.subject = subject
        self.audience = audience
        self.not_before = not_before
        self.issued_at = issued_at

    @classmethod
    def generate(Cls, refresh_token):
        log.warning("{}.generate() is deprecated. Please use "
                    "{}.from_refresh_token()".format(Cls.__name__, Cls.__name__))
        return Cls.from_refresh_token(refresh_token)

    @classmethod
    def from_refresh_token(Cls, refresh_token):
        """
        Given a refresh token, return an instance of ShortLivedTokenMixin 
        configured using information from ``refresh_token``.

        :param refresh_token: A refresh token instance.
        :returns: A new ShortLivedToken instance.

        .. warning::
            
            You must implement this method



        """
        raise NotImplemented("You must implement from_refresh_token. Invoke {}() "
                             "and instantiate it using information from the "
                             "refresh token".format(Cls.__name__))

    @classmethod
    def load(Cls, token_string, secret=None, issuer=None, audience=None):
        """
        Load from a JWT (``token_string``)

        :param token_string: The raw string to load from
        :param secret: The secret that the JWT was signed with to check validity. 
                       If this is omitted, the secret will be sourced 
                       from ``current_app.config['SECRET_KEY']``
        :param issuer: The issuer the JWT decode should expect
        :param audience: The audience the JWT decode should expect
        :returns: A de-serialized ShortLivedToken instance.
        """

        if secret is None:
            secret = current_app.config['SECRET_KEY']

        try:
            payload = jwt.decode(token_string, secret, issuer=issuer, audience=audience)
        except (jwt.exceptions.InvalidTokenError) as e:
            log.info("The provided token has expired or was malformed. {}".format(e))
            return None

        deserialized, errs = Cls.TokenSchema().load(payload)
        if errs:
            # Malformed token?
            log.info("Malformed token was provided, error during de-serialisation.")
            return None
        try:
            return Cls(**deserialized)
        except TypeError as e:
            log.info("Malformed token was provided, error during instantiation.")
            return None

    def dump(self, secret=None):
        """
        Dump the token into a stringified JWT.

        :param secret: The secret to sign the JWT with. If this is omitted, the 
                       secret will be sourced from ``current_app.config['SECRET_KEY']``

        :returns: The stringified JWT.
        """

        self.issued_at = datetime.datetime.now(pytz.UTC)
        payload, err = self.TokenSchema().dump(self)

        if secret is None:
            secret = current_app.config['SECRET_KEY']

        return jwt.encode(payload, secret).decode('UTF-8')


    def __repr__(self):
        return "<ShortlivedToken expiry={}>".format(self.expiry)
