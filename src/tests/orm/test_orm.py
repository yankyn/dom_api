'''
This is a test suite for the "schema" part of the orm. We do not test advanced functionalities but rather
that our objects contain the desired fields.

NOTE: Add tests to this suite every time you write a functionality to test that the necessary objects work.

Created on Nov 23, 2012

@author: Nathaniel
'''
import datetime
from utils import dominion_fix, ruleset #@UnusedImport

from dominion.orm import Player, GeneralRuleSet, Game, GamePlayer, SpecificRuleSet

def test_player(dominion_fix):
    '''
    Tests creating a player and saving it to the DB.
    '''
    Player(name='test_player')
    assert Player.objects(name='test_player') #@UndefinedVariable
    
def test_ruleset_game(dominion_fix, ruleset):
    '''
    Tests creating a game and a ruleset and connecting them together.
    '''
    date = datetime.datetime.now()
    game = Game(start_date=date)
    ruleset.games.append(game)
    
    game.ruleset = ruleset
    
    assert game.ruleset.name == 'test_ruleset'
    assert ruleset.games
    assert Game.objects(start_date=date) #@UndefinedVariable
    
def test_spec_ruleset(dominion_fix, ruleset):
    '''
    Tests adding a variation to a ruleset and querrying by its number of players.
    '''
    spec_ruleset = SpecificRuleSet(player_number=2)
    ruleset.variations.append(spec_ruleset)
    
    assert SpecificRuleSet.objects(player_number__gt=1)#@UndefinedVariable
    assert ruleset.variations
    
def test_game_player(dominion_fix):
    '''
    Tests creating games and connecting them to players.
    '''
    game = Game()
    player = Player(name='test_player')

    player.games.append(game)
    player.save()
    gameplayer = GamePlayer(player=player)
    game.game_players[str(player.id)] = gameplayer
    game.save()

    assert game.game_players
    assert game.game_players[str(player.id)].player == player
    assert Player.objects(games=game) #@UndefinedVariable
    
    
       

