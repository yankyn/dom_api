'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.orm.utils.autosave import AutoSave
from dominion.orm.utils.dev_utils import untested
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, BooleanField
    
class Card(AutoSave, Document):
    '''
    A reference document for a card. This should contain only one isntance of every card in the game.
    '''
    
    name = StringField()
    cost = IntField()
    buys = IntField(default=0)
    actions = IntField(default=0)
    cards = IntField(default=0)
    money = IntField(default=0)
    victory = IntField(default=0)
    type = StringField()
    has_script = BooleanField(default=False)
    
    function = None
    
    def __repr__(self):
        '''
        To String.
        '''
        return '<Card %s>' % self.name
    
    @untested
    def playout(self):
        '''
        Plays out the actual contens of the card.
        '''
        pass
    
    '''    
    I guess at some point we may want to add an order field in case some effects are affected by action number etc...
    '''
    
    
                
            
            
