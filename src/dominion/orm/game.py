'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import DateTimeField, ListField, ReferenceField, \
    EmbeddedDocumentField, IntField, StringField, BooleanField
from utils.consts import *
from dominion.dominion_exceptions import FullGameException
import datetime


'''
    --- Colleciton --- 
'''
    
class GeneralRuleSet(Document):
    '''
    A collection for all possible rule sets. 
    (Different expensions, or other rule variations we might want to try out)
    
    This colleciton holds most of the game-play related information.
    '''
    
    name = StringField()
    number_of_piles = IntField()
    variations = ListField(EmbeddedDocumentField(SPEC_RULESET_COLLECTION))
    cards = ListField(ReferenceField(CARD_COLLECTION))
    games = ListField(ReferenceField(GAME_COLLECTION))
    
    def start_game(self, start_date):
        '''
        Creates a game and connects it to this ruleset.
        '''
        self.save()
        game = Game(start_date=start_date, ruleset=self)
        game.save()
        self.games.append(game)
        self.save()
        game.save()
        return game
    
    def player_num_ruleset(self, number):
        '''
        Get the specific ruleset for the given number of players.
        '''
        return GeneralRuleSet.get(id=self.id, variations__player_number=number).only('variations')
    
class SpecificRuleSet(EmbeddedDocument):
    '''
    A sub document for rule sets specific for the number of players.
    '''
    general_ruleset = ReferenceField(GENERAL_RULESET_COLLECTION)
    player_number = IntField()
    cards = ListField(EmbeddedDocumentField(CARD_PILE_DOC))
    
class Game(Document):
    '''
    An embedded document type for actual games.

    generally contains metadate + all information shared between all players.
    ''' 
    ruleset = ReferenceField(GENERAL_RULESET_COLLECTION)
    start_date = DateTimeField(default=datetime.datetime.now())
    end_date = DateTimeField()
    game_players = ListField(EmbeddedDocumentField(GAME_PlAYER_DOC))
    card_piles = ListField(EmbeddedDocumentField(CARD_PILE_DOC))
    trashed_cards = ListField(ReferenceField(CARD_COLLECTION))  
    draft_style = StringField()
    
    def can_add_players(self):
        '''
        Tests whether there are game variations with a number of players 
        greater than the current number of players
        '''
        return GeneralRuleSet.objects(id=self.ruleset.id,\
                                       variations__player_number__gt=len(self.game_players))
        
    def can_start(self):
        '''
        Checks whether there is a variation for the current number of players.
        '''
        return GeneralRuleSet.objects(id=self.ruleset.id, variations__player_number=len(self.game_players))
    
    def add_player(self, player):
        '''
        Adds a player to this game if possible. Else throws FullGameException.
        '''
        if not self.can_add_players():
            raise FullGameException(player=player, game=self)
        
        player.save()
        self.save()
        player.games.append(self)
        player.save()
        
        gameplayer = GamePlayer(player=player)
        self.game_players.append(gameplayer)
        self.save()
        
        return gameplayer
'''
    --- Embedded Documents ---
'''    
 
    
class CardPile(EmbeddedDocument):
    '''
    Piles of cards. Generally only used in Game.
    
    NOTE: may want to just use DictField instead. This exists only the reinforce the schema. Not very mongo.
    '''
    
    size = IntField()
    card = ReferenceField(CARD_COLLECTION)
            
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
    
    hand = ListField(EmbeddedDocumentField(HAND_CARD_DOC))
    played_actions = ListField(ReferenceField(CARD_COLLECTION))
    bought_cards = ListField(ReferenceField(CARD_COLLECTION))
    discarded_cards = ListField(ReferenceField(CARD_COLLECTION))
    trashed_cards = ListField(ReferenceField(CARD_COLLECTION))
    
class HandCard(EmbeddedDocument):    
    card = ReferenceField('Card')
    is_revealed = BooleanField(default=False)
    

            
            
