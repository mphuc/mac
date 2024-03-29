import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class History(Document):
    __collection__ = 'history'

    structure = {
        'uid':  unicode,
        'user_id': unicode,
        'username': unicode,
        'detail':  unicode,
        'amount': float,
        'amount_sub' :  unicode,
        'amount_add' :  unicode,
        'amount_rest' : unicode,
        'type':  unicode,
        'wallet': unicode,
        'txtid':  unicode,
        'rate': unicode,
        'date_added' : datetime.datetime,
        'status' : int,
        'address' : unicode,
        'id_withdraw' : unicode
    }
    use_dot_notation = True

db.register([History])