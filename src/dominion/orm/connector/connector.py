'''
Contains everything needed for managing the connection to the DB.

Created on Nov 23, 2012

@author: Nathaniel
'''
from decorator import decorator
import mongoengine

DEFAULT_DB_NAME = 'DEBUG'

@decorator
def assure_connect(func, *args, **kwargs):
    '''
    This is a decorator for having functions connect to the DB if not connected.
    '''
    if not is_connected():
        connect(DEFAULT_DB_NAME)
    return func(*args, **kwargs)

def connect(dbname=DEFAULT_DB_NAME):
    '''
    Connects to the database with the specified name.
    '''
    connection = mongoengine.connect(dbname)
    return connection

def is_connected():
    '''
    Returns true if mongoengine is connected.
    '''
    return mongoengine.connection
