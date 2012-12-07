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
    for arg in args:
        if isinstance(arg, Document):
            arg.save()

def _save(func, *args, **kwargs):
    save_args(args)
    val = func(*args, **kwargs)
    save_args(args)
    return val
    
def save(func):
    return decorator(_save, func)

'''
Classes
'''

class AutoSaveDocument(Document):
    
    meta = {'allow_inheritance': True}
    
    def __init__(self, *args, **kwargs):
        self.should_save = False
        Document.__init__(self, *args, **kwargs)
        self.save()
        self.should_save = True
        
    def __setattr__(self, name, value):
        Document.__setattr__(self, name, value)
        if name in self._fields and name != 'id' and self.should_save:
            self.should_save = False
            self.save()
            self.should_save = True
            
