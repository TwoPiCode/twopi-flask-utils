from flask import request
from marshmallow import Schema, fields
from webargs import fields as wfields
from webargs.flaskparser import parser

pagination_args = {
    'offset': wfields.Integer(missing=0),
    'limit': wfields.Integer(missing=20)
}

def paginated(basequery, schema_type, offset=None, limit=None):
    """
    Paginate a sqlalchemy query
    
    :param basequery: The base query to be iterated upon
    :param schema_type: The ``Marshmallow`` schema to dump data with
    :param offset: (Optional) The offset into the data. If omitted it will 
                  be read from the query string in the ``?offset=`` argument. If
                  not query string, defaults to 0.
    :param limit: (Optional) The maximum results per page. If omitted it will 
                  be read from the query string in the ``?limit=`` argument. If
                  not query string, defaults to 20.
    
    :returns: The page's data in a namedtuple form ``(data=, errors=)``
    """

    if offset is None or limit is None:
        args = parser.parse(pagination_args, request)
        if offset is None:
            offset = args['offset']

        if limit is None:
            limit = args['limit']

    data = {
        'offset': offset,
        'limit': limit,
        'items': basequery.limit(limit).offset(offset),
        'totalItems': basequery.count()
    }

    class _Pagination(Schema):
        offset = fields.Integer()
        limit = fields.Integer()
        totalItems = fields.Integer()
        items = fields.Nested(schema_type, many=True)

    return _Pagination().dump(data)


__all__ = ['paginated']
