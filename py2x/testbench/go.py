#!/usr/bin/env python

import sys

sys.path[0:0] = '..', 'simplejson'

import tests
import simplejson
from simplejson.decoder import JSONDecodeError
from rson.ejson import EJsonParser
from rson.unquoted import StrictUnquotedToken

class MyDecodeError(JSONDecodeError):
    """Subclass of ValueError with the following additional properties:

    msg: The unformatted error message
    doc: The JSON document being parsed
    pos: The start index of doc where parsing failed
    end: The end index of doc where parsing failed (may be None)
    lineno: The line corresponding to pos
    colno: The column corresponding to pos
    endlineno: The line corresponding to end (may be None)
    endcolno: The column corresponding to end (may be None)

    """

    def __init__(self, msg, token):
        if token[1] == '@':
            text = 'at end of string'
        else:
            text = token[2]
        linenum = token[5]
        offset = colno = -token[0]
        if linenum != 1:
            colno -= token[-1].tokens.source.rfind('\n', offset)
        loc = 'line %s, column %s, text %s' % (linenum, colno, repr(text[:20]))
        ValueError.__init__(self, '%s: %s' % (msg, loc))
        self.msg = msg
        self.doc = None
        self.pos = offset
        self.end = None
        self.lineno, self.colno = linenum, colno
        self.endlineno, self.endcolno = None, None
        #if end is not None:
        #    self.endlineno, self.endcolno = linecol(doc, pos)
        #else:
        #    self.endlineno, self.endcolno = None, None



def loads(s, **kw):

    class MyUnquoted(StrictUnquotedToken):
        makefloat = kw.pop('parse_float', None)
        if makefloat is None:
            del makefloat
        makeint = kw.pop('parse_int', None)
        if makeint is None:
            del makeint

    class MyParser(EJsonParser):
        UnquotedToken = MyUnquoted

        def error(self, msg, token):
            raise MyDecodeError(msg, token)

    return MyParser.factory()(s)

simplejson.loads = loads

tests.main()
