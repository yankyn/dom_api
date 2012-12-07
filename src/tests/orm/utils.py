'''
Created on Dec 1, 2012

@author: Nathaniel
'''
import pytest
from decorator import decorator #@UnresolvedImport
from dominion.orm import connect, GeneralRuleSet, SpecificRuleSet

TEST_DB = 'DOMINION_AUTO_TEST'

'''
Decorators
'''

@decorator
def uniplemented(func, *args, **kwargs):
    func(*args, **kwargs)
    raise NotImplementedError(func)

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
    ruleset = GeneralRuleSet(name='test_ruleset')
    ruleset.save()
    return ruleset

@pytest.fixture
def ruleset_game(request, ruleset):
    '''
    Fixture for creating games with rulesets.
    '''
    return ruleset.create_game()

