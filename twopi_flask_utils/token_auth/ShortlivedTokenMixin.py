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
    class TokenSchema(Schema):
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
        raise NotImplemented("You must implement generate. Simply invoke Cls() "
                             "and instantiate it using information from the "
                             "refresh token")

    @classmethod
    def load(Cls, token_string, secret=None, issuer=None, audience=None):
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
        self.issued_at = datetime.datetime.now(pytz.UTC)
        payload, err = self.TokenSchema().dump(self)

        if secret is None:
            secret = current_app.config['SECRET_KEY']

        return jwt.encode(payload, secret).decode('UTF-8')


    def __repr__(self):
        return "<ShortlivedToken expiry={}>".format(self.expiry)
