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
        # Maybe switch back to all documents?
        if isinstance(arg, AutoSaveDocument):
            arg.save()

@decorator
def save(func, *args, **kwargs):
    '''
    This is a decorator for having functions save after execution.
    '''
    val = func(*args, **kwargs)
    save_args(args)
    return val

'''
Classes
'''

class AutoSaveDocument(Document):
    '''
    Our own implementation of a document that is automatically saved on any save requiring action.
    '''
    meta = {'allow_inheritance': True}
    
    def __init__(self, *args, **kwargs):
        '''
        Save at the end of construction.
        '''
        # We want to intialize should_save because __init__ calls __setsttr__.
        self.should_save = False
        Document.__init__(self, *args, **kwargs)
        self.save()
        self.should_save = True
        
    def __setattr__(self, name, value):
        '''
        Setting attributes often consistates a save.
        '''
        Document.__setattr__(self, name, value)
        # We do not want to save recursively so we use should_save.
        if name in self._fields and self.should_save:
            self.should_save = False
            self.save()
            self.should_save = True
            
