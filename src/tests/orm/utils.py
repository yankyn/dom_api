'''
Created on Dec 1, 2012

@author: Nathaniel
'''
import pytest
from dominion.orm import connect

TEST_DB = 'DOMINION_TEST'

@pytest.fixture
def dominion_fix(request):
    '''
    Fixture for creating and dropping a test db.
    '''
    con = connect(TEST_DB)
    def fin():
        con.drop_database(TEST_DB)
    request.addfinalizer(fin)
