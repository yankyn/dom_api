'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.dominion_exceptions import GameFullException
from dominion.dominion_exceptions.exceptions import GameNotReadyException, \
    DominionException
from dominion.orm.card import Card
from dominion.orm.rulesets import SpecificRuleSet, ConstantRules
from dominion.orm.utils.autosave import AutoSaveDocument, save
from dominion.orm.utils.consts import GENERAL_RULESET_COLLECTION, \
    SPEC_RULESET_COLLECTION, GAME_PlAYER_DOC, CARD_COLLECTION, PLAYER_COLLECTION, \
    TURN_DOC, HAND_CARD_DOC
from dominion.orm.utils.dev_utils import untested, undocumented
from dominion.orm.utils.game_consts import INACTIVE, HAND_SIZE
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import DateTimeField, ListField, ReferenceField, \
    EmbeddedDocumentField, IntField, StringField, BooleanField, MapField, DictField
import datetime
import random


class Game(AutoSaveDocument):
    '''
    An embedded document type for actual games.

    generally contains metadate + all information shared between all players.
    ''' 
    ruleset = ReferenceField(GENERAL_RULESET_COLLECTION)
    spec_rulset = ReferenceField(SPEC_RULESET_COLLECTION)
    created_date = DateTimeField(default=datetime.datetime.now())
    start_date = DateTimeField()
    end_date = DateTimeField()
    
    '''
    We may want to make adding players and removing them asymchronous.
    so we'll need another dictionary of "removed players"
    '''
    game_players = MapField(EmbeddedDocumentField(GAME_PlAYER_DOC))
    
    trashed_cards = ListField(ReferenceField(CARD_COLLECTION))  
    
    def can_add_players(self):
        '''
        Tests whether there are game variations with a number of players 
        greater than the current number of players
        '''
        return SpecificRuleSet.objects(general_ruleset=self.ruleset, player_number__gt=len(self.game_players)) #@UndefinedVariable
        
    def can_start(self):
        '''
        Checks whether there is a variation for the current number of players.
        '''
        return SpecificRuleSet.objects(general_ruleset=self.ruleset, player_number=len(self.game_players)) #@UndefinedVariable
    
    @save
    def add_player(self, player):
        '''
        Adds a player to this game if possible. Else throws GameFullException.
        '''
        if player._id in self.game_players:
            return
        if not self.can_add_players():
            raise GameFullException(player=player, game=self)
        player.games.append(self)
        self.game_players[player._id] = GamePlayer(player=player, game=self)
    
    @save
    def remove_player(self, player):
        '''
        Removes a player from the game if possible.
        '''
        if player._id in self.game_players:
            self.game_players.pop(player._id)
        if self in player.games:
            player.games.remove(self)
     
    def _get_player(self, player):
        '''
        Returns the GamePlayer mapped to the received player.
        '''
        return self.game_players[player._id]
     
    @untested   
    def start(self):
        '''
        Initialized the game for all players.
        '''
        if not self.can_start(self):
            raise GameNotReadyException(self)
        
        spec_ruleset = SpecificRuleSet.objects(ruleset=self.ruleset, player_number=len(self.game_players)) #@UndefinedVariable
        self.spec_rulset = spec_ruleset
        for player in self.game_players:
            player.start_game(self)
    
    @untested
    @undocumented
    def get_starting_deck(self):
        return self.ruleset.starting_deck
    
    @untested
    @undocumented    
    def start_turn(self, player):
        money = self.ruleset.const_rules.money
        actions = self.ruleset.const_rules.actions
        buys = self.ruleset.const_rules.buys
        hand_size = self.ruleset.const_rules.hand_size
        
        if not self.phase_order:
            raise DominionException('No phase order found in constant configuration!')
        phase = self.ruleset.const_rules.phase_order[0]
        
        player.craete_turn(money=money, actions=actions, buys=buys, hand_sizes=hand_size, phase=phase)
        
class GamePlayer(EmbeddedDocument):
    '''
    The actual isntance of the player in the game.
    '''
    
    player = ReferenceField(PLAYER_COLLECTION)
    deck = ListField(ReferenceField(CARD_COLLECTION))
    discard_pile = ListField(ReferenceField(CARD_COLLECTION))
    center = ListField(ReferenceField(CARD_COLLECTION))
    turns = ListField(EmbeddedDocumentField(TURN_DOC))
    
    @untested
    @undocumented
    def start_game(self, game):
        self.deck = game.get_starting_deck()
        self.shuffle_deck()
        self.turns.append(Turn())
    
    @untested
    @undocumented
    def shuffle_deck(self):    
        self.deck = random.shuffle(self.deck)
        
    @untested
    @undocumented
    def create_turn(self, money, actions, buys, hand_sizes, phase):
        turn = Turn(money=money, actions=actions, buys=buys, phase=phase)
        self.turns.append(turn)
        
class Turn(EmbeddedDocument):
    
    start_date = DateTimeField(default=datetime.datetime.now())
    end_date = DateTimeField()
    
    money = IntField()
    actions = IntField()
    buys = IntField()
    phase = StringField()
    is_current = BooleanField()
    
    hand = DictField() # Cards to numbers
    played_actions = ListField(ReferenceField(CARD_COLLECTION))
    bought_cards = ListField(ReferenceField(CARD_COLLECTION))
    discarded_cards = ListField(ReferenceField(CARD_COLLECTION))
    trashed_cards = ListField(ReferenceField(CARD_COLLECTION))
    
class HandCard(EmbeddedDocument):    
    card = ReferenceField(HAND_CARD_DOC)
    is_revealed = BooleanField(default=False)
    

            
            
