'''
Created on Nov 24, 2012

@author: Nathaniel
'''
class OrmBase(object):
    
    def __repr__(self):
        string = '<%s' % self.__class__
        if hasattr(self, 'reprs'):
            for field in self.reprs:
                string += ' %s: %s' % (str(field), str(self.reprs[field]))
        string += '>'
        