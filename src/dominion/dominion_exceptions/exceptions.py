'''
Created on Dec 1, 2012

@author: Nathaniel
'''
class FullGameException(Exception):
    '''
    Exception for trying to add a player to a full game.
    '''
    def __init__(self, player, game, *args, **kwargs):
        self.player = player
        self.game = game
        Exception.__init__(self, 'Cannot add any more players to this game!', *args, **kwargs)
    