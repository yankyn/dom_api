'''
Created on Dec 3, 2012

@author: Nathaniel
'''

from decorator import decorator #@UnresolvedImport
from mongoengine.document import Document

'''
Decorators
'''

def save_args(args):
    '''
    Iterates over the provided arguments and saves them if they are auto-saving documents.
    '''
    for arg in args:
        if isinstance(arg, AutoSave):
            arg.save()

@decorator
def save(func, *args, **kwargs):
    '''
    This is a decorator for having functions save after execution.
    '''
    val = func(*args, **kwargs)
    save_args(args)
    if isinstance(val, AutoSave):
        val.save()
    return val

'''
Classes
'''

class AutoSave(object):
    '''
    Our own implementation of a document that is automatically saved on any field set.
    '''
    
    def __init__(self, *args, **kwargs):
        '''
        Save at the end of construction.
        '''
        # We want to intialize should_save_attrs because __init__ calls __setsttr__.
        self.should_save_attrs = False
        Document.__init__(self, *args, **kwargs)
        self.should_save_attrs = True
        
    def __setattr__(self, name, value):
        '''
        Setting attributes often consistates a save.
        '''
        Document.__setattr__(self, name, value)
        # We do not want to save recursively so we use should_save_attrs.
        if name in self._fields and self.should_save_attrs:
            self.should_save_attrs = False
            self.save()
            self.should_save_attrs = True
            
