# -*- coding: utf-8 -*-

"""
Interpreter for the Unlikely programming language.  XXX incomplete!
$Id: interpreter.py 509 2010-04-27 20:15:32Z cpressey $
"""

import ast

class Instance(object):
    """
    Represents an instance of an Unlikely class, at runtime.
    """
    
    def __init__(self, class_defn):
        self.class_defn = class_defn
        self.props = {}

    def set(self, prop_name, value):
        self.props[prop_name] = value

    def get(self, prop_name):
        return self.props[prop_name]

    def execute(self, method_name, args):
        """
        Executes a method name in this instance.
        Returns a new instance and method name to be executed next.
        """
        for arg in args:
            self.set(arg, args[arg])
        method_defn = self.class_defn.lookup_method_defn(method_name)
        for assignment in method_defn.assignments:
            self.assign(assignment.lhs, assignment.rhs)
        # apply args in method_defn.continue_
        # get instance from method_defn.continue_
        # get method name from method_defn.continue_
        return (instance, method_name)

    def assign(self, lhs, rhs):
        (instance, prop_name) = self.resolve_qual_name(lhs)
        if isinstance(rhs, Construction):
            value = self.eval_construction(rhs)
        else:
            (src_instance, src_prop_name) = self.resolve_qual_name(rhs)
            value = src_instance.get(src_prop_name)
        instance.set(prop_name, value)

    def resolve_qual_name(self, qual_name, pos = 0):
        prop_defn = qual_name.get_prop_defn_by_index(pos)
        prop_name = prop_defn.name
        if pos == qual_name.length():
            return (self, prop_name)
        instance = self.get(prop_name)
        return instance.resolve_qual_name(qual_name, pos + 1)
