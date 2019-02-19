from flask import current_app, Flask, request, abort, jsonify, g
from twopi_flask_utils.token_auth import (
    ShortlivedTokenMixin, parse_auth_header, auth_required)
from marshmallow import fields
import uuid
import random
import string
import pytz
import datetime
import logging

log = logging.getLogger(__name__)


class ShortlivedToken(ShortlivedTokenMixin):

    class TokenSchema(ShortlivedTokenMixin.TokenSchema):
        rfid = fields.String(attribute='refresh_token_id')
        user_id = fields.String(attribute='user_id')
        scopes = fields.List(fields.String(), attribute='scopes')

    def __init__(self, refresh_token_id, user_id, scopes, *args, **kwargs):
        super(ShortlivedToken, self).__init__(*args, **kwargs)

        self.refresh_token_id = refresh_token_id
        self.user_id = user_id
        self.scopes = scopes

    @classmethod
    def from_refresh_token(Cls, refresh_token):
        # Fetch the token expiry from the application configuration
        shortlived_expiry = current_app.config['SHORT_LIVED_TOKEN_EXPIRY']

        return Cls(
            refresh_token_id=refresh_token.id,
            user_id=refresh_token.user_id,
            scopes=refresh_token.scopes,
            expiry=datetime.datetime.now(pytz.UTC) + shortlived_expiry,
        )


random_alpha = string.digits + string.ascii_letters

class RefreshToken():
    def __init__(self, user_id, scopes):
        self.id = uuid.uuid4().hex
        self.user_id = user_id
        self.scopes = scopes
        self.token = ''.join(random.choice(random_alpha) for _ in range(80))


# Store the granted refresh tokens in memory.
refresh_tokens = []

app = Flask(__name__)
app.config.update({
    'SHORT_LIVED_TOKEN_EXPIRY': datetime.timedelta(hours=1),
    'SECRET_KEY': 'supersecret'
})


@app.route('/login', methods=['POST'])
def login():
    # Check if the credentials were correct
    if request.form.get('username') != 'test' or \
            request.form.get('password') != 'test':
        abort(401)

    # Create a new refresh token
    refresh_token = RefreshToken(user_id=request.form.get('username'),
                                 scopes=['360noscope'])

    # Persist the refresh token so we can renew it later
    refresh_tokens.append(refresh_token)

    shortlived_token = ShortlivedToken.from_refresh_token(refresh_token)
    log.info("Generated token with payload: {}".format(shortlived_token))

    return jsonify({
        'token': shortlived_token.dump(),
        'refreshToken': refresh_token.token
    })


@app.route('/logout', methods=['POST'])
@parse_auth_header(ShortlivedToken)
@auth_required()
def logout():

    # Find the associated refresh token
    for refresh_token in refresh_tokens:
        if refresh_token.id == g.token.refresh_token_id:
            break # Found the associated token

    else: # nobreak
        # Couldn't find the token. Maybe it has been revoked.
        abort(401)

    # Remove the refresh token from the store. It has now been revoked.
    refresh_tokens.remove(refresh_token)

    return jsonify({
        'status': 'success'
    })


@app.route('/renew', methods=['POST'])
def renew():
    token_string = request.form.get('refreshToken')

    # Find the refresh token in the store
    for refresh_token in refresh_tokens:
        if refresh_token.token == token_string:
            break # Found the token that we need.

    else: # nobreak
        # Couldn't find the token. Oops
        abort(401)

    # Make a new shortlived token
    shortlived_token = ShortlivedToken.from_refresh_token(refresh_token)
    log.info("Generated token with payload: {}".format(shortlived_token))

    # Respond to the client with the new token
    return jsonify({
        'token': shortlived_token.dump()
    })


@app.route('/protected', methods=['POST'])
@parse_auth_header(ShortlivedToken)
@auth_required()
def protected():
    return "Welcome, {}".format(g.token.user_id)


if __name__ == '__main__':
    app.run(debug=True, port=5005)
