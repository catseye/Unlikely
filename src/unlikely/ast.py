# -*- coding: utf-8 -*-

# (c)2010-2012 Chris Pressey, Cat's Eye Technologies.
# All rights reserved.  Released under a BSD-style license (see LICENSE).

"""
Abstract Syntax Trees for the Unlikely programming language.
$Id: ast.py 318 2010-01-07 01:49:38Z cpressey $
"""


class ArtefactExistsError(Exception):
    """An exception indicating that a proposed artefact (class, method,
    property, ...) already exists.

    """
    pass


class ArtefactNotFoundError(Exception):
    """An exception indicating that a needed artefact (class, method,
    property, ...) does not exist.

    """
    pass


class BadModifierError(Exception):
    """An exception indicating that a specified modifier is not valid."""
    pass


class IncompatibleTypeError(Exception):
    """An exception indicating that the types of two connected subexpressions
    are not compatible.

    """
    pass


class ClassRelationshipError(Exception):
    """An exception indicating that the specified relationship between two
    classes is illegal.

    """
    pass


class AST:
    """Class representing nodes in an abstract syntax tree."""
    pass


class ClassBase(AST):
    """A collection of Unlikely class definitions."""
    def __init__(self):
        self.class_defn_map = {}

    def __str__(self):
        s = ""
        for class_name in self.class_defn_map:
            s = s + str(self.class_defn_map[class_name]) + " "
        return "ClassBase { " + s + "}"

    def add_class_defn_by_name(self, class_name, superclass_name=None,
                               modifiers=None):
        """A factory method.  Call this instead of ClassDefn().
        If a class was declared forward, this will return the stub.
        The third and fourth arguments are conveniences for stdlib.

        """
        if class_name in self.class_defn_map:
            class_defn = self.class_defn_map[class_name]
        else:
            class_defn = ClassDefn(self, class_name)
            self.class_defn_map[class_name] = class_defn
        if modifiers is not None:
            for modifier in modifiers:
                class_defn.add_modifier(modifier)
        if superclass_name is not None:
            class_defn.set_superclass_by_name(superclass_name)
        return class_defn

    def lookup_class_defn(self, class_name):
        if class_name in self.class_defn_map:
            return self.class_defn_map[class_name]
        raise ArtefactNotFoundError("class " + class_name)


