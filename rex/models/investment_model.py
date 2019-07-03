import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Investment(Document):
    __collection__ = 'investment'

    structure = {
        'uid' : unicode,
        'user_id': unicode,
        'username' : unicode,
        'package' : float,
        'status' : int,
        'date_added' : datetime.datetime,
        'date_finish' : datetime.datetime,
        'amount_frofit' : float,
        'date_profit' : datetime.datetime,
        'precent_profit' : float,
        'precent_profit_next_day' : float,
        'day_number' : float,
        'day_number_profit' : float,
        'amount_currency' : float,
        'currency' : unicode,
        'invoid_id' : unicode
    }
    default_values = {
        'date_added': datetime.datetime.utcnow()
        }
    use_dot_notation = True

db.register([Investment])