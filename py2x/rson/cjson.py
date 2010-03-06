'''
"compatible" JSON syntax -- designed to be able to test
tokenizer/parser pieces with simplejson testsuite.

Copyright (c) 2010, Patrick Maupin.  All rights reserved.

See http://code.google.com/p/rson/source/browse/#svn/trunk/license.txt
'''

from rson.ejson import EJsonParser
from rson.unquoted import UnquotedToken
from rson.doublequoted import QuotedToken
from rson.dispatcher import Dispatcher


class CJsonSystem(EJsonParser, UnquotedToken, QuotedToken, Dispatcher):
    ''' Compatible JSON-only token syntax,
        tries to work same as simplejson
    '''
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


loads = CJsonSystem.dispatcher_factory()
