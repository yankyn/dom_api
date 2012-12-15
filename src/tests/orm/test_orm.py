'''
This is a test suite for the "schema" part of the orm. We do not test advanced functionalities but rather
that our objects contain the desired fields.

NOTE: Add tests to this suite every time you write a functionality to test that the necessary objects work.

Created on Nov 23, 2012

@author: Nathaniel
'''
from dominion.controller.game_controller import create_player, create_game
from dominion.controller.rules_controller import create_constant_rules, \
    create_specific_rule_set
from dominion.dominion_exceptions.exceptions import DominionException
from dominion.orm import Player, Game, GamePlayer
from dominion.orm.rulesets import Rules, SpecificRuleSet
from dominion.orm.utils.game_consts import MONEY, BUYS, ACTIONS, HAND_SIZE, \
    INACTIVE, ACTION, BUY, CLEANUP, TREASURE, CURSE, VICTORY, ATTACK, REACTION
from utils import dominion_fix, ruleset #@UnusedImport
import datetime
import pytest


def test_player(dominion_fix):
    '''
    Tests creating a player and saving it to the DB.
    '''
    create_player(name='test_player')
    assert Player.objects(name='test_player') #@UndefinedVariable
    
def test_ruleset_game(dominion_fix, ruleset):
    '''
    Tests creating a game and a ruleset and connecting them together.
    '''
    date = datetime.datetime.now()
    game = create_game(ruleset=None, start_date=date)
    
    game.ruleset = ruleset
    
    assert game.ruleset.name == 'test_ruleset'
    assert Game.objects(start_date=date) #@UndefinedVariable
    
def test_spec_ruleset(dominion_fix, ruleset):
    '''
    Tests adding a variation to a ruleset and querrying by its number of players.
    '''
    create_specific_rule_set(parent=ruleset, player_number=2)
    
    assert SpecificRuleSet.objects(player_number__gt=1)#@UndefinedVariable
    assert SpecificRuleSet.objects(name=ruleset.name) #@UndefinedVariable
    
def test_game_player(dominion_fix):
    '''
    Tests creating games and connecting them to players.
    '''
    game = create_game(ruleset=None)
    player = create_player(name='test_player')

    player.games.append(game)
    player.save()
    gameplayer = GamePlayer(player=player)
    game.game_players[str(player.id)] = gameplayer
    game.save()

    assert game.game_players
    assert game.game_players[str(player.id)].player == player
    assert Player.objects(games=game) #@UndefinedVariable
    
def test_constant_rules_validate(dominion_fix):
    '''
    Tests validating that there is only one constant rule_set
    '''
    const_rules = create_constant_rules()
    const_rules.validate()
    const_rules.save()
    
    with pytest.raises(DominionException): 
        const_rules_2 = create_constant_rules()
    
def test_const_rules_default(dominion_fix):
    '''
    Tests that the default constant rules are fine.
    '''
    cr = create_constant_rules()
    assert cr.money == MONEY
    assert cr. buys == BUYS
    assert cr.actions == ACTIONS
    assert cr.hand_size == HAND_SIZE
    assert cr.phase_order == [INACTIVE, ACTION, BUY, CLEANUP]
    assert cr.card_types == [TREASURE, ACTION, CURSE, VICTORY, ATTACK, REACTION]
       

