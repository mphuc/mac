import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Invoice(Document):
    __collection__ = 'invoice'

    structure = {
        'uid' : unicode,
        'user_id' : unicode,
        'username' : unicode,
        'amount' : float,
        'invoid_id' : unicode,
        'txt' : unicode,
        'callback' : unicode,
        'wallet' : unicode,
        'confirmations' : int,
        'currency' : unicode,
        'status': int,
        'amount_usd' : float,
        'amount_receve' : float,
        'date_added' : datetime.datetime,
    }
    default_values = {
        'confirmations' : 0
        }
    use_dot_notation = True

db.register([Invoice])