class ClassDefn(AST):
    """
    A definition of an Unlikely class.
    Really, only ClassBase should be allowed to call this constructor.
    Everyone else should use the factory methods on ClassBase.
    """
    def __init__(self, classbase, class_name):
        assert isinstance(classbase, ClassBase)
        self.classbase = classbase
        self.name = class_name
        self.superclass = None
        self.dependant_map = {}
        self.dependant_names = []
        self.prop_defn_map = {}
        self.method_defn_map = {}
        self.modifiers = []

    def __str__(self):
        c = "class " + self.name + "("
        d = ""
        for class_name in self.dependant_map:
            if d == "":
                d = d + class_name
            else:
                d = d + "," + class_name
        c = c + d + ") "
        if self.superclass is not None:
            c = c + "extends " + self.superclass.name + " "
        c = c + "{ "
        for prop_name in self.prop_defn_map:
            prop_defn = self.prop_defn_map[prop_name]
            c = c + str(prop_defn) + " "
        for method_name in self.method_defn_map:
            method_defn = self.method_defn_map[method_name]
            c = c + str(method_defn) + " "
        return c + "}"

    def set_superclass_by_name(self, superclass_name):
        """
        Sets the superclass of this class.
        """
        superclass = self.classbase.lookup_class_defn(superclass_name)
        if not self.has_modifier("forcible"):
            if superclass.has_modifier("final"):
                raise ClassRelationshipError("cannot inherit from final " +
                                             superclass_name)
        if (self.superclass is not None and
            self.superclass.name != superclass_name):
            raise ClassRelationshipError("class " + self.name +
                                         " already has superclass " +
                                         self.superclass.name)
        self.superclass = superclass
        if len(self.dependant_names) == 0:
            for dependant_name in superclass.dependant_names:
                self.dependant_names.append(dependant_name)
                self.dependant_map[dependant_name] = \
                  superclass.dependant_map[dependant_name]
        return superclass

    def add_dependant_by_name(self, dependant_name):
        if dependant_name in self.dependant_map:
            raise ClassRelationshipError("dependant " + dependant_name +
                                         " already declared")
        dependant = self.classbase.lookup_class_defn(dependant_name)
        self.dependant_map[dependant.name] = dependant
        self.dependant_names.append(dependant.name)

    def get_dependant_by_index(self, index):
        return self.dependant_map[self.dependant_names[index]]

    def add_prop_defn_by_name(self, prop_name, type_class_name):
        """
        Factory method.  Call this instead of PropDefn().
        """
        try:
            prop_defn = self.lookup_prop_defn(prop_name)
        except ArtefactNotFoundError:
            prop_defn = PropDefn(self, prop_name)
            self.prop_defn_map[prop_name] = prop_defn
            prop_defn.type_class_defn = self.lookup_class_defn(type_class_name)
            return prop_defn
        raise ArtefactExistsError("property " + prop_defn.name)

    def add_method_defn_by_name(self, method_name):
        """
        Factory method.  Call this instead of MethodDefn().
        """
        if method_name in self.method_defn_map:
            raise ArtefactExistsError("method " + method_name)
        try:
            overridden_method_defn = self.lookup_method_defn(method_name)
        except ArtefactNotFoundError:
            overridden_method_defn = None
        if (self.is_saturated() and overridden_method_defn is None and
            self.superclass is not None):
            raise ClassRelationshipError("new method " + method_name +
                                         " not allowed on saturated " +
                                         self.name)
        method_defn = MethodDefn(self, method_name)
        self.method_defn_map[method_defn.name] = method_defn
        return method_defn

    def add_modifier(self, modifier):
        if modifier not in ["final", "saturated", "abstract", "forcible"]:
            raise BadModifierError(modifier)
        self.modifiers.append(modifier)

    def has_modifier(self, modifier):
        return modifier in self.modifiers

    def must_be_injected(self):
        if self.has_modifier("final"):
            return False
        return True

    def lookup_class_defn(self, class_name):
        """Note that this first looks up the class definition in the dependant
        classes of this class: all classes referred to by a class *must* be
        injected!  And then the dependants of the superclass of this class.
        This doesn't apply for final classes, since injecting them doesn't
        make any sense.

        """
        if class_name[0].isdigit():
            class_defn = self.classbase.add_class_defn_by_name(class_name)
            class_defn.add_modifier("final")
            class_defn.add_modifier("forcible")
            class_defn.set_superclass_by_name("Integer")
            return class_defn
        if class_name[0] == "\"":
            class_defn = self.classbase.add_class_defn_by_name(class_name)
            class_defn.add_modifier("final")
            class_defn.add_modifier("forcible")
            class_defn.set_superclass_by_name("String")
            return class_defn
        if class_name in self.dependant_map:
            return self.dependant_map[class_name]
        if self.superclass is not None:
            return self.superclass.lookup_class_defn(class_name)
        class_defn = self.classbase.lookup_class_defn(class_name)
        if class_defn is not None and not class_defn.must_be_injected():
            return class_defn
        raise ArtefactNotFoundError("dependant class " + class_name)

    def lookup_prop_defn(self, prop_name):
        if prop_name in self.prop_defn_map:
            return self.prop_defn_map[prop_name]
        if self.superclass is not None:
            return self.superclass.lookup_prop_defn(prop_name)
        raise ArtefactNotFoundError("property " + prop_name)

    def lookup_method_defn(self, method_name):
        if method_name in self.method_defn_map:
            return self.method_defn_map[method_name]
        if self.superclass is not None:
            return self.superclass.lookup_method_defn(method_name)
        raise ArtefactNotFoundError("method " + method_name)

    def is_subclass_of(self, class_defn):
        if self == class_defn:
            return True
        if self.superclass is None:
            return False
        return self.superclass.is_subclass_of(class_defn)

    def is_saturated(self):
        if self.has_modifier("saturated"):
            return True
        if self.superclass is None:
            return False
        return self.superclass.is_saturated()

    def find_all_method_defns(self, map=None):
        """
        Returns all methods defined and inherited by this class, in the form
        of a map from method name to method definition object.
        """
        if map is None:
            map = {}
        for method_defn_name in self.method_defn_map:
            if method_defn_name not in map:
                map[method_defn_name] = self.method_defn_map[method_defn_name]
        if self.superclass is not None:
            self.superclass.find_all_method_defns(map)
        return map

    def typecheck(self):
        map = self.find_all_method_defns()
        if not self.has_modifier("abstract"):
            for method_defn_name in map:
                if map[method_defn_name].has_modifier("abstract"):
                    message = ("concrete class " + self.name +
                               " does not implement abstract method " +
                               method_defn_name)
                    raise ClassRelationshipError(message)
        else:
            all_concrete = True
            for method_defn_name in map:
                if map[method_defn_name].has_modifier("abstract"):
                    all_concrete = False
            if all_concrete:
                raise ClassRelationshipError("abstract class " + self.name +
                                             " has no abstract methods")


