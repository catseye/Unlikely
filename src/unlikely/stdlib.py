# -*- coding: utf-8 -*-

# (c)2010-2012 Chris Pressey, Cat's Eye Technologies.
# All rights reserved.  Released under a BSD-style license (see LICENSE).

"""
Pre-built AST representing built-in Unlikely classes.
"""

from .ast import ClassBase

stdlib = ClassBase()

continuation = stdlib.add_class_defn_by_name("Continuation", None,
                                             ["saturated", "abstract"])
program = stdlib.add_class_defn_by_name("Program", "Continuation",
                                        ["abstract"])

chain = stdlib.add_class_defn_by_name("Chain", "Program", ["abstract"])

passive = stdlib.add_class_defn_by_name("Passive", "Chain", ["abstract"])

# Now that we have Passive we patch property and method into Continuation
# and all its subclasses so far
continuation.add_dependant_by_name("Passive")
program.add_dependant_by_name("Passive")
chain.add_dependant_by_name("Passive")
chain.add_dependant_by_name("Chain")
chain.add_prop_defn_by_name("next", "Chain")
passive.add_dependant_by_name("Passive")

accumulator = continuation.add_prop_defn_by_name("accumulator", "Passive")
continue_ = continuation.add_method_defn_by_name("continue")
continue_.add_modifier("abstract")
continue_.add_param_decl_by_name("accumulator", "Passive")

# now we're done patching, we can continue defining further classes
stop = stdlib.add_class_defn_by_name("Stop", "Program", ["final"])

boolean_ = stdlib.add_class_defn_by_name("Boolean", "Passive",
                                         ["abstract", "final"])
true_ = stdlib.add_class_defn_by_name("True", "Boolean",
                                      ["final", "forcible"])
false_ = stdlib.add_class_defn_by_name("False", "Boolean",
                                       ["final", "forcible"])

integer_ = stdlib.add_class_defn_by_name("Integer", "Passive",
                                         ["abstract", "final"])
# we have special logic elsewhere to recognize the countably infinite
# number of subclasses of Integer
string_ = stdlib.add_class_defn_by_name("String", "Passive",
                                        ["abstract", "final"])
# we have special logic elsewhere to recognize the countably infinite
# number of subclasses of String

binary_operation = stdlib.add_class_defn_by_name("BinaryOperation", "Chain",
                                                 ["abstract"])
binary_operation.add_prop_defn_by_name("value", "Passive")

add = stdlib.add_class_defn_by_name("Add", "BinaryOperation")
subtract = stdlib.add_class_defn_by_name("Subtract", "BinaryOperation")
multiply = stdlib.add_class_defn_by_name("Multiply", "BinaryOperation")
divide = stdlib.add_class_defn_by_name("Divide", "BinaryOperation")

condition = stdlib.add_class_defn_by_name("Condition", "BinaryOperation")

equal = stdlib.add_class_defn_by_name("Equal", "Condition")
greater_than = stdlib.add_class_defn_by_name("GreaterThan", "Condition")

print_ = stdlib.add_class_defn_by_name("Print", "Chain")
input_ = stdlib.add_class_defn_by_name("Input", "Chain")

branch = stdlib.add_class_defn_by_name("Branch", "Chain", ["abstract"])
branch.add_prop_defn_by_name("else", "Chain")

if_ = stdlib.add_class_defn_by_name("If", "Branch")

switch = stdlib.add_class_defn_by_name("Switch", "Branch", ["abstract"])
switch.add_prop_defn_by_name("state", "Passive")

loop = stdlib.add_class_defn_by_name("Loop", "Switch", ["abstract"])

while_loop = stdlib.add_class_defn_by_name("WhileLoop", "Loop")
while_loop.add_prop_defn_by_name("test", "Chain")

for_loop = stdlib.add_class_defn_by_name("ForLoop", "Loop")
for_loop.add_prop_defn_by_name("value", "Integer")
for_loop.add_prop_defn_by_name("delta", "Integer")
for_loop.add_prop_defn_by_name("finish", "Integer")
