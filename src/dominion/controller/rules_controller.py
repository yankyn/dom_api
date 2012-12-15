'''
A module allowing admins to manage the configuration database.
One day we may want to provide gui for this, but this is not a priority.

Created on Dec 15, 2012

@author: Nathaniel
'''
from dominion.dominion_exceptions.exceptions import DominionException
from dominion.orm.card import Card
from dominion.orm.rulesets import Rules, GeneralRuleSet, SpecificRuleSet
from dominion.orm.utils.autosave import save
from dominion.orm.utils.game_consts import INACTIVE, ACTION, BUY, CLEANUP, \
    TREASURE, CURSE, VICTORY, ATTACK, REACTION

DEFAULT_PHASE_ORDER = [INACTIVE, ACTION, BUY, CLEANUP]
DEFAULT_CARD_TYPES = [TREASURE, ACTION, CURSE, VICTORY, ATTACK, REACTION]

@save
def create_constant_rules(phase_order=DEFAULT_PHASE_ORDER, card_types=DEFAULT_CARD_TYPES):
    '''
    Creates a set of constant rules.
    '''
    if Rules.objects(_is_constant=True): #@UndefinedVariable
            raise DominionException('''Constant rules configuration document already exists
            , please check your actions again''')
    else:
        rules = Rules(phase_order=phase_order, card_types=card_types, _is_constant=True)
    return rules
 
@save
def create_general_rule_set(*args, **kwargs):
    '''
    Initializes a general rule set from the configured constant rules.
    '''
    if not Rules.objects(_is_constant=True): #@UndefinedVariable
        raise DominionException('Default constant rules are not configured!')
    rules = GeneralRuleSet(*args, **kwargs)
    
    copy_fields(rules, Rules.objects(_is_constant=True)[0]) #@UndefinedVariable
    
    return rules

@save
def create_specific_rule_set(parent, *args, **kwargs):
    '''
    Creates a specific rule set from a received general_rule_set name.
    '''
    name = parent.name
    
    if not GeneralRuleSet.objects(name=name, _is_general=True): #@UndefinedVariable
        raise DominionException('No such rule set %s!' % name)
    rules = SpecificRuleSet(name=name, *args, **kwargs)
    copy_fields(rules, GeneralRuleSet.objects(name=name, _is_general=True)[0]) #@UndefinedVariable
    
    return rules
    
@save         
def copy_fields(child, parent):
        '''
        Copies the parent's fields to the child document. This is used to easily 
        construct rule sets from other rule sets.
        '''
        for field in parent._fields:
            if field not in parent.no_copy_fields:
                setattr(child, field, getattr(parent, field))
                
@save
def create_card(name, cost, type, *args, **kwargs):
    '''
    Writes a card to the database.
    '''
    return Card(name=name, cost=cost, type=type, *args, **kwargs)
