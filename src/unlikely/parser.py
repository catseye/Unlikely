# -*- coding: utf-8 -*-

"""
Parser for the Unlikely programming language.
$Id: parser.py 318 2010-01-07 01:49:38Z cpressey $

Based on the following EBNF grammar:

ClassBase   ::= {ClassDefn}.
ClassDefn   ::= "class" ClassName<NEW> "(" [ClassName {"," ClassName}] ")"
                "extends" ClassName ["{" {PropDefn} {MethodDefn} "}"]
                ["is" ClassMod {"and" ClassMod}].
ClassMod    ::= "final" | "saturated" | "abstract".
PropDefn    ::= ClassName PropName<NEW> ";".
MethodDefn  ::= "method" MethodName<NEW> "(" [ParamDecl {"," ParamDecl}] ")"
                ("{" {Assignment} Continue "}" | "is" "abstract").
ParamDecl   ::= ClassName PropName.
Assignment  ::= QualName "=" Expr ";".
Continue    ::= "goto" PropName "." MethodName "(" [Expr {"," Expr}] ")" ";".
Expr        ::= ConstrExpr | QualName.
ConstrExpr  ::= "new" (ClassName) "(" [ClassName {"," ClassName}] ")".
QualName    ::= PropName {"." PropName}.
Constant    ::= <<sequence of decimal digits>>
              | <<sequence of arbitrary characters between double quotes>>.
"""


class Parser(object):
    """A recursive-descent parser for Unlikely.
    """

    def __init__(self, scanner):
        """
        Creates a new Parser object.  The passed-in scanner is expected
        to be compatible with a Scanner object.
        """
        self.scanner = scanner

    def parse(self):
        raise NotImplementedError


class ClassBaseParser(Parser):
    # ClassBase ::= {ClassDefn}.

    def __init__(self, scanner, classbase=None):
        Parser.__init__(self, scanner)
        self.classbase = classbase

    def parse(self):
        class_defn_parser = ClassDefnParser(self.scanner, self.classbase)
        while self.scanner.token == "class":
            class_defn_parser.parse()


class ClassDefnParser(Parser):
    def __init__(self, scanner, classbase):
        Parser.__init__(self, scanner)
        self.classbase = classbase

    def parse(self):
        self.scanner.expect("class")
        class_name = self.scanner.grab()
        class_defn = self.classbase.add_class_defn_by_name(class_name)
        self.scanner.expect("(")
        dependant_names = []
        if self.scanner.token != ")":
            dependant_names.append(self.scanner.grab())
            while self.scanner.token == ",":
                self.scanner.expect(",")
                dependant_names.append(self.scanner.grab())
        self.scanner.expect(")")
        self.scanner.expect("extends")
        class_defn.set_superclass_by_name(self.scanner.grab())
        for dependant_name in dependant_names:
            class_defn.add_dependant_by_name(dependant_name)
        if self.scanner.token == "{":
            self.scanner.expect("{")
            while self.scanner.token != "}":
                if self.scanner.token == "method":
                    parser = MethodDefnParser(self.scanner, class_defn)
                else:
                    parser = PropDefnParser(self.scanner, class_defn)
                parser.parse()
            self.scanner.expect("}")
            is_forward_decl = False
        else:
            is_forward_decl = True
        if self.scanner.token == "is":
            self.scanner.expect("is")
            class_defn.add_modifier(self.scanner.grab())
            while self.scanner.token == "and":
                self.scanner.expect("and")
                class_defn.add_modifier(self.scanner.grab())
        if not is_forward_decl:
            class_defn.typecheck()


class PropDefnParser(Parser):
    def __init__(self, scanner, class_defn):
        Parser.__init__(self, scanner)
        self.class_defn = class_defn

    def parse(self):
        class_name = self.scanner.grab()
        prop_name = self.scanner.grab()
        self.class_defn.add_prop_defn_by_name(prop_name, class_name)
        self.scanner.expect(";")


