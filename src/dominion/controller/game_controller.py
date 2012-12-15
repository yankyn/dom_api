'''
Created on Dec 15, 2012

@author: Nathaniel
'''
from dominion.orm.game import Game
from dominion.orm.player import Player
from dominion.orm.utils.autosave import save

@save
def create_player(*args, **kwargs):
    '''
    Writes a player to the DB.
    '''
    return Player(*args, **kwargs)

@save
def create_game(ruleset, *args, **kwargs):
    '''
    Writes a game to the DB.
    '''
    return Game(ruleset=ruleset, *args, **kwargs)