class PropDefn(AST):
    """
    Definition of a property on an Unlikely class.
    """
    def __init__(self, class_defn, name):
        assert isinstance(class_defn, ClassDefn)
        self.class_defn = class_defn
        self.name = name
        self.type_class_defn = None

    def __str__(self):
        return self.type_class_defn.name + " " + self.name

    def lookup_class_defn(self, class_name):
        return self.class_defn.lookup_class_defn(class_name)


class MethodDefn(AST):
    """
    Definition of a method on an Unlikely class.
    """
    def __init__(self, class_defn, name):
        assert isinstance(class_defn, ClassDefn)
        self.class_defn = class_defn
        self.name = name
        self.param_decl_map = {}
        self.param_names = []
        self.assignments = []
        self.modifiers = []
        self.continue_ = None

    def __str__(self):
        c = "method " + self.name + "("
        d = ""
        for param_name in self.param_names:
            p = str(self.param_decl_map[param_name])
            if d == "":
                d = d + p
            else:
                d = d + "," + p
        c = c + d + ")"
        return c

    def add_param_decl_by_name(self, param_name, type_class_name):
        """
        Factory method.  Call this instead of ParamDecl().
        """
        if param_name in self.param_decl_map:
            raise ArtefactExistsError("param " + param_name)
        prop_defn = self.lookup_prop_defn(param_name)
        type_class_defn = self.lookup_class_defn(type_class_name)
        if prop_defn.type_class_defn != type_class_defn:
            raise IncompatibleTypeError(param_name + " param is a " +
                                        type_class_name +
                                        " but property is a " +
                                        prop_defn.type_class_defn.name)
        param_decl = ParamDecl(self, param_name, type_class_defn)
        self.param_decl_map[param_name] = param_decl
        self.param_names.append(param_name)
        return param_decl

    def add_assignment(self):
        """
        Factory method.  Call this instead of Assignment().
        """
        assignment = Assignment(self)
        self.assignments.append(assignment)
        return assignment

    def add_modifier(self, modifier):
        if modifier not in ["abstract"]:
            raise BadModifierError(modifier)
        self.modifiers.append(modifier)

    def has_modifier(self, modifier):
        return modifier in self.modifiers

    def add_continue(self):
        """
        Factory method.  Call this instead of Continue().
        """
        assert self.continue_ == None
        continue_ = Continue(self)
        self.continue_ = continue_
        return continue_

    def lookup_class_defn(self, class_name):
        return self.class_defn.lookup_class_defn(class_name)

    def lookup_prop_defn(self, prop_name):
        return self.class_defn.lookup_prop_defn(prop_name)

    def get_param_decl_by_index(self, index):
        param_name = self.param_names[index]
        param_decl = self.param_decl_map[param_name]
        return param_decl


class ParamDecl(AST):
    """
    Definition of a formal parameter to an Unlikely method.
    """
    def __init__(self, method_defn, name, type_class_defn):
        assert isinstance(method_defn, MethodDefn)
        self.method_defn = method_defn
        self.name = name
        self.type_class_defn = type_class_defn

    def __str__(self):
        return self.type_class_defn.name + " " + self.name


