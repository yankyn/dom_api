'''
Created on Nov 23, 2012

@author: Nathaniel
'''
import mongoengine

def connect(dbname):
    connection = mongoengine.connect(dbname)
    return connection
