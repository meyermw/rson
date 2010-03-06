'''
"compatible" JSON syntax -- designed to be able to test
tokenizer/parser pieces with simplejson testsuite.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt
'''

from rson.ejson import EJsonParser
from rson.unquoted import CompatibleUnquotedToken
from rson.doublequoted import QuotedToken

def _dispatch():

    classcache = {}

    cached = classcache.get

    def newclass(key, kw):

        class MyParser(EJsonParser, CompatibleUnquotedToken, QuotedToken):
            cachestrings = True
            allow_trailing_commas = False
            parse_float = kw.pop('parse_float', None) or CompatibleUnquotedToken.parse_float
            parse_int = kw.pop('parse_int', None) or CompatibleUnquotedToken.parse_int
            object_hooks = kw.pop('object_hook', None), kw.pop('object_pairs_hook', None)

        value = MyParser.parser_factory()
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
