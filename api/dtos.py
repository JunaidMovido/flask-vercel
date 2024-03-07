from marshmallow import Schema, fields, ValidationError, validate

class WPACheckRequest(Schema):
    company = fields.Str(required=True)
    country = fields.Str(required=True, validate=validate.OneOf(['DE', 'AT', 'CH']))
    street = fields.Str(required=True)
    zip = fields.Str(required=True)
    email = fields.Email(required=True)