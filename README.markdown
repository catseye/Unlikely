The Unlikely Programming Language
=================================

Overview
--------

Unlikely is a programming language with the following traits:

-   Unlikely conflates objects with continuations, and methods with
    labels. All classes are subclasses of the root class `Continuation`.
    Every object can be continued at any method. Every method, except
    for the `continue` method on the built-in class `Stop`, must
    continue some other method at the end of its definition.
-   All Unlikely program structures are exposed as objects with
    commensurate inheritance relationships. For example, every Unlikely
    program is a subclass of `Program`, and the classes `If` and
    `Switch` are both subclasses of the abstract base class `Branch`.
-   Unlikely takes dependency injection to the logical extreme.
    Dependency injection is an increasingly popular modern
    object-oriented program construction technique which allows the
    specific classes which will be used by some class ("dependencies")
    to be specified ("injected") when that class is instantiated.
    Unlikely goes one step further by *requiring* that all specific
    classes used by some class are specified during instantiation.

Semantics
---------

### Classes

A class is a schema describing a set of objects. Instantiating a class
produces a new object of that class. When a class is instantiated, all
classes that are referenced by the class (dependant classes) must be
named (injected) by the instantiating code (the instantiator). For each
requested dependant class, any subclass of it may be supplied by the
instantiator, further specifying and constraining behaviour (a technique
called dependency injection). In this way, classes are inherently
parameterized.

When a class refers to itself, it is considered a dependant class of
itself; it (or a subclass) must be injected by the instantiator.

All specified dependant classes must be unique (no dependant class may
be specified more than once.) Final classes need not and may not be
specified as dependant classes because, being final, there is no
subclass that the instantiator could possibly substitute for them.

Each class may define zero or more properties and zero or more methods.

#### Inheritance

Whenever a class is defined in Unlikely source code, a superclass must
be named; the class being defined is thus a subclass that inherits from
that superclass. Its inheritance consists of the properties and methods
defined by the superclass and all of its ancestors (i.e. including all
properties and methods that the superclass inherited from its own
superclasses) as well as the dependant classes of the superclass. The
subclass may not inject dependencies when inheriting from a superclass.
Only single inheritance is supported.

A subclass may override methods that it inherits from its superclass. It
may access the method definition of its direct superclass (or any
indirect ancestor class) by naming that superclass explicitly in a
continue.

A class may be declared as final, in which case it may not be
subclassed. In addition, final dependant classes may not be injected.

A class may also be declared as saturated, in which case it can be
subclassed, but subclasses of it must also be declared as saturated, and
they cannot define any new methods. They can only override existing
methods. In fact, the root class `Continuation` is declared saturated,
so really, all objects have exactly one method, `continue`.

If a class defines or inherits any abstract methods, that class must be
declared as abstract. Abstract classes cannot be instantiated. Any
subclass of an abstract class must define all inherited abstract methods
in order to be considered concrete and thus instantiatable.

### Properties

Each property has a particular type, which is a class. The values it may
take on are objects of that class, or of its subclasses.

Each object has its own instances of the properties defined on the
class, and each of these properties may take on different values.

All state of an object is stored in its properties. Properties are
effectively public; they can be modified by code in any method in any
class.

The root class `Continuation` defines one property, `accumulator`, of
type `Passive`, which all classes inherit.

Subclasses may not override inherited properties.

### Methods

A method is a label on a piece of code inside a class. The methods of a
class are shared by all objects of that class.

A method may be declared abstract instead of defining code for it.
Classes which contain abstract methods must themselves be declared
abstract.

Only one thing may be done to a method in code, which is to continue it
with respect to some object; this is described in the next section.

A method may declare zero or more arguments. Each argument has a type,
which is a class. When a method is continued, a value of the
corresponding type (or some subclass of that type) must be given for
each argument. In actuality, the arguments merely name properties of the
object; they must already be declared in the class before they are
listed in the declaration of the method. Passing values in arguments is
just shorthand for assigning these properties before continuing the
method.

Methods do not have local variables, so for storage must use the
properties of the object on which they were continued.

