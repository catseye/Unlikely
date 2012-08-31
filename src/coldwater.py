#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c)2010-2012 Chris Pressey, Cat's Eye Technologies.
# All rights reserved.  Released under a BSD-style license (see LICENSE).

"""
The Coldwater static analyzer for the Unlikely programming language.
"""

import sys
from optparse import OptionParser

from unlikely.scanner import Scanner
from unlikely.parser import ClassBaseParser
from unlikely.stdlib import stdlib


def load(filename, options):
    f = open(filename, "r")
    scanner = Scanner(f.read())
    f.close()
    parser = ClassBaseParser(scanner, stdlib)
    parser.parse()
    if options.dump_ast:
        print "---AST---"
        print str(stdlib)


def main(argv):
    usage = "[python] coldwater.py {options} {source.unlikely}"
    optparser = OptionParser(usage + "\n" + __doc__)
    optparser.add_option("-a", "--dump-ast",
                         action="store_true", dest="dump_ast", default=False,
                         help="dump AST after source is parsed")
    (options, args) = optparser.parse_args(argv[1:])
    for filename in args:
        load(filename, options)


if __name__ == "__main__":
    main(sys.argv)
