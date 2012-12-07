'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.dominion_exceptions import FullGameException
from dominion.orm import Player, GeneralRuleSet, Game, GamePlayer, \
    SpecificRuleSet
from utils import dominion_fix, ruleset, ruleset_game #@UnusedImport
import datetime
import pytest

def test_create_game(dominion_fix, ruleset, ruleset_game):
    '''
    Tests GeneralRuleSet.star_game(self)
    '''
    date = datetime.datetime.now()
    
    assert Game.objects #@UndefinedVariable
    assert ruleset.games[0].ruleset == ruleset
    assert Game.objects(ruleset=ruleset) #@UndefinedVariable
    assert GeneralRuleSet.objects(games=ruleset_game) #@UndefinedVariable
    
def test_create_specific_ruleset(dominion_fix, ruleset):
    '''
    Tests GeneralRuleSet.create_specific_ruleset(self)
    '''
    spec = ruleset.create_specific_ruleset(player_number=0)
    
    assert ruleset.variations
    assert GeneralRuleSet.objects(variations=spec) #@UndefinedVariable
    assert spec.general_ruleset == ruleset
    assert SpecificRuleSet.objects(general_ruleset=ruleset) #@UndefinedVariable
    
def test_can_add_player(dominion_fix, ruleset, ruleset_game):
    '''
    Tests Game.can_add_players()
    '''
    spec_ruleset = ruleset.create_specific_ruleset(0)
    assert not ruleset_game.can_add_players()
    
    spec_ruleset.player_number = 1
    assert ruleset_game.can_add_players()
    
    spec_ruleset.player_number = 2
    assert ruleset_game.can_add_players()
    
def test_add_player_exception(dominion_fix, ruleset, ruleset_game):
    '''
    Tests that adding a player to a game that cannot add players raises an exception.
    '''
    with pytest.raises(FullGameException):
        ruleset_game.add_player(Player())
        
def test_add_and_get_player(dominion_fix, ruleset, ruleset_game):
    '''
    Tests adding and getting players from a game.
    '''
    spec = ruleset.create_specific_ruleset(1)
    game = ruleset_game
    player = Player(name = 'test_player_1')
    
    game.add_player(player)
    assert game.game_players
    assert game._get_player(player)
    assert game._get_player(player).player == player
    assert player.games
    assert player.games[0] == game
    game.add_player(player) # Should not raise an exception
    with pytest.raises(FullGameException):
        game.add_player(Player(name = 'test_player_2'))
        
def test_remove_player(dominion_fix, ruleset, ruleset_game):
    '''
    Tests removing existing and non-existing players.
    '''
    ruleset.create_specific_ruleset(1)
    player = Player()
    game = ruleset_game
    game.remove_player(player)
    game.add_player(player)
    game.remove_player(player)
    
    assert not game.game_players
    assert not player.games

def test_remove_player_corrupt(dominion_fix, ruleset, ruleset_game):
    '''
    Test removing players when the game or the player documents are corrupted.
    '''
    ruleset.create_specific_ruleset(2)
    player = Player()
    game = ruleset_game
    
    # Corrupted player
    player.games.append(game)
    player.save()
    game.save()
    assert player.games
    
    game.remove_player(player)
    assert not game.game_players
    assert not player.games
    
    # Corrupted game
    game.game_players[player._id] = GamePlayer(player = player)
    assert game.game_players
    assert game.game_players[player._id].player == player
    
    game.remove_player(player)
    assert not game.game_players
    assert not player.games

def test_can_start(dominion_fix, ruleset, ruleset_game):

