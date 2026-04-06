from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from models import User, FinancialRecord, UserStatus, RoleType

ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
    
    role = fields.String(validate=validate.OneOf([r.value for r in RoleType]))
    status = fields.String(validate=validate.OneOf([s.value for s in UserStatus]))

class FinancialRecordSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FinancialRecord
        load_instance = True
    
    type = fields.String(required=True, validate=validate.OneOf(['income', 'expense']))
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    category = fields.String(required=True, validate=validate.Length(min=1))

user_schema = UserSchema()
users_schema = UserSchema(many=True)
financial_record_schema = FinancialRecordSchema()
financial_records_schema = FinancialRecordSchema(many=True)
