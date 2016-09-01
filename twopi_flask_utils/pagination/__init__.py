from flask import request
from marshmallow import Schema, fields
from webargs import fields as wfields
from webargs.flaskparser import parser

pagination_args = {
    'offset': wfields.Integer(missing=0),
    'limit': wfields.Integer(missing=20)
}

def paginated(basequery, schema_type, offset=None, limit=None):
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