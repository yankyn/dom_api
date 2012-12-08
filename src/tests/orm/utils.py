'''
Created on Dec 1, 2012

@author: Nathaniel
'''
from decorator import decorator #@UnresolvedImport
from dominion.orm import connect, GeneralRuleSet
from dominion.orm.card import Card
from dominion.orm.rulesets import ConstantRules
from dominion.orm.utils.game_consts import TREASURE, VICTORY, COPPER, ESTATE
import pytest
from dominion.orm.player import Player

TEST_DB = 'DOMINION_AUTO_TEST'

'''
Fixtures
'''

@pytest.fixture
def dominion_fix(request):
    '''
    Fixture for creating and dropping a test db.
    '''
    con = connect(TEST_DB)
    def fin():
        con.drop_database(TEST_DB)
    request.addfinalizer(fin)
    
@pytest.fixture
def ruleset(request, dominion_fix):
    '''
    Fixture for creating rulesets.
    '''
    const_rules = ConstantRules()
    const_rules.save()
    
    ruleset = GeneralRuleSet(name='test_ruleset')
    return ruleset

@pytest.fixture
def ruleset_game(request, ruleset):
    '''
    Fixture for creating games with rulesets.
    '''
    return ruleset.create_game()

def create_cards():
    if not Card.objects(name=COPPER): #@UndefinedVariable
        copper = Card(name=COPPER, cost=0, type=TREASURE, money=1)
    if not Card.objects(name=ESTATE): #@UndefinedVariable
        estate = Card(name=ESTATE, cost=2, type=VICTORY, victory=1)

@pytest.fixture
def full_ruleset(request, ruleset):
    '''
    A Fixture for creating rule_sets with content.
    '''
    create_cards()
    ruleset.starting_deck = [Card.objects(name=COPPER)[0]] * 7 #@UndefinedVariable
    ruleset.starting_deck.extend([Card.objects(name=ESTATE)[0]] * 3) #@UndefinedVariable
    ruleset.save()
    ruleset.create_specific_ruleset(player_number = 1)
    return ruleset

@pytest.fixture
def full_ruleset_game(request, full_ruleset):
    '''
    A Fixture for creating rule_sets with content.
    '''
    game = full_ruleset.create_game()
    return game

@pytest.fixture
def full_ruleset_game_player(full_ruleset_game):
    player = Player(name = 'test_player')
    full_ruleset_game.add_player(player)
    return full_ruleset_game._get_player(player)

