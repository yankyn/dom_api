'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.dominion_exceptions import GameFullException
from dominion.dominion_exceptions.exceptions import DominionException
from dominion.orm import Player, GeneralRuleSet, Game, GamePlayer, \
    SpecificRuleSet
from dominion.orm.rulesets import ConstantRules
from dominion.orm.utils.game_consts import COPPER, ESTATE, MONEY
from tests.orm.utils import hook
from utils import *
import datetime
import pytest

def test_create_game(dominion_fix, ruleset, ruleset_game):
    '''
    Tests GeneralRuleSet.star_game(self)
    '''
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
    ruleset.create_specific_ruleset(1)
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
    '''
    Tests Player.shuffle_deck. This is sort of statistical because the actual randomizer may return the same
    result 10 times, but thats 60 bit unlikely.
    '''
    player = full_ruleset_game_player
    player.deck = list(full_ruleset_game.get_starting_deck())
    
    decks = list()
    for i in range(10): #@UnusedVariable
        decks.append(copy_shuffled_deck(player))
        
    success = False
    for deck1 in decks:
        assert len(deck1) == 10
        for deck2 in decks:
            assert set(deck1) == set(deck2)
            if deck1 != deck2:
                success = True
                break
    assert success
    
def test_player_create_turn(full_ruleset_game_player):
    '''
    Tests that player turn creation works as expected
    '''
    cr = ConstantRules()
    player = full_ruleset_game_player
    player.create_turn(money=cr.money, buys=cr.buys, actions=cr.actions, phase=cr.phase_order[0])
    assert player.turns
    assert player.turns[0].money == MONEY
    
def test_player_init_deck_shuffle(full_ruleset_game_player, monkeypatch):
    '''
    Tests that shuffle_deck is called on player.set_deck
    '''
    player = full_ruleset_game_player
    hook(player, player.shuffle_deck, monkeypatch)
    assert not player.called_shuffle_deck
    player.set_deck([])
    assert player.called_shuffle_deck
    
def test_player_init_deck_init(full_ruleset_game_player):
    '''
    Tests that set_deck actually sets the deck
    '''
    player = full_ruleset_game_player
    player.set_deck([1, 2, 3])
    sortedlist = list(player.deck)
    sortedlist.sort()
    assert sortedlist == [1, 2, 3]
    
def test_player_shuffle_discard(full_ruleset_game_player, discard, monkeypatch):
    '''
    Tests shuffleing the discard pile back into the deck.
    '''
    player = full_ruleset_game_player
    player.discard_pile = discard
    hook(player, player.shuffle_deck, monkeypatch)
    assert not player.called_shuffle_deck
    player.shuffle_discard_pile()
    assert player.called_shuffle_deck
    sorted_deck = list(player.deck)
    sorted_deck.sort()
    discard.sort()
    assert sorted_deck == discard
    
def test_player_shuffle_discard_raises_exception(full_ruleset_game_player):
    '''
    Tests that trying to shuffle the discard pile into a non empty deck fails.
    '''
    player = full_ruleset_game_player
    player.deck = [1]
    player.discard_pile = [1]
    with pytest.raises(DominionException):
        player.shuffle_discard_pile()
    
    
def test_player_draw_cards(full_ruleset_game_player, deck, discard):
    '''
    Tests that drawing cards works as expected
    '''
    hand_size = 5
    
    player = full_ruleset_game_player
    player.set_deck(deck)
    player.discard_pile = discard
    
    player.draw_cards(hand_size)
    assert (len(player.hand) == hand_size) or (len(player.hand) < hand_size and not player.deck and not player.discard_pile)
    
    assert (len(player.deck) + len(player.discard_pile) == len(deck) + len(discard) - hand_size) \
        or (not player.deck and not player.discard_pile)
    
    
