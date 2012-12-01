'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from mongoengine.fields import StringField, IntField, BooleanField
from mongoengine.document import Document
    
class Card(Document):
    
    name = StringField()
    cost = IntField()
    buys = IntField()
    actions = IntField()
    cards = IntField()
    money = IntField()
    victory = IntField()
    type = StringField()
    has_script = BooleanField()
    
    '''    
    I guess at some point we may want to add an order field in case some effects are affected by action number etc...
    '''
            
            
            