class MethodDefnParser(Parser):
    def __init__(self, scanner, class_defn):
        Parser.__init__(self, scanner)
        self.class_defn = class_defn

    def parse(self):
        self.scanner.expect("method")
        method_name = self.scanner.grab()
        method_defn = self.class_defn.add_method_defn_by_name(method_name)
        self.scanner.expect("(")
        if self.scanner.token != ")":
            param_decl_parser = ParamDeclParser(self.scanner, method_defn)
            param_decl_parser.parse()
            while self.scanner.token == ",":
                param_decl_parser.parse()
        self.scanner.expect(")")
        if self.scanner.token == "{":
            self.scanner.expect("{")
            assignment_parser = AssignmentParser(self.scanner, method_defn)
            while self.scanner.token != "goto":
                assignment_parser.parse()
            continue_parser = ContinueParser(self.scanner, method_defn)
            continue_parser.parse()
            self.scanner.expect("}")
        elif self.scanner.token == "is":
            self.scanner.expect("is")
            method_defn.add_modifier(self.scanner.grab())
            while self.scanner.token == "and":
                self.scanner.expect("and")
                method_defn.add_modifier(self.scanner.grab())
        else:
            self.scanner.error("expected '{' or 'is', but found " +
                               self.scanner.token)


class ParamDeclParser(Parser):
    def __init__(self, scanner, method_defn):
        Parser.__init__(self, scanner)
        self.method_defn = method_defn

    def parse(self):
        type_class_name = self.scanner.grab()
        prop_name = self.scanner.grab()
        self.method_defn.add_param_decl_by_name(prop_name, type_class_name)


class AssignmentParser(Parser):
    def __init__(self, scanner, method_defn):
        Parser.__init__(self, scanner)
        self.method_defn = method_defn

    def parse(self):
        assignment = self.method_defn.add_assignment()
        qual_name_parser = QualNameParser(self.scanner, assignment)
        qual_name_parser.parse()
        self.scanner.expect("=")
        expr_parser = ExprParser(self.scanner, assignment)
        expr_parser.parse()
        self.scanner.expect(";")


class ContinueParser(Parser):
    def __init__(self, scanner, method_defn):
        Parser.__init__(self, scanner)
        self.method_defn = method_defn

    def parse(self):
        continue_ = self.method_defn.add_continue()
        self.scanner.expect("goto")
        prop_name = self.scanner.grab()
        self.scanner.expect(".")
        method_name = self.scanner.grab()
        continue_.set_prop_defn_by_name(prop_name)
        continue_.set_method_defn_by_name(method_name)
        self.scanner.expect("(")
        expr_parser = ExprParser(self.scanner, continue_)
        if self.scanner.token != ")":
            expr_parser.parse()
            while self.scanner.token == ",":
                self.scanner.expect(",")
                expr_parser.parse()
        self.scanner.expect(")")
        self.scanner.expect(";")
        continue_.typecheck()
        return continue_


class ExprParser(Parser):
    def __init__(self, scanner, parent):
        Parser.__init__(self, scanner)
        self.parent = parent

    def parse(self):
        if self.scanner.token == "new":
            parser = ConstructionParser(self.scanner, self.parent)
        else:
            parser = QualNameParser(self.scanner, self.parent)
        parser.parse()


class ConstructionParser(Parser):
    def __init__(self, scanner, parent):
        Parser.__init__(self, scanner)
        self.parent = parent

    def parse(self):
        self.scanner.expect("new")
        class_name = self.scanner.grab()
        construction = self.parent.add_construction(class_name)
        self.scanner.expect("(")
        if self.scanner.token != ")":
            construction.add_dependency_by_name(self.scanner.grab())
            while self.scanner.token == ",":
                self.scanner.expect(",")
                construction.add_dependency_by_name(self.scanner.grab())
        self.scanner.expect(")")
        construction.typecheck()


class QualNameParser(Parser):
    def __init__(self, scanner, parent):
        Parser.__init__(self, scanner)
        self.parent = parent

    def parse(self):
        qual_name = self.parent.add_qual_name()
        qual_name.add_prop_defn_by_name(self.scanner.grab())
        while self.scanner.token == ".":
            self.scanner.expect(".")
            qual_name.add_prop_defn_by_name(self.scanner.grab())
