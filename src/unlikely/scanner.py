# -*- coding: utf-8 -*-

"""
Lexical scanner for the Unlikely programming language.
$Id: scanner.py 318 2010-01-07 01:49:38Z cpressey $
"""

class Scanner(object):
    """
    A lexical scanner.
    """

    def __init__(self, input):
        """
        Create a new Scanner object that will consume the given
        UTF-8 encoded input string.
        """
        self._input = unicode(input, 'utf-8')
        self._token = None
        self.scan()

    def scan(self):
        """
        Consume a token from the input.
        """
        self._token = ""
        while self._input[0].isspace():
            self._input = self._input[1:]
            if len(self._input) == 0:
                return
        if self._input[0].isalpha():
            while self._input[0].isalnum():
                self._token += self._input[0]
                self._input = self._input[1:]
            self.toktype = "ident"
        elif self._input[0].isdigit():
            while self._input[0].isdigit():
                self._token += self._input[0]
                self._input = self._input[1:]
            self.toktype = "int"
            self.tokval = int(self._token)
        elif self._input[:1] == "\"":
            st = ""
            self._input = self._input[1:]
            while self._input[:1] != "\"":
                st += self._input[:1]
                self._input = self._input[1:]
            self._input = self._input[1:]
            self.toktype = "string"
            self.tokval = st
            self._token = "\"" + st + "\""
        elif self._input[:2] == '(*':
            while self._input[:2] != '*)':
                self._input = self._input[1:]
            self._input = self._input[2:]
            return self.scan()
        else:
            self._token = self._input[0]
            self._input = self._input[1:]
            self.toktype = "op"
    
    def get_token(self):
        return self._token
    
    token = property(get_token)

    def expect(self, str):
        """
        Expect a certain token to be in the input, and complain
        if it is not.
        """
        if self._token == str:
            self.scan()
        else:
            self.error("expected " + str + ", found " + self._token)

    def grab(self):
        """
        Return the current token as a string, and advance.
        """
        t = self._token
        self.scan()
        return t

    def error(self, str):
        """
        Log the given scan error.
        """
        print "error: " + str
        self.scan()
