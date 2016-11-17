from webargs.flaskparser import FlaskParser
from webargs.core import ValidationError
from flask import jsonify


class BetterFlaskParser(FlaskParser):
    """
    A Flask-Restful compatible parser for WebArgs.
    """

    def handle_error(self, error):
        """
        Don't raise a ``HTTPException`` via ``abort``. Instead we will throw the 
        ``ValidationError`` and handle it with our flask Exception handler.

        This allows a common code path for both Flask-Restful AND standard 
        Flask Views.
        """
        raise error


parser = BetterFlaskParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs

def handle_validation_error(exc):
    """
    When using :class:`BetterFlaskParser`, if an exception occurs, it will throw the 
    original ``ValidationError``. This circumvents the capture inside Flask-Restful
    (if it is being used at all). 

    Instead of capturing all 422 ``HTTPExceptions``, you register this error 
    handler with ``ValidationError``:

    .. code-block:: python
    
        app.errorhandler(ValidationError)(handle_validation_error)


    This function will produce a jsonified response with the field errors from
    the ValidationError.

    .. warning::

        This handler is incompatible with the standard ``FlaskParser``, since
        it throws ``HTTPExceptions`` (via ``abort``). Registering this handler with 
        ``errorhandler(422)`` will not work.

    """

    assert(type(exc) == ValidationError)
    return jsonify(exc.messages), exc.status_code


__all__ = ['BetterFlaskParser', 'parser', 'use_args', 'use_kwargs',
           'handle_validation_error']

