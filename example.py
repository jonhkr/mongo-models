from mongomodels import Document, ValidationError, Field as field
from bson.objectid import ObjectId

import re


def email_validator(email):
    reg = re.compile(r'\b[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b', re.IGNORECASE)
    return True if reg.match(email) else (False, 'Invalid email address')


class User(Document):

    __collection__ = 'user'

    firstname = field(required=True)
    lastname = field(required=True)
    email = field(validators=[email_validator])
    login = field(required=True)
    passwd = field(required=True)


class Transaction(Document):

    uid = field(required=True)
    description = field(required=True)
    category = field(required=True)


u = User()
u.id = ObjectId()
u.firstname = 'Joao'
u.lastname = 'Pereira'
u.email = 'joao@example.com'
u.login = 'jp'
u.passwd = 't'

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