The root class `Continuation` defines one abstract method which
subclasses must implement, called `continue(Passive accumulator)`. By
convention, this method is what other methods continue. The accumulator
is passed from continuation to continuation, manipulated as execution
proceeds.

### Code

The code inside a class labelled by a method consists of a series of
assignments followed by a continue.

Each assignment consists of an object property on the left-hand side,
and an expression on the right-hand side. The the property so named will
take on the value resulting from evalulating the given expression.
Expressions consist of instantiations of new objects, and references to
other object properties.

The continue names a method on an object to which control flow will
immediately pass. It may also pass values as arguments to that method;
however, this is mere shorthand for assigning properties of the object
on which the method being continued is defined. See above under
"Methods" for more details.

### Passive Data

Passive data values, such as integers and strings, are modelled somewhat
specially in Unlikely, in order to strike a balance in language design
between "too straightforward" and "too convoluted".

All passive data values are instances of some subclass of the abstract
class `Passive`, which is itself a subclass of `Chain`. When a passive
data value is continued, it passes its own value into the accumulator of
the "next" continuation. (It is not necessary, however, to continue the
passive data value to obtain its value in all cases.)

Each immediate subclass of `Passive` gives a data type of values, such
as `Integer` or `String`. Each of these type-classes has a countably
infinite number of subclasses, one for each possible value of that type.
It is these classes that are instantiated to acquire a passive value
object. For example, `three = new 3()` instantiates the value 3. When
the `continue` method on this object is continued, the value that it
represents will be passed down the chain to the continuation assigned to
its `next` property. For example, `three.next = new Print()` would cause
3 to be printed when `three` was continued.

None of the direct subclasses of `Passive` can be further subclassed. In
effect, they are final (despite being abstract!) because all possible
subclasses of them already exist.

Syntax
------

### Overview

The overall schema of a class definition is:

    class ClassName(ClassName,ClassName) extends ClassName {
      ClassName propname;
      method methodname(ClassName propname, ClassName argname) {
        propname = new ClassName(ClassName,ClassName);
        propname.propertyname = argname;
        goto expr.methodname(expr,expr);
      }
    }

### Grammar

A somewhat more formal definition of the syntactic structure of Unlikely
code is given in the following EBNF-like grammar.

    ClassBase   ::= {ClassDefn}.
    ClassDefn   ::= "class" ClassName<NEW> "(" [ClassName {"," ClassName}] ")" "extends" ClassName
                    ["{" {PropDefn} {MethodDefn} "}"] ["is" ClassMod {"and" ClassMod}].
    ClassMod    ::= "final" | "saturated" | "abstract".
    PropDefn    ::= ClassName PropName<NEW> ";".
    MethodDefn  ::= "method" MethodName<NEW> "(" [ParamDecl {"," ParamDecl}] ")"
                    ("{" {Assignment} Continue "}" | "is" "abstract").
    ParamDecl   ::= ClassName PropName.
    Assignment  ::= QualName "=" Expr ";".
    Continue    ::= "goto" PropName "." MethodName "(" [Expr {"," Expr}] ")" ";".
    Expr        ::= ConstrExpr | QualName.
    ConstrExpr  ::= "new" (ClassName | Constant) "(" [ClassName {"," ClassName}] ")".
    QualName    ::= PropName {"." PropName}.
    ClassName   ::= <<sequence of alphabetic characters>> | Constant.
    Constant    ::= <<sequence of decimal digits>> | <<sequence of arbitrary characters between double quotes>>.

Note that multiple ClassDefns for a single class may appear; each may
partially define the class. In this way a "forward declaration" of a
class may occur. This may give its name, superclass, and dependant
classes, so these can be consumed by some following class that requires
them, before the methods of this class are defined. The dependant
classes are cumulative over successive partial definitions; they need
not be repeated. However the same superclass must be specified for all
partial definitions of a class.

Built-in Classes
----------------