class Assignment(AST):
    """
    An Unlikely assignment statement.
    """
    def __init__(self, method_defn):
        assert isinstance(method_defn, MethodDefn)
        self.method_defn = method_defn
        self.lhs = None
        self.rhs = None

    def add_qual_name(self):
        qual_name = QualName(self)
        if self.lhs is None:
            self.lhs = qual_name
        else:
            assert self.rhs is None
            self.rhs = qual_name
        return qual_name

    def add_construction(self, type_class_name):
        construction = Construction(self, type_class_name)
        assert self.rhs is None
        self.rhs = construction
        return construction


class Continue(AST):
    """
    An Unlikely continue ("goto") statement.
    """
    def __init__(self, method_defn):
        assert isinstance(method_defn, MethodDefn)
        self.method_defn = method_defn
        self.prop_defn = None
        self.method_name = None
        self.param_exprs = []

    def set_prop_defn_by_name(self, prop_name):
        self.prop_defn = self.method_defn.lookup_prop_defn(prop_name)
        assert isinstance(self.prop_defn, PropDefn)

    def set_method_defn_by_name(self, method_name):
        type_class_defn = self.prop_defn.type_class_defn
        self.method_defn = type_class_defn.lookup_method_defn(method_name)
        assert isinstance(self.method_defn, MethodDefn)

    def add_qual_name(self):
        qual_name = QualName(self)
        self.param_exprs.append(qual_name)
        return qual_name

    def add_construction(self, type_class_name):
        construction = Construction(self, type_class_name)
        self.param_exprs.append(construction)
        return construction

    def typecheck(self):
        if len(self.param_exprs) != len(self.method_defn.param_names):
            message = ("continue provides " + str(len(self.param_exprs)) +
                       " params, " + str(len(self.method_defn.param_names)) +
                       " needed")
            raise IncompatibleTypeError(message)
        i = 0
        for param_expr in self.param_exprs:
            param_decl = self.method_defn.get_param_decl_by_index(i)
            arg_type_class_defn = param_expr.get_type_class_defn()
            param_type_class_defn = param_decl.type_class_defn
            if not arg_type_class_defn.is_subclass_of(param_type_class_defn):
                message = (arg_type_class_defn.name + " not a subclass of " +
                           param_type_class_defn.name)
                raise IncompatibleTypeError(message)
            i += 1


class Construction(AST):
    """
    An Unlikely construction ("new") expression.
    """
    def __init__(self, parent, type_class_name):
        assert isinstance(parent, Assignment) or isinstance(parent, Continue)
        self.parent = parent
        self.type_class_defn = \
          self.parent.method_defn.lookup_class_defn(type_class_name)
        self.dependencies = []

    def add_dependency_by_name(self, class_name):
        dependency = self.parent.method_defn.lookup_class_defn(class_name)
        self.dependencies.append(dependency)
        return dependency

    def get_type_class_defn(self):
        return self.type_class_defn

    def typecheck(self):
        if len(self.dependencies) != len(self.type_class_defn.dependant_names):
            message = ("instantiation specifies " +
                       str(len(self.dependencies)) + " classes, " +
                       str(len(self.type_class_defn.dependant_names)) +
                       " needed (" +
                       ",".join(self.type_class_defn.dependant_names) + ")")
            raise IncompatibleTypeError(message)
        i = 0
        for dependency in self.dependencies:
            dependant_class_defn = \
              self.type_class_defn.get_dependant_by_index(i)
            if not dependency.is_subclass_of(dependant_class_defn):
                message = (dependency.name + " not a subclass of " +
                           dependant_class_defn.name)
                raise IncompatibleTypeError(message)
            i += 1


class QualName(AST):
    """
    An Unlikely qualified name (property reference) expression.
    """
    def __init__(self, parent):
        assert isinstance(parent, Assignment) or isinstance(parent, Continue)
        self.parent = parent
        self.prop_defns = []
        self.scope_class_defn = self.parent.method_defn.class_defn

    def add_prop_defn_by_name(self, prop_name):
        prop_defn = self.scope_class_defn.lookup_prop_defn(prop_name)
        self.prop_defns.append(prop_defn)
        self.scope_class_defn = prop_defn.type_class_defn
        return prop_defn

    def get_type_class_defn(self):
        return self.scope_class_defn

    def get_prop_defn_by_index(self, index):
        return self.prop_defns[index]
