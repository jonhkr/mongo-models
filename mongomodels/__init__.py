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

    def is_empty(self, fv):
        if fv is None or fv is '':
            return True
        return False

    def append_error(self, field, error):
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(error)

    def validate_required(self, f, fv):
        if f in self.required_fields:
            if self.is_empty(fv):
                self.append_error(f, self.FIELD_REQUIRED_MESSAGE)

    def validate_with_validators(self, f, fv):
        if f in self.field_validators.keys():
            validators = self.field_validators[f]
            for validator in validators:
                valid = validator(fv)
                if not valid is True:
                    self.append_error(f, valid[1])

    def validate_type(self, v, f, fv):
        if not isinstance(fv, v.meta['type']) and fv:
            self.append_error(f, self.INVALID_FIELD_TYPE_MESSAGE
                              % v.meta['type'].__name__)

    def validate(self):
        self.errors = {}
        for f, v in self.fields.items():
            fv = getattr(self, f)
            self.validate_required(f, fv)
            self.validate_with_validators(f, fv)
            self.validate_type(v, f, fv)

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

__all__ = ['Document', 'Field', 'ValidationError']