-   `Continuation`

    The abstract base class that is the superclass of all Unlikely
    classes, and which can't be instantiated. Declares the property
    `Passive accumulator`, and the abstract method
    `continue(Passive accumulator)`, which all concrete subclasses must
    implement. Is declared `saturated`, so no subclass may declare or
    define any additional methods.

    -   `Program`

        An abstract continuation that provides the guarantee that it can
        be started (that is, that its `continue` method can be initially
        continued) from the operating system. It can be reasonably
        expected that the `accumulator` will be assigned a value
        provided by the user, perhaps via a command-line argument.

        -   `Stop`

            A concrete continuation which exits to the operating system
            when continued. The accumulator is used as the exit code,
            assuming the operating system supports this.

        -   `Chain`

            An abstract continuation which defines the property
            `Continuation next`. When a subclass of `Chain` is
            continued, it will generally continue the continuation
            assigned to its `next` property after doing something.

            -   `Passive`

                The abstract final base class representing passive data
                values. Discards whatever accumulator was passed to it,
                and passes its own value into the accumulator when it
                continues the continuation assigned to its `next`
                property.

                -   `Boolean`

                    The abstract final base class representing boolean
                    values.

                    -   `True`, `False`

                        Final classes representing particular boolean
                        values.

                -   `Integer`

                    The abstract final base class representing integer
                    values.

                    -   `0`, `1`, `2`...

                        Final classes representing particular integer
                        values. Note that only positive constants are
                        available; negative values must be computed by
                        subtracting from 0.

                -   `String`

                    The abstract final class representing string values.

                    -   `""`, `"a"`, `"b"`, `"aa"`...

                        Final classes representing particular string
                        values.

            -   `BinaryOperation`

                A continuation which posesses a property `value` and
                which yields a value when continued by applying some
                operation to `value` (treated as LHS) and the
                accumulator (treated as RHS.)

                -   `Add`

                    A concrete binary operation which adds `value` to
                    the accumulator and passes the result when
                    continuing `next`.

                -   `Subtract`

                    A concrete binary operation which subtracts the
                    accumulator from `value` and passes the result when
                    continuing `next`.

                -   `Multiply`

                    A concrete binary operation which multiplies `value`
                    by the accumulator and passes the result when
                    continuing `next`.

                -   `Divide`

                    A concrete binary operation which divides `value` by
                    the accumulator and passes the result when
                    continuing `next`.

                -   `Condition`

                    A BinaryOperation which yields a boolean value.

                    -   `Equal`

                        A concrete binary operation which compares
                        `value` to the accumulator and passes True when
                        continuing `next` only if they are equal.

                    -   `GreaterThan`

                        A concrete binary operation which compares
                        `value` to the accumulator and passes True when
                        continuing `next` only if `value` is greater.

            -   `Print`

                A concrete continuation which displays the value of the
                accumulator to the user before continuing its `next`
                property.

            -   `Input`

                A concrete continuation which obtains a value from the
                user, and passes this value in the accumulator when
                continuing its `next` property.

            -   `Branch`

                An abstract continuation which continues one of the
                continuations assigned to its properties, based on some
                other information. Defines the `Chain` property `else`
                which represents the basic alternate continuation that
                can be continued instead of `next`.

                -   `If`

                    A continuation which continues one of two
                    continuations assigned to its properties, `next` and
                    `else`, based on whether the accumulator is an
                    instance of `True` or `False`.

                -   `Switch`

                    An abstract continuation whose behaviour differs on
                    subsequent times it is continued. This is
                    implemented by means of a `state` property which
                    changes values each time the switch is continued;
                    depending on the value of `state`, different things
                    happen.

                    -   `Loop`

                        An abstract continuation which is intended to
                        implement a loop. However, this is not
                        automatic; some continuation chain leading from
                        this continuation *must* lead back to this
                        continuation in order for actual repetition to
                        take place.

                        -   `WhileLoop`

                            A concrete `Loop` which, on odd visits
                            continues its `test` property. It is assumed
                            that some continuation down that chain
                            continues this `WhileLoop` object with a
                            boolean value in the accumulator. On these
                            even visits, it will behave like an `If`:
                            when the boolean is a `True`, `next` is
                            continued, otherwise `else`.

                        -   `ForLoop`

                            A concrete `Loop` which defines `value`,
                            `delta`, and `finish` properties, all
                            `Integer`s. On each visit, it checks if
                            `value` equals `finish`; if not, it adds
                            `delta` to `value` and continues `next`. But
                            if so, it simply continues `else`.

