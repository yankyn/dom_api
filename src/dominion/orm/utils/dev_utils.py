'''
Created on Dec 7, 2012

@author: Nathaniel
'''

from decorator import decorator #@UnresolvedImport
import sys

@decorator
def untested(func, *args, **kwargs):
    '''
    A decorator for warning on use of untested methods.
    '''
    print >> sys.stderr, 'WARNING: You have called the untested method %s' % str(func)
    func(*args, **kwargs)

@decorator
def undocumented(func, *args, **kwargs):
    '''
    A decorator for notifing on use of undocumented methods.
    '''
    print 'INFO: You have called the undocumented method %s' % str(func)
    func(*args, **kwargs)
