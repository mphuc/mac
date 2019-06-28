import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Updatewallet(Document):
    __collection__ = 'updatewallet'

    structure = {
        'user_id': unicode,
        'uid': unicode,
        'bitcoin': unicode,
        'ethereum':  unicode,
        'status': int,
        'date_added' : datetime.datetime,
        'code': unicode
    }
    use_dot_notation = True

db.register([Updatewallet])