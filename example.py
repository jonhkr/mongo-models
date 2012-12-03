from mongomodels import Document, ValidationError, Field as field

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