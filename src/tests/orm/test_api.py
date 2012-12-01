'''
Created on Nov 23, 2012

@author: Nathaniel
'''
import datetime

TEST_DB = 'DOMINION_TEST'

from utils import dominion_fix #@UnusedImport
from dominion.orm import Player, GeneralRuleSet, Game, GamePlayer, SpecificRuleSet

def test_start_game(dominion_fix):
    ruleset = GeneralRuleSet(name='test_ruleset')
    ruleset.save()
    
    date = datetime.datetime.now()
    ruleset.start_game(start_date=date)
    
    assert Game.objects
    assert ruleset.games[0].ruleset == ruleset
    assert len(GeneralRuleSet.objects(games__start_date=date)) == 1
    
       

