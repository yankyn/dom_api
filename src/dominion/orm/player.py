'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.orm.orm_base import OrmBase
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, ReferenceField
    
class Player(Document, OrmBase):
    
    name = StringField()
    password_hash = StringField()
    games = ListField(ReferenceField('Game'))
    
    def __repr__(self):
        return 'Player %s' % self.name

    
