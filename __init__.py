

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

    def validate(self):
        for f, v in self.fields.items():
            field = getattr(self, f)
            if f in self.required_fields:
                if self.is_empty(field):
                    self.append_error(f, self.FIELD_REQUIRED_MESSAGE)
            if f in self.field_validators.keys():
                validators = self.field_validators[f]
                for validator in validators:
                    valid = validator(field)
                    if not valid is True:
                        self.append_error(f, valid[1])
            if not isinstance(field, v.meta['type']) and field:
                self.append_error(f, self.INVALID_FIELD_TYPE_MESSAGE \
                    % v.meta['type'].__name__)
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

print a.to_mongo()