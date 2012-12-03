from mongomodels import Document, ValidationError, Field as field
from bson.objectid import ObjectId

import re


def email_validator(email):
    reg = re.compile(r'\b[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b', re.IGNORECASE)
    return True if reg.match(email) else (False, 'Invalid email address')


class User(Document):

    id = field(type=ObjectId)
    firstname = field(type=basestring, required=True)
    lastname = field(type=basestring, required=True)
    email = field(type=basestring, validators=[email_validator])
    login = field(type=basestring, required=True)
    passwd = field(type=basestring, required=True)


class Transaction(Document):

    id = field(type=ObjectId)
    uid = field(type=ObjectId, required=True)
    description = field(type=basestring, required=True)
    category = field(type=basestring, required=True)


u = User()
u.id = ObjectId()
u.firstname = 'Joao'
u.lastname = 'Pereira'
u.email = 'joao@example.com'
u.login = 'jp'
u.passwd = 'passwd'

a = Transaction()
a.uid = u.id
a.description = 'Teste'
a.category = 'Teste'

try:
    print u.to_mongo()
except ValidationError as e:
    print e.errors

try:
    print a.to_mongo()
except ValidationError as e:
    print e.errors
