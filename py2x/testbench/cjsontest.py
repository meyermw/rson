#!/usr/bin/env python

import sys
import re
import cProfile

sys.path[0:0] = '..', 'simplejson'

import simplejson
import simplejson.tests

from rson import RsonParser, UnquotedToken, QuotedToken, Dispatcher, BaseObjects, Tokenizer, RSONDecodeError

# For some reason, the only test that simplejson does on actual file location
# uses a different location than we do...

oldloc = Tokenizer.sourceloc
def sourceloc(token):
    offset, lineno, colno = oldloc(token)
    return offset-1, lineno, colno-1
Tokenizer.sourceloc = staticmethod(sourceloc)

class CJsonSystem(RsonParser, UnquotedToken, QuotedToken, Dispatcher, BaseObjects):
    ''' Compatible JSON-only token syntax,
        tries to work same as simplejson
    '''
    Tokenizer = Tokenizer
    cachestrings = True
    allow_trailing_commas = False

    parse_int = lambda s: int(s, 0)

    @staticmethod
    def parse_unquoted_str(token):
        token[-1].error('Invalid literal', token)


    unquoted_pattern = r'''
    (?:
        true | false | null       |     # Special JSON names
        Infinity | NaN            |
        (?P<num>
            -?                          # Optional minus sign
            (?:0|[1-9]\d*)              # Zero or digits with non-zero lead
            (?P<float>
               (?:\.\d+)?               # Optional frac part
               (?:[eE][-+]?\d+)?        # Optional exponent
            )
        )
    )  \Z                               # Match end of string
    '''

    special_strings = UnquotedToken.special_strings.copy()
    for x in 'Infinity NaN'.split():
        special_strings[x] = float(x)

    quoted_splitter = re.compile(r'(\\u[0-9a-fA-F]{4}|\\.|"|[\x1f])').split
    object_pairs_expects_tuple = True

simplejson.loads = CJsonSystem.dispatcher_factory()
simplejson.JSONDecodeError = RSONDecodeError

simplejson.tests.main()

#cProfile.run('foo()')
