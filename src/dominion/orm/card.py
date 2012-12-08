'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from mongoengine.fields import StringField, IntField, BooleanField
from dominion.orm.utils.autosave import AutoSaveDocument
    
class Card(AutoSaveDocument):
    
    meta = {'allow_inheritance': True}
    
    name = StringField()
    cost = IntField()
    buys = IntField(default=0)
    actions = IntField(default=0)
    cards = IntField(default=0)
    money = IntField(default=0)
    victory = IntField(default=0)
    type = StringField()
    has_script = BooleanField(default=False)
    
    '''    
    I guess at some point we may want to add an order field in case some effects are affected by action number etc...
    '''
    
                
            
            
