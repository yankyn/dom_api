'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.orm.orm_base import OrmBase
from dominion.orm.utils.autosave import AutoSave
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, ReferenceField
    
class Player(AutoSave, OrmBase, Document):
    '''
    "Meta" player. This contains everything not game related about a user.
    '''
    
    name = StringField()
    salt = StringField()
    password_hash = StringField()
    games = ListField(ReferenceField('Game'))
    
    def __repr__(self):
        return 'Player %s' % self.name

    
