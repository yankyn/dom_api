'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.dominion_exceptions import FullGameException
from dominion.orm.utils.autosave import AutoSaveDocument, save
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import DateTimeField, ListField, ReferenceField, \
    EmbeddedDocumentField, IntField, StringField, BooleanField, MapField, DictField
from utils.consts import *
import datetime
from dominion.orm.utils.dev_utils import untested

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
    
    @save
    def create_game(self):
        '''
        Creates a game and connects it to this ruleset.
        '''
        game = Game(ruleset=self)
        game.save()
        self.games.append(game)
        return game

    #Untested    
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
    draft_style = StringField()
    
    def can_add_players(self):
        '''
        Tests whether there are game variations with a number of players 
        greater than the current number of players
        '''
        return SpecificRuleSet.objects(general_ruleset=self.ruleset, player_number__gt=len(self.game_players))
        
    def can_start(self):
        '''
        Checks whether there is a variation for the current number of players.
        '''
        return SpecificRuleSet.objects(ruleset=self.ruleset, player_number=len(self.game_players))
    
    @save
    def add_player(self, player):
        '''
        Adds a player to this game if possible. Else throws FullGameException.
        '''
        if player._id in self.game_players:
            return
        if not self.can_add_players():
            raise FullGameException(player=player, game=self)
        player.games.append(self)
        self.game_players[player._id] = GamePlayer(player=player)
    
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
        if not self.can_start(self):
            raise Exception('Cannot start game!')
        
        spec_ruleset = SpecificRuleSet.objects(ruleset=self.ruleset, player_number=len(self.game_players))
        self.spec_rulset = spec_ruleset
        for player in self.game_players:
            player.create_game(self)
        
class GamePlayer(EmbeddedDocument):
    '''
    The actual isntance of the player in the game.
    '''
    
    player = ReferenceField(PLAYER_COLLECTION)
    deck = ListField(ReferenceField(CARD_COLLECTION))
    discard_pile = ListField(ReferenceField(CARD_COLLECTION))
    center = ListField(ReferenceField(CARD_COLLECTION))
    turns = ListField(EmbeddedDocumentField(TURN_DOC))
    
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
    

            
            
