'''
Created on Dec 1, 2012

@author: Nathaniel
'''
from decorator import decorator
from dominion.orm import connect, GeneralRuleSet
from dominion.orm.card import Card
from dominion.orm.player import Player
from dominion.orm.rulesets import ConstantRules
from dominion.orm.utils.dev_utils import untested
from dominion.orm.utils.game_consts import TREASURE, VICTORY, COPPER, ESTATE
import pytest

TEST_DB = 'DOMINION_AUTO_TEST'

'''
Actual utilities
'''

def hook(self, func, monkeypatch):
    '''
    Monkeypatches the given function to announce its number of calls.
    '''
    name = func.im_func.func_name
    new_field_name = 'called_%s' % name
    setattr(self, new_field_name, 0)
    def hooked_func(*args, **kwargs):
        setattr(self, new_field_name, getattr(self, new_field_name) + 1)
        func(*args, **kwargs)
    monkeypatch.setattr(self, name, hooked_func)
    
@untested
def turn_card_dict_to_list(dictionary):
    '''
    Turns a dictionary of cards to numbers to a list of cards where each card's 
    number of instances is equal to its mapped value in the dictionary.
    '''
    cardlist = []
    for cardname in dictionary:
        card = Card.objects(name=cardname)[0] #@UndefinedVariable
        cardlist.extend([card] * dictionary[cardname])
    return cardlist

class HashableDict(dict):
    '''
    Hashable dictionary for fixture parameters. Code copied from stackoverflow.
    '''
    
    def __key(self):
        return tuple((k, self[k]) for k in sorted(self))
    
    def __hash__(self):
        return hash(self.__key())
    
    def __eq__(self, other):
        return self.__key() == other.__key()
    
'''Params for card fixturs.'''
piles_params = [HashableDict({COPPER : 7, ESTATE : 3}), HashableDict({})]
    
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

@pytest.fixture
def full_ruleset(request, cards, ruleset):
    '''
    A Fixture for creating rule_sets with content.
    '''
    ruleset.starting_deck = [Card.objects(name=COPPER)[0]] * 7 #@UndefinedVariable
    ruleset.starting_deck.extend([Card.objects(name=ESTATE)[0]] * 3) #@UndefinedVariable
    ruleset.save()
    ruleset.create_specific_ruleset(player_number=1)
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
    '''
    A fixture for creating a player in game with a full ruleset.
    '''
    player = Player(name='test_player')
    full_ruleset_game.add_player(player)
    return full_ruleset_game._get_player(player)

@pytest.fixture
def cards(request):
    '''
    A fixture for creating example cards.
    '''
    if not Card.objects(name=COPPER): #@UndefinedVariable
        Card(name=COPPER, cost=0, type=TREASURE, money=1)
    if not Card.objects(name=ESTATE): #@UndefinedVariable
        Card(name=ESTATE, cost=2, type=VICTORY, victory=1)

@pytest.fixture(params=piles_params)
def deck(request, cards):
    '''
    A fixture for parametrizing different decks.
    The expected parameters are dictionaries of card names existing in the 
    cards fixture to their wanted pile sizes.
    '''
    dictionary = request.param
    return turn_card_dict_to_list(dictionary)

@pytest.fixture(params=piles_params)
def discard(request, cards):
    '''
    A fixture for parametrizing discard piles.
    The expected parameters are dictionaries of card names existing in the 
    cards fixture to their wanted pile sizes.
    '''
    dictionary = request.param
    return turn_card_dict_to_list(dictionary)
    

