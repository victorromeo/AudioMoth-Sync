import enum
from transitions.extensions import HierarchicalMachine as Machine
#from transitions.extensions.nesting import NestedState
from pprint import pprint

_name = 'name'
_children = 'children'
_trigger = 'trigger'
_source = 'source'
_dest = 'dest'
_trigger = 'trigger'
_before = 'before'
_after = 'after'
_prepare = 'prepare'
_conditions = 'conditions'
_unless = 'unless'
_on_enter = 'on_enter'
_on_exit = 'on_exit'

class state():

    def __init__(self, name):
        self.s = {}
        self.s[_name] = name
    
    def on_enter(self, operation):
        self.s.on_enter = operation
        return self

    def on_exit(self, operation):
        self.s[_on_exit] = operation
        return self

    def children(self, states):
        self.s[_children] = states
        return self

    def get(self):
        return self.s

class transition():

    def __init__(self,trigger,source,dest):
        self.t = {}
        self.t[_trigger] = trigger
        self.t[_source] = source
        self.t[_dest] = dest

    def before(self, operation):
        self.t[_before] = operation
        return self

    def after(self, operation):
        self.t[_after] = operation
        return self

    def prepare(self, operation):
        self.t[_prepare] = operation
        return self

    def conditions(self, operations):
        self.t[_conditions] = operations
        return self

    def unless(self, operation):
        self.t[_unless] = operation
        return self

    def get(self):
        return self.t