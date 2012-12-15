'''
Created on Dec 1, 2012

@author: Nathaniel
'''
class GameFullException(Exception):
    '''
    Exception for trying to add a player to a full game.
    '''
    def __init__(self, player, game, *args, **kwargs):
        self.player = player
        self.game = game
        message = 'Cannot add any more players to this game! game: %s player %s' \
             % (str(game), str(player))
        Exception.__init__(self, message, *args, **kwargs)
    
class GameNotReadyException(Exception):
    '''
    Exception for trying to start a game that doesn't have a ruleset for current number of players.
    '''
    def __init__(self, game, *args, **kwargs):
        self.game = game
        message = 'Ruleset %s does not support %d players' \
             % (str(game.ruleset.name), len(game.game_players))
        Exception.__init__(self, message, *args, **kwargs)
        
class DominionException(Exception):
    '''
    General logic Exception.
    '''
    pass