'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.dominion_exceptions import GameFullException
from dominion.orm import Player, GeneralRuleSet, Game, GamePlayer, \
    SpecificRuleSet
from dominion.orm.utils.game_consts import COPPER, ESTATE
from utils import dominion_fix, ruleset, ruleset_game, full_ruleset #@UnusedImport
from utils import full_ruleset_game, full_ruleset_game_player #@UnusedImport
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
    with pytest.raises(GameFullException):
        ruleset_game.add_player(Player())
        
def test_add_and_get_player(dominion_fix, ruleset, ruleset_game):
    '''
    Tests adding and getting players from a game.
    '''
    spec = ruleset.create_specific_ruleset(1)
    game = ruleset_game
    player = Player(name='test_player_1')
    
    game.add_player(player)
    assert game.game_players
    assert game._get_player(player)
    assert game._get_player(player).player == player
    assert player.games
    assert player.games[0] == game
    game.add_player(player) # Should not raise an exception
    with pytest.raises(GameFullException):
        game.add_player(Player(name='test_player_2'))
        
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
    game.game_players[player._id] = GamePlayer(player=player)
    assert game.game_players
    assert game.game_players[player._id].player == player
    
    game.remove_player(player)
    assert not game.game_players
    assert not player.games

def test_can_start(dominion_fix, ruleset, ruleset_game):
    '''
    Tests Game.can_start.
    '''
    sr = ruleset.create_specific_ruleset(1)
    player = Player()
    game = ruleset_game
    
    assert not game.can_start()
    game.add_player(player)
    assert game.can_start()
    sr.player_number = 2
    assert not game.can_start()
    sr.player_number = 0
    assert not game.can_start()
    
def test_starting_deck(full_ruleset, full_ruleset_game):
    '''
    Tests starting deck creation.
    '''
    assert len(full_ruleset.starting_deck) == 10
    assert full_ruleset_game.ruleset == full_ruleset
    assert len(full_ruleset_game.get_starting_deck()) == 10
    for card in full_ruleset_game.get_starting_deck():
        assert (card.name == COPPER or card.name == ESTATE)
    
def copy_shuffled_deck(player):
    '''
    Shuffles the playe's deck and returns a copy of the old deck.
    '''
    deck = list(player.deck)
    player.shuffle_deck()
    print player.deck
    return deck
    
def test_player_shuffle_deck(full_ruleset_game, full_ruleset_game_player):
    player = full_ruleset_game_player
    player.deck = list(full_ruleset_game.get_starting_deck())
    
    decks = list()
    for i in range(10): #@UnusedVariable
        decks.append(copy_shuffled_deck(player))
    success = False
    for deck1 in decks:
        for deck2 in decks:
            if deck1 != deck2:
                success = True
                break
    assert success
    
    
        

