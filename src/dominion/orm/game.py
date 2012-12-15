'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.dominion_exceptions import GameFullException
from dominion.dominion_exceptions.exceptions import GameNotReadyException, \
    DominionException
from dominion.orm.rulesets import SpecificRuleSet
from dominion.orm.utils.autosave import AutoSave, save
from dominion.orm.utils.consts import GENERAL_RULESET_COLLECTION, \
    GAME_PlAYER_DOC, CARD_COLLECTION, PLAYER_COLLECTION, TURN_DOC
from dominion.orm.utils.dev_utils import untested
from dominion.orm.utils.game_consts import ACTION, BUY
from mongoengine.document import EmbeddedDocument, Document
from mongoengine.fields import DateTimeField, ListField, ReferenceField, \
    EmbeddedDocumentField, IntField, StringField, MapField
import datetime
import random


class Game(AutoSave, Document):
    '''
    An embedded document type for actual games.

    generally contains metadate + all information shared between all players.
    ''' 
    ruleset = ReferenceField(GENERAL_RULESET_COLLECTION)
    created_date = DateTimeField(default=datetime.datetime.now())
    start_date = DateTimeField()
    end_date = DateTimeField()
    
    '''
    We may want to make adding players and removing them asymchronous.
    so we'll need another dictionary of "removed players"
    '''
    game_players = MapField(EmbeddedDocumentField(GAME_PlAYER_DOC))
    player_order = ListField(ReferenceField(PLAYER_COLLECTION))
    
    trashed_cards = ListField(ReferenceField(CARD_COLLECTION))  
    
    def can_add_players(self):
        '''
        Tests whether there are game variations with a number of players 
        greater than the current number of players
        '''
        return SpecificRuleSet.objects(name=self.ruleset.name, player_number__gt=len(self.game_players)) #@UndefinedVariable
        
    def can_start(self):
        '''
        Checks whether there is a variation for the current number of players.
        '''
        return SpecificRuleSet.objects(name=self.ruleset.name, player_number=len(self.game_players)) #@UndefinedVariable
    
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
        self.player_order.append(player)
        
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
    
    def start(self):
        '''
        Initialized the game for all players.
        '''
        if not self.can_start():
            raise GameNotReadyException(self)
        
        self.ruleset = SpecificRuleSet.objects(name=self.ruleset.name, player_number=len(self.game_players))[0] #@UndefinedVariable
        
        for player_id in self.game_players:
            player = self.game_players[player_id] #@UndefinedVariable
            player.set_deck(self.ruleset.starting_deck)
            player.draw_cards(self.ruleset.hand_size)
    
    def get_starting_deck(self):
        '''
        Returns the ruleset's starting deck.
        '''
        return self.ruleset.starting_deck
    
    def start_turn(self, player):
        '''
        Initializes a turn for the given player.
        '''
        money = self.ruleset.money
        actions = self.ruleset.actions
        buys = self.ruleset.buys
        
        if not self.ruleset.phase_order:
            raise DominionException('No phase order found in constant configuration!')
        phase = self.ruleset.phase_order[0]
        
        if player._id not in self.game_players:
            raise DominionException('Player not registered to game!')
        game_player = self.game_players[player._id]
        
        return game_player.create_turn(money=money, actions=actions, buys=buys, phase=phase)

    def get_next_player(self):
        '''
        Returns the next player to play.
        '''
        next_player = self.player_order.pop(0)
        self.player_order.append(next_player)
        return next_player
        
        
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
    
    def set_deck(self, deck):
        '''
        Initializes the player's deck and shuffles it.
        '''
        self.deck = list(deck)
        self.shuffle_deck()
    
    def shuffle_discard_pile(self):
        '''
        Shuffles the discard pile back into the deck. Assumes the deck is empty.
        '''
        if self.deck:
            raise DominionException('Cannot shuffle discard pile into non-empty deck!')
        
        new_deck = list(self.discard_pile)
        self.discard_pile = []
        self.set_deck(new_deck)
       
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
    
    @untested
    def get_current_turn(self):
        '''
        Get the current turn.
        '''
        return self.turns[-1]
    
    @untested
    def change_current_turn_fields(self, turn , money, actions, buys):
        '''
        Sets the current turns values according to the provided ones.
        '''
        turn = self.get_current_turn()
        turn.money += money
        turn.actions += actions
        turn.buys += buys
     
    @untested   
    def use_card(self, card):
        '''
        Does all generic actions required to play any card.
        '''
        if card.type == ACTION:
            self._use_action_card(card)
        self.hand[card] -= 1
        self.center.append(card)
        
    @untested
    def _use_action_card(self, card):
        '''
        Does all generic actions required to play any action card.
        '''
        if card.type == ACTION:
            '''
            For monitoring purposes we may want to know which actions were played in a turn.
            And in what order.
            '''
            turn = self.get_current_turn()
            turn.played_actions.append(card)
        else:
            raise DominionException('Not an action card! %s' % str(card))
        
    @untested
    def play_action(self, card):
        '''
        Plays the basic parts of the card according to its description. 
        All complex parts of the card must be handled by the controller because they may require
        access to player choices.
        '''
        
        phase = self.get_current_turn().phase
        
        '''
        We make sure that the card can indeed be played.
        '''
        if card.type != ACTION:
            raise DominionException('Cannot play non-action card %s' % str(card)) 
        if phase != BUY:
            raise DominionException('Cannot play action on phase %s' % str(phase)) 
        if card not in self.hand:
            raise DominionException('Player does not have card %s in hand!' % str(card))
        
        self.change_current_turn_fields(card.money, card.actions, card.buys)
        
        # Reminder to self.
        print 'You have not yet implemented the actual card playing part in the controller!!!!!'
    
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
    
    played_actions = ListField(ReferenceField(CARD_COLLECTION))
    bought_cards = ListField(ReferenceField(CARD_COLLECTION))
    discarded_cards = ListField(ReferenceField(CARD_COLLECTION))
    trashed_cards = ListField(ReferenceField(CARD_COLLECTION))
    

            
            
