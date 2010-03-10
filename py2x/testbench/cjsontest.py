#!/usr/bin/env python

import sys
import cProfile

sys.path[0:0] = '..', 'simplejson'

import simplejson
import simplejson.tests

from rson import RsonParser, UnquotedToken, QuotedToken, Dispatcher, MergeDict, Tokenizer, RSONDecodeError

class CJsonSystem(RsonParser, UnquotedToken, QuotedToken, Dispatcher, MergeDict):
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


simplejson.loads = CJsonSystem.dispatcher_factory()
simplejson.JSONDecodeError = RSONDecodeError

simplejson.tests.main()

#cProfile.run('foo()')
