from mongomodels import Document, Field as field, Embed as embed
from bson.objectid import ObjectId

class User(Document):

    firstname = field(type=basestring)
    lastname = field(type=basestring)
    email = field(type=basestring)
    login = field(type=basestring)
    passwd = field(type=basestring)


class Transaction(Document):

    uid = field(type=ObjectId)
    description = field(type=basestring)
    category = field(type=basestring)
    embed = embed(type=User)
    

a = User()

b = Transaction()

print b.to_mongo()