Implementations
---------------

There is not currently a reference implementation of Unlikely. Any
contradictions and/or grey areas in this document will therefore have
nowhere to turn to to be cleared up.

There is, however, a partial and non-normative implementation of
Unlikely, a static analyzer written in Python called Coldwater. It
parses Unlikely programs and identifies many type errors and other
statically-detectable invalid programs. It is meant to give some body to
the ideas present in Unlikely, without actually going so far as
implementing it in full.

The construction of Coldwater helped clear up some of the fuzzier
corners of the language. However, there are probably several areas that
remain fuzzy and render the language unsuitable for anything but the
most trivial programming. Extending Coldwater to be a full-fledged
Unlikely interpreter will probably help define the language. However
that project has been deferred as future work, and any clarifications
that come from it will be incorporated only in a future language
version.

Discussion
----------

This section contains some random thoughts and reflections on the
Unlikely programming language.

There is a rough analogy between Unlikely's requisite dependency
injection class parameters, and value parameters in languages without
global variables. There is no implicit referent when you say `Foo`;
`Foo` must name some parameter that has been passed into scope.

Because all the parts of the language are modelled as objects, the
language's execution model has some resemblance to an object-oriented
AST interpreter for itself. Except, of course, these objects are
continuations, so it is not like a recursive, depth-first walk of the
AST; it is much closer to the technique of threading the AST and
following that thread.

At one point I included the constraint that the set of dependant classes
specified by a class must be mutually disjoint; that is, no dependant
class in the set could be a subclass of some other dependant class in
the set. I am not entirely sure why I introduced that constraint, since
it could well be valuable to refine two classes by injection even when
one of those classes is a subclass of the other. I took it out.

Because properties cannot be redefined in subclasses, and because
parameters to methods are just syntactic sugar for properties, methods
cannot be overloaded. In particular `continue` must always work on a
`Passive` parameter, although of course it is mere convention that the
method works on the `accumulator` property anyway.

Unlikely is Turing-complete. (I will assert this because it seems
reasonable to me, but I do not have a proof, so I may be wrong.) The
Unlikely language is not minimal. In particular, the `Loop` class and
its subclasses `WhileLoop` and `ForLoop` could be removed, and the
resulting language would still be Turing-complete. In fact, `WhileLoop`
and `ForLoop` could probably be implemented in Unlikely and provided in
an extension class library.

The idea to conflate contintuations and objects was inspired by the
data-structure representation of continuations in Chapter 7 of
[Essentials of Programming Languages, 2nd
ed.](http://www.cs.indiana.edu/eopl/), which embodies a tiny measure of
inheritance. The idea that language constructs have commensurate
inheritance relationships (`WhileLoop` and `ForLoop` are subclasses of
`Loop`, etc.) was borrowed from Steve Yegge's article [Scheming is
Believing](http://steve.yegge.googlepages.com/scheming-is-believing).
The idea that all programs are subclasses of `Program`, which dovetails
so nicely with that, was borrowed from Brian Connors' "Sulawesi"
language design. The idea that every concrete value has its own class,
leading to abstract final classes with countably infinite subclasses,
was pure desperation.

For the purpose of defining computable functions, the Unlikely-Calculus
could be considered as a variant of Unlikely without `Print` or `Input`
classes. The `Stop` class would be there redefined to yield the value
passed to the accumulator as the result of evaluation, rather than as an
operating system exit code.

It's a safe bet that there is at least one person out there who will be
disappointed that this language is named Unlikely yet contains no
probabilistic design features.

Happy object-method-continuing!  
Chris Pressey  
March 15, 2009  
Bellevue, WA
