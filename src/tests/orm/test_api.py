'''
Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.dominion_exceptions import GameFullException
from dominion.dominion_exceptions.exceptions import DominionException, \
    GameNotReadyException
from dominion.orm import GamePlayer, SpecificRuleSet
from dominion.orm.utils.game_consts import MONEY, ACTION, CLEANUP
from utils import *
import pytest

def test_create_game(dominion_fix, ruleset, ruleset_game):
    '''
    Tests GeneralRuleSet.star_game(self)
    '''
    assert Game.objects #@UndefinedVariable
    assert Game.objects(ruleset=ruleset) #@UndefinedVariable
    
def test_create_specific_ruleset(dominion_fix, ruleset):
    '''
    Tests GeneralRuleSet.create_specific_ruleset(self)
    '''
    spec = create_specific_rule_set(parent=ruleset, player_number=0)
    
    assert spec.name == ruleset.name
    assert SpecificRuleSet.objects(name=ruleset.name) #@UndefinedVariable
    
def test_can_add_player(dominion_fix, ruleset, ruleset_game):
    '''
    Tests Game.can_add_players()
    '''
    spec_ruleset = create_specific_rule_set(parent=ruleset, player_number=0)
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
        ruleset_game.add_player(create_player())
        
def test_add_and_get_player(dominion_fix, ruleset, ruleset_game):
    '''
    Tests adding and getting players from a game.
    '''
    create_specific_rule_set(parent=ruleset, player_number=1)
    game = ruleset_game
    player = create_player(name='test_player_1')
    
    game.add_player(player)
    assert game.game_players
    assert game._get_player(player)
    assert game._get_player(player).player == player
    assert player.games
    assert player.games[0] == game
    game.add_player(player) # Should not raise an exception
    with pytest.raises(GameFullException):
        game.add_player(create_player(name='test_player_2'))
        
def test_remove_player(dominion_fix, ruleset, ruleset_game):
    '''
    Tests removing existing and non-existing players.
    '''
    create_specific_rule_set(parent=ruleset, player_number=1)
    player = create_player()
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
    create_specific_rule_set(parent=ruleset, player_number=2)
    player = create_player()
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
    sr = create_specific_rule_set(parent=ruleset, player_number=1)
    player = create_player()
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
    cr = Rules.objects(_is_constant=True)[0]
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
    assert (len(player.hand) == hand_size) or (len(player.hand) < hand_size \
                                               and not player.deck and not player.discard_pile)
    
    assert (len(player.deck) + len(player.discard_pile) == len(deck) + len(discard) - hand_size) \
        or (not player.deck and not player.discard_pile)
        
def test_draw_from_deck(full_ruleset_game_player, deck):
    '''
    Tests actually drawing the correct number of cards from the deck.
    '''
    hand_size = 5
    player = full_ruleset_game_player
    player.set_deck(deck)
    
    overflow = player._draw_from_deck(5)
    
    assert (len(player.hand) == hand_size - overflow)
    assert overflow == 0 or overflow == hand_size - len(deck)
    
def test_get_next_player(full_ruleset_game):
    '''
    Tests the cyclic get next player method.
    '''
    playernum = 3
    
    game = full_ruleset_game
    players = [create_player() for i in range(playernum)]
    game.player_order = players
    
    for i in range(100):
        assert game.get_next_player() == players[i % playernum]
        
def test_start_turn(full_ruleset_game, full_ruleset_game_player):
    '''
    Tests game.start_turn(player)
    '''
    game_player = full_ruleset_game_player
    player = game_player.player
    game = full_ruleset_game
    
    turn = game.start_turn(player)
    
    assert turn.money == game.ruleset.money
    assert turn.actions == game.ruleset.actions
    assert turn.buys == game.ruleset.buys
    assert turn.phase == game.ruleset.phase_order[0]
    
def test_start_game_no_player(full_ruleset_game):
    '''
    Tests that starting a turn with a non-mapped player raises the proper exception.
    '''
    with pytest.raises(DominionException):
        full_ruleset_game.start_turn(create_player())
        
def test_start_game_not_ready(full_ruleset_game, full_ruleset_game_player):
    '''
    Test starting a game that does not have enough players.
    '''
    game = full_ruleset_game
    with pytest.raises(GameNotReadyException):
        game.start()
        
def test_start_game(full_ruleset_game, full_ruleset_game_player, monkeypatch):
    '''
    Tests initializing all players in the game.
    '''
    game = full_ruleset_game
    player = full_ruleset_game_player
    game.add_player(create_player())
    hook(player, player.set_deck, monkeypatch)
    assert not player.deck
    assert not player.called_set_deck
    assert not player.hand
    game.start()
    full_card_list = (player.deck + player.hand)
    full_card_list.sort()
    
    game_starting_deck = list(game.ruleset.starting_deck)
    game_starting_deck.sort()
    
    assert full_card_list == game_starting_deck
    assert player.called_set_deck
    assert len(player.hand) == 5
    assert len(player.deck) == 5
    
def test_get_current_turn(full_ruleset_game_player):
    '''
    Tests that getting the latest turn works correctly.
    '''
    player = full_ruleset_game_player
    assert not player.get_current_turn()
    player.create_turn(money=0, buys=0, actions=0, phase=ACTION)
    assert player.get_current_turn()
    player.create_turn(money=1, buys=0, actions=0, phase=ACTION)
    assert player.get_current_turn().money == 1
    
def test_change_current_turn_fields(full_ruleset_game_player, turn, monkeypatch):
    '''
    A test for changing the current player turn.
    '''
    player = full_ruleset_game_player
    hook(player, player.get_current_turn, monkeypatch)
    assert turn
    player.change_current_turn_fields(1, 1, 1)
    assert player.get_current_turn().money != 0
    assert player.called_get_current_turn
    player.create_turn(money=2, actions=2, buys=2, phase=CLEANUP)
    assert player.get_current_turn() != turn
    player.change_current_turn_fields(-1, -1, -1)
    assert player.get_current_turn().buys == 1
    
    
