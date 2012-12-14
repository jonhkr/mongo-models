from bson import json_util
from bson.objectid import ObjectId


class Field(object):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(dict(*args, **kwargs))


class Embed(Field):
    pass


class Document(object):

    def __init__(self):
        self.fields = {}
        self.embed_fields = []
        self.prepare_fields()

    def prepare_fields(self):
        for attr in dir(self):
            attrv = getattr(self, attr)
            if isinstance(attrv, Field):
                v = None
                if isinstance(attrv, Embed):
                    v = attrv.type()
                    self.embed_fields.append(attr)
                setattr(self, attr, v)
                self.fields[attr] = attrv

    def to_mongo(self):
        mongodoc = {}
        for field in self.fields.keys():
            mongodoc[field] = getattr(self, field)
            if field in self.embed_fields:
                mongodoc[field] = mongodoc[field].to_mongo()
        return mongodoc

    def from_mongo(self, data):
        if not '_id' in self.fields.keys() and '_id' in data.keys():
            self.fields['_id'] = Field()
        for f in self.fields.keys():
            obj = data[f]
            if f in self.embed_fields:
                obj = self.fields[f].type()
                obj.from_mongo(data[f])
            setattr(self, f, obj)

    def to_json(self):
        return json_util.dumps(self.to_mongo())

    def from_json(self, data):
        self.from_mongo(json_util.loads(data))

    def __setattr__(self, name, value):
        if hasattr(self, 'fields') and name in self.fields.keys():
            if not isinstance(value, self.fields[name].type):
                raise ValueError('Attribute %s expecting instance of %s, received %s' %
                                 (name, self.fields[name].type.__name__, type(value).__name__))
        super(Document, self).__setattr__(name, value)