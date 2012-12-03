from bson import json_util

class Field:
    def __init__(self, *args, **kwargs):
        self.meta = dict(*args, **kwargs)


class ValidationError(Exception):
    def __init__(self, errors):
        Exception.__init__(self, errors)

        self.errors = errors


class Document(object):
    FIELD_REQUIRED_MESSAGE = 'Field required'
    INVALID_FIELD_TYPE_MESSAGE = 'Invalid field type, should be %s'

    def __init__(self):
        self.errors = {}
        self.fields = {}
        self.required_fields = []
        self.field_validators = {}
        
        self.prepare_fields()

    def prepare_fields(self):
        for attr in dir(self):
            attrv = getattr(self, attr)
            if isinstance(attrv, Field):
                self.fields[attr] = attrv
                if 'required' in attrv.meta and attrv.meta['required']:
                    self.required_fields.append(attr)
                if 'validators' in attrv.meta:
                    self.field_validators[attr] = attrv.meta['validators']
                setattr(self, attr, None)

    def is_empty(self, field):
        if field is None or field is '':
            return True
        return False

    def append_error(self, field, error):
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(error)

    def validate_required(self, f):
        if f in self.required_fields:
            if self.is_empty(field):
                self.append_error(f, self.FIELD_REQUIRED_MESSAGE)

    def validate_with_validators(self, f):
        if f in self.field_validators.keys():
            validators = self.field_validators[f]
            for validator in validators:
                valid = validator(field)
                if not valid is True:
                    self.append_error(f, valid[1])

    def validate_type(self, field, v):
        if not isinstance(field, v.meta['type']) and field:
            self.append_error(f, self.INVALID_FIELD_TYPE_MESSAGE
                              % v.meta['type'].__name__)

    def validate(self):
        for f, v in self.fields.items():
            self.validate_required(f)
            self.validate_with_validators(f)
            self.validate_type(getattr(self, f), v)

        if self.errors:
            raise ValidationError(self.errors)

    def to_mongo(self):
        self.validate()
        mongodoc = {}
        for field in self.fields.keys():
            mongodoc[field] = getattr(self, field)
        return mongodoc

    def from_mongo(self, data):
        for f in self.fields.keys():
            setattr(self, f, data[f])

    def to_json(self):
        return json_util.dumps(self.to_mongo())

    def from_json(self, data):
        self.from_mongo(json_util.loads(data))

field = Field


class Transaction(Document):

    description = field(type=str, required=True)
    category = field(type=str, required=True)


a = Transaction()

a.from_mongo({
    'description': 'teste',
    'category': 'cat'
})

try:
    a.validate()
except ValidationError as e:
    print e.errors

print a.to_json()