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
    
    def get_starting_deck(self):
        '''
        Returns the ruleset's starting deck.
        '''
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
    hand = ListField(ReferenceField(CARD_COLLECTION))
    revealed_cards = ListField(ReferenceField(CARD_COLLECTION))
    
    turns = ListField(EmbeddedDocumentField(TURN_DOC))
    
#    @untested
#    def _validate_card_list(self, cardlist):
#        '''
#        Validates that a list of cards is a list of cards
#        '''
#        for card in cardlist:
#            assert isinstance(card, Card)
#    
#    @untested
#    def validate(self):
#        '''
#        Validates that the player's state is valid.
#        '''
#        self._validate_card_list(self.deck)
#        self._validate_card_list(self.discard_pile)
#        self._validate_card_list(self.center)
#        
#        for card in self.hand:
#            assert isinstance(card, HandCard)
#            assert isinstance(self.hand[card], int)
        
    
    def set_deck(self, deck):
        '''
        Initializes the player's deck and shuffles it.
        '''
        self.deck = list(deck)
        self.shuffle_deck()
    
    @untested
    def _draw_from_deck(self, card_number):
        '''
        Draws the specified number of cards from the deck. 
        Returns the number of cards failed o draw due to the deck not having enough cards.
        '''
        overflow = 0 if len(self.deck) >= card_number else card_number - len(self.deck)
        deck_draw = card_number - overflow
        
        self.hand.extend(self.deck[-1 * deck_draw:])
        self.deck = self.deck[:-1 * deck_draw]
        
        return overflow
    
    def shuffle_discard_pile(self):
        '''
        Shuffles the discard pile back into the deck. Assumes the deck is empty.
        '''
        if self.deck:
            raise DominionException('Cannot shuffle discard pile into non-empty deck!')
        
        new_deck = list(self.discard_pile)
        self.discard_pile = []
        self.set_deck(new_deck)
       
    @untested
    def draw_cards(self, card_number):
        '''
        Removes @card_number cards from the player's deck and appends them to his hand.
        '''
        overflow = self._draw_from_deck(card_number)
        if overflow:
            self.shuffle_discard_pile()
            self._draw_from_deck(overflow)
            
        
    def shuffle_deck(self):    
        '''
        Shuffles the player's deck.
        '''
        random.shuffle(self.deck)
        
    def create_turn(self, money, actions, buys, phase):
        '''
        Starts a turn with the given starting parameters.
        '''
        turn = Turn(money=money, actions=actions, buys=buys, phase=phase)
        self.turns.append(turn)
        return turn
        
class Turn(EmbeddedDocument):
    '''
    A player's turn.
    '''
    
    start_date = DateTimeField(default=datetime.datetime.now())
    end_date = DateTimeField()
    
    money = IntField()
    actions = IntField()
    buys = IntField()
    phase = StringField()
    is_current = BooleanField()
    
    played_actions = ListField(ReferenceField(CARD_COLLECTION))
    bought_cards = ListField(ReferenceField(CARD_COLLECTION))
    discarded_cards = ListField(ReferenceField(CARD_COLLECTION))
    trashed_cards = ListField(ReferenceField(CARD_COLLECTION))
    

            
            
