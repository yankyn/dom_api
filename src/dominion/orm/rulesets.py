'''
Created on Dec 7, 2012

@author: Nathaniel
'''
from dominion.dominion_exceptions.exceptions import DominionException
from dominion.orm.utils.autosave import AutoSaveDocument, save
from dominion.orm.utils.consts import SPEC_RULESET_COLLECTION, CARD_COLLECTION, \
    GAME_COLLECTION, GENERAL_RULESET_COLLECTION, CONSTANT_RULES_COLLECITON
from dominion.orm.utils.dev_utils import untested, undocumented
from dominion.orm.utils.game_consts import MONEY, BUYS, ACTIONS, HAND_SIZE, \
    INACTIVE, ACTION, BUY, CLEANUP, TREASURE, CURSE, VICTORY, ATTACK, REACTION
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, ListField, ReferenceField, \
    DictField
    
class GeneralRuleSet(AutoSaveDocument):
    '''
    A collection for all possible rule sets. 
    (Different expensions, or other rule variations we might want to try out)
    
    This colleciton holds most of the game-play related information.
    '''
    
    name = StringField()
    number_of_piles = IntField()
    variations = ListField(ReferenceField(SPEC_RULESET_COLLECTION))
    cards = ListField(ReferenceField(CARD_COLLECTION))
    games = ListField(ReferenceField(GAME_COLLECTION))
    starting_deck = ListField(ReferenceField(CARD_COLLECTION))
    const_rules = ReferenceField(CONSTANT_RULES_COLLECITON) #@UndefinedVariable
    
    def __init__(self, *args, **kwargs): 
        '''
        We default the constant rules to the (should be) only document in the collection.
        '''
        if not ConstantRules.objects: #@UndefinedVariable
            raise DominionException('Default constant rules are not configured!')
        super(GeneralRuleSet, self).__init__(*args, **kwargs)
        self.const_rules = ConstantRules.objects[0]
        
    @save
    def create_game(self):
        from dominion.orm.game import Game
        '''
        Creates a game and connects it to this ruleset.
        '''
        game = Game(ruleset=self)
        game.save()
        self.games.append(game)
        return game

    @save
    def create_specific_ruleset(self, player_number, cards=None):
        '''
        Creates a specific rule set for this rule set with the given number of players and card set.
        '''
        spec = SpecificRuleSet(general_ruleset=self, player_number=player_number, cards=cards)
        self.variations.append(spec)
        return spec
    
class SpecificRuleSet(AutoSaveDocument):
    '''
    A sub document for rule sets specific for the number of players.
    '''
    general_ruleset = ReferenceField(GENERAL_RULESET_COLLECTION)
    player_number = IntField()
    cards = DictField() # Cards to numbers
    
class ConstantRules(Document):
    '''
    A document to hold all rules that are currently not changeabe between rule-sets.
    '''
    
    phase_order = ListField(StringField())
    money = IntField(default=MONEY)
    buys = IntField(default=BUYS)
    actions = IntField(default=ACTIONS)
    hand_size = IntField(default=HAND_SIZE)
    card_types = ListField(StringField())
    
    def validate(self):
        '''
        We want to validate that there is always only one document here. Otherwise the data should go inside
        the general rule sets.
        '''
        
        if ConstantRules.objects:
            raise DominionException('Constant rules document already exists, please check your actions again')
        super(ConstantRules, self).validate()
    
    def __init__(self, *args, **kwargs):
        '''
        cTor
        '''
        super(ConstantRules, self).__init__(*args, **kwargs)
        self.phase_order = [INACTIVE, ACTION, BUY, CLEANUP]
        self.card_types = [TREASURE, ACTION, CURSE, VICTORY, ATTACK, REACTION]
