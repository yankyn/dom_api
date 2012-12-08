'''
Created on Dec 7, 2012

@author: Nathaniel
'''
from dominion.orm.game import Game
from dominion.orm.utils.autosave import AutoSaveDocument, save
from dominion.orm.utils.consts import SPEC_RULESET_COLLECTION, CARD_COLLECTION, \
    GAME_COLLECTION, GENERAL_RULESET_COLLECTION
from dominion.orm.utils.dev_utils import untested, undocumented
from dominion.orm.utils.game_consts import MONEY, BUYS, ACTIONS, HAND_SIZE, \
    INACTIVE, ACTION, BUY, CLEANUP
from mongoengine.fields import StringField, IntField, ListField, ReferenceField, \
    DictField, EmbeddedDocumentField
    
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
    const_rules = EmbeddedDocumentField()
    
    @undocumented
    @untested
    def __init__(self, *args, **kwargs): 
        if not ConstantRules.objects:
            raise Exception('Default constant rules are not configured!')
        self.const_rules = ConstantRules.objects[0]
        super(GeneralRuleSet, self).__init__(self, *args, **kwargs)
        
    @save
    def create_game(self):
        '''
        Creates a game and connects it to this ruleset.
        '''
        game = Game(ruleset=self)
        game.save()
        self.games.append(game)
        return game

    @save
    def create_specific_ruleset(self, player_number, cards=None):
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
    
class ConstantRules(AutoSaveDocument):
    '''
    A document to hold all rules that are currently not changeabe between rule-sets.
    
    Currently this holds quite a lot.
    '''
    
    phase_order = ListField(StringField)
    money = IntField(default=MONEY)
    buys = IntField(default=BUYS)
    actions = IntField(default=ACTIONS)
    hand_size = IntField(default=HAND_SIZE)
    
    @untested
    @undocumented
    def __init__(self):
        if ConstantRules.objects:
            raise Exception('Constant rules document already exists, please check your actions again')
        self.phase_order = [INACTIVE, ACTION, BUY, CLEANUP]
        super(ConstantRules, self).__init__(self)
