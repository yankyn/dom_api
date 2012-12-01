'''
This is a test suite for the "schema" part of the orm. We do not test advanced functionalities but rather
that our objects contain the desired fields.

NOTE: Add tests to this suite every time you write a functionality to test that the necessary objects work.

Created on Nov 23, 2012

@author: Nathaniel
'''
import datetime
from utils import dominion_fix #@UnusedImport

from dominion.orm import Player, GeneralRuleSet, Game, GamePlayer, SpecificRuleSet

def test_player(dominion_fix):
    '''
    Tests creating a player and saving it to the DB.
    '''
    player = Player(name='test_player')
    player.save()
    assert len(Player.objects(name='test_player')) == 1 #@UndefinedVariable
    
def test_ruleset_game(dominion_fix):
    '''
    Tests creating a game and a ruleset and connecting them together.
    '''
    date = datetime.datetime.now()
    ruleset = GeneralRuleSet(name='test_ruleset')
    ruleset.save()
    
    game = Game(start_date=date)
    game.save()
    ruleset.games.append(game)
    
    game.ruleset = ruleset
    game.save()
    
    assert game.ruleset.name == 'test_ruleset'
    assert len(ruleset.games) == 1
    assert len(Game.objects(start_date=date)) == 1 #@UndefinedVariable
    
def test_spec_ruleset(dominion_fix):
    '''
    Tests adding a variation to a ruleset and querrying by its number of players.
    '''
    ruleset = GeneralRuleSet(name='test_ruleset')
    ruleset.save()
    
    spec_ruleset = SpecificRuleSet(player_number=2)
    ruleset.variations.append(spec_ruleset)
    ruleset.save()
    
    assert len(GeneralRuleSet.objects(variations__player_number__gt=1)) > 0 #@UndefinedVariable
    
def test_game_player(dominion_fix):
    '''
    Tests creating games and connecting them to players.
    '''
    game = Game()
    game.save()
    player = Player(name='test_player')
    player.save()

    player.games.append(game)
    player.save()
    gameplayer = GamePlayer(player=player)
    game.game_players.append(gameplayer)
    game.save()

    assert len(Game.objects(game_players__player=player)) == 1 #@UndefinedVariable
    assert len(game.game_players) == 1
    assert len(Player.objects(games=game)) == 1 #@UndefinedVariable
    
    
       

