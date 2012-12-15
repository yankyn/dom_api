'''
This module contains everything to do with managing the rules of the game.

We use inheritance here for code readability purposses. DB wise this is not the best because
the DB should not be able to return the documents of the different types here in the same query.

Created on Dec 7, 2012

@author: Nathaniel
'''
from dominion.orm.utils.autosave import save, AutoSave
from dominion.orm.utils.consts import CARD_COLLECTION
from dominion.orm.utils.game_consts import MONEY, BUYS, ACTIONS, HAND_SIZE
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, ListField, ReferenceField, \
    DictField, BooleanField

class Rules(AutoSave, Document):
    '''
    A parent class for all documents. Should generally hold all data common to all rule-sets.
    '''
    
    meta = {'allow_inheritance': True}
    
    phase_order = ListField(StringField())
    money = IntField(default=MONEY)
    buys = IntField(default=BUYS)
    actions = IntField(default=ACTIONS)
    hand_size = IntField(default=HAND_SIZE)
    card_types = ListField(StringField())
    
    _is_constant = BooleanField(default=False)
    
    no_copy_fields = ['id', '_is_constant']
    
class GeneralRuleSet(Rules):
    '''
    A collection for all possible rule sets. 
    (Different expensions, or other rule variations we might want to try out)
    
    This colleciton holds most of the game-play related information.
    '''
    
    '''
    name is a key field, all specific rule sets know which general \
    rule set is their parent by using this.
    '''
    name = StringField() 
    number_of_piles = IntField()
    used_cards = ListField(ReferenceField(CARD_COLLECTION))
    starting_deck = ListField(ReferenceField(CARD_COLLECTION))
    
    _is_general = BooleanField(default=True)
    
    no_copy_fields = Rules.no_copy_fields + ['_is_general']
    
class SpecificRuleSet(GeneralRuleSet):
    '''
    A sub document for rule sets specific for the number of players.
    '''
    player_number = IntField()
    cards = DictField() # Cards to numbers
    
