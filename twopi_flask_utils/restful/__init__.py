from flask import jsonify, request

def format_errors(*errors):
    return {
        '_errors': errors
    }

def format_error(error):
    return format_errors(error)


def output_json(data, code, headers=None):
    """
    
    .. code-block:: python
        
        api.representations['application/json'] = output_json
    
    Generates better formatted responses for RESTFul APIs. 

    If the restful resource responds with a string, with a non 200 error,
    the response will look like

    .. code-block:: json

        {
            "_errors": ["String the user responded with"]
        }

    Likewise, a string return value with a 200 response will look like:


    .. code-block:: json

        {
            "message": "String the user returned with."
        }

    
    If a Non-200 response occured, and flask-restful added it's own error 
    message in the "message" field of the response data, this data is moved into
    "_errors":


    .. code-block:: json

        {
            "_errors": ["You don't have the permission to access the requested resource..."]
        }


    All data is returned using flask's jsonify method. This means you can 
    use simplejson to return decimal objects from your flask restful resources.
    """

    if type(data) is str:
        # Handle view returning a string.
        message = data
        if code != 200:
            data = format_errors(message)
        else:
            data = {'message': message}

    elif code != 200 and type(data) is dict and 'message' in data:
        # Flask-Restful returns non-200 error messages to the user.
        # Let's show them.
        data = format_errors(data.get('message'))

    resp = jsonify(data)

    if code:
        resp.status_code = code

    resp.headers.extend(headers)
    return resp



class ExpectedJSONException(Exception):
    """
    Thrown when JSON was expected in a flask request but was not
    provided
    """
    pass

    @classmethod
    def handle(cls, exc):
        """
        A handler for this type of exception.

        Usage:

        .. code-block:: python
     
            app.errorhandler(ExpectedJSONException)(ExpectedJSONException.handle)


        """
        return jsonify(
            format_error('Resource expected a JSON payload to be provided.')
        ), 400


def get_and_expect_json():
    """
    Returns the ``flask.request.get_json()`, however if no JSON data was decoded,
    will raise a :class:`ExpectedJSONException`
    """

    data = request.get_json()
    if data is None:
        raise ExpectedJSONException()
    
    return data

