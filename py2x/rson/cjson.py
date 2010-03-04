'''
"compatible" JSON syntax -- designed to be able to test
tokenizer/parser pieces with simplejson testsuite.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt
'''

from rson.ejson import EJsonParser, ParseError
from rson.unquoted import CompatibleUnquotedToken
from rson.doublequoted import QuotedToken

class MyQuotedToken(QuotedToken):
    cachestrings = True

def _dispatch():

    classcache = {}

    cached = classcache.get

    def newclass(key, kw):
        
        class MyUnquoted(CompatibleUnquotedToken):
            makefloat = kw.pop('parse_float', None) or CompatibleUnquotedToken.makefloat
            makeint = kw.pop('parse_int', None) or CompatibleUnquotedToken.makeint
    
        class MyParser(EJsonParser):
            UnquotedToken = MyUnquoted
            QuotedToken = MyQuotedToken
            object_hooks = kw.pop('object_hook', None), kw.pop('object_pairs_hook', None)
            allow_trailing_commas = False
    
        value = MyParser.factory()
        classcache[key] = value
        return value

    default_loads = newclass((), {})

    def loads(s, **kw):
        if not kw:
            return default_loads(s)
        key = kw and tuple(sorted(kw.iteritems()))
        return (cached(key) or newclass(key, kw))(s)

    return loads

loads = _dispatch()
