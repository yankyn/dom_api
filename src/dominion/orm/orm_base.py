'''
Created on Nov 24, 2012

@author: Nathaniel
'''
class OrmBase(object):
    '''
    Base for all documents to inherit from.
    '''
    
    @property
    def _id(self):
        '''
        Stringwise ID.
        '''
        return str(self.id)
        
