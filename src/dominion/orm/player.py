'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from mongoengine.fields import StringField, ListField, ReferenceField
from dominion.orm.utils.autosave import AutoSaveDocument
from dominion.orm.orm_base import OrmBase
    
class Player(AutoSaveDocument, OrmBase):
    
    name = StringField()
    password_hash = StringField()
    games = ListField(ReferenceField('Game'))
    
    def __repr__(self):
        return 'Player %s' % self.name

    
