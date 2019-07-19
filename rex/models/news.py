import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'ad'


class New(Document):
    __collection__ = 'notification'

    structure = {
        'content':  unicode,
        'date_added' : datetime.datetime,
        'status': int,
        'title' : unicode,
        'thumb' : unicode
    }
    use_dot_notation = True

db.register([